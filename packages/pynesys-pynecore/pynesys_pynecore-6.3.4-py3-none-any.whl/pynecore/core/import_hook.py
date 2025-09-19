from typing import cast
import os
import sys
import importlib.util
import importlib.machinery
import re
from pathlib import Path


class PyneLoader(importlib.machinery.SourceFileLoader):
    """Loader that handles AST transformation"""

    # noinspection PyMethodOverriding
    def source_to_code(self, data: bytes | str, path: str, *, _optimize: int = -1):
        """Transform source to code if needed"""
        path: Path = Path(path)

        # Create marker file for pynecore site-packages to indicate we processed this file
        if (os.path.sep + 'site-packages' + os.path.sep in str(path).lower()
                and os.path.sep + 'pynecore' + os.path.sep in str(path).lower()):
            pyc_path = Path(importlib.util.cache_from_source(str(path)))
            cache_dir = pyc_path.parent
            marker_path = pyc_path.parent / f'{pyc_path.name}.pyne'
            try:
                cache_dir.mkdir(exist_ok=True)
                # Write the .py file's mtime to the marker
                py_mtime = str(path.stat().st_mtime)
                marker_path.write_text(py_mtime)
            except (OSError, PermissionError):
                pass  # Ignore if we can't create marker

        # Fast check for @pyne decorator before parsing AST
        # data is bytes, need to convert to string for regex
        data_str = data.decode('utf-8') if isinstance(data, bytes) else data
        if not re.search(r'@pyne\b', data_str):
            # No @pyne decorator, let Python handle it normally
            return compile(data, path, 'exec', optimize=_optimize)

        import ast

        # Parse AST only if @pyne is present
        tree = ast.parse(data_str)

        # Store file path in AST for transformers
        tree._module_file_path = str(path.resolve())  # type: ignore

        # Only transform if it has @pyne decorator
        if (tree.body and isinstance(tree.body[0], ast.Expr) and
                isinstance(cast(ast.Expr, tree.body[0]).value, ast.Constant) and
                isinstance(cast(ast.Constant, cast(ast.Expr, tree.body[0]).value).value, str) and
                '@pyne' in cast(ast.Constant, cast(ast.Expr, tree.body[0]).value).value):  # type: ignore

            # Remove test cases from the output, because they can coorupt the output
            transformed = tree
            transformed.body = [node for node in transformed.body
                                if not (isinstance(node, ast.FunctionDef)
                                        and node.name.startswith('__test_') and node.name.endswith('__'))]

            # Transform AST - lazy import transformers only when needed
            from pynecore.transformers.import_lifter import ImportLifterTransformer
            from pynecore.transformers.import_normalizer import ImportNormalizerTransformer
            from pynecore.transformers.persistent_series import PersistentSeriesTransformer
            from pynecore.transformers.lib_series import LibrarySeriesTransformer
            from pynecore.transformers.closure_arguments_transformer import ClosureArgumentsTransformer
            from pynecore.transformers.function_isolation import FunctionIsolationTransformer
            from pynecore.transformers.module_property import ModulePropertyTransformer
            from pynecore.transformers.series import SeriesTransformer
            from pynecore.transformers.unused_series_detector import UnusedSeriesDetectorTransformer
            from pynecore.transformers.persistent import PersistentTransformer
            from pynecore.transformers.input_transformer import InputTransformer
            from pynecore.transformers.safe_convert_transformer import SafeConvertTransformer
            from pynecore.transformers.safe_division_transformer import SafeDivisionTransformer

            transformed = ImportLifterTransformer().visit(transformed)
            transformed = ImportNormalizerTransformer().visit(transformed)
            transformed = PersistentSeriesTransformer().visit(transformed)
            transformed = LibrarySeriesTransformer().visit(transformed)
            transformed = ModulePropertyTransformer().visit(transformed)
            transformed = ClosureArgumentsTransformer().visit(transformed)
            transformed = FunctionIsolationTransformer().visit(transformed)
            transformed = UnusedSeriesDetectorTransformer().optimize(transformed)
            transformed = SeriesTransformer().visit(transformed)
            transformed = PersistentTransformer().visit(transformed)
            transformed = InputTransformer().visit(transformed)
            transformed = SafeConvertTransformer().visit(transformed)
            transformed = SafeDivisionTransformer().visit(transformed)

            ast.fix_missing_locations(transformed)

            # Debug output if requested
            if os.environ.get('PYNE_AST_DEBUG'):
                print("-" * 100)
                print(f"Transformed {path}:")
                try:
                    from rich.syntax import Syntax  # type: ignore
                    from rich import print as rprint  # type: ignore
                    rprint(Syntax(ast.unparse(transformed), "python", word_wrap=True, line_numbers=False))
                except ImportError:
                    print(ast.unparse(transformed))
                print("-" * 100)
            elif os.environ.get('PYNE_AST_DEBUG_RAW'):
                print(ast.unparse(transformed))

            if os.environ.get('PYNE_AST_SAVE'):
                Path("/tmp/pyne").mkdir(parents=True, exist_ok=True)

                with open(f"/tmp/pyne/{path.stem}.py", "w") as f:
                    f.write(ast.unparse(transformed))

            tree = transformed

        # Let Python handle bytecode caching
        return compile(tree, path, 'exec', optimize=_optimize)


class PyneImportHook:
    """Import hook that uses PyneLoader"""

    # noinspection PyMethodMayBeStatic,PyUnusedLocal
    def find_spec(self, fullname: str, path, target=None):
        """Find and create module spec"""
        if path is None:
            path = sys.path

        if "." in fullname:
            *_, name = fullname.split(".")
        else:
            name = fullname

        for entry in path:
            if entry == "":
                entry = "."

            # Check both module.py and module/__init__.py
            candidates = [
                Path(entry) / f"{name}.py",
                Path(entry) / name / "__init__.py"
            ]

            for py_path in candidates:
                if py_path.exists():
                    # Check if pynecore site-packages bytecode needs recompilation
                    if (os.path.sep + 'site-packages' + os.path.sep in str(py_path).lower() and
                            os.path.sep + 'pynecore' + os.path.sep in str(py_path).lower()):
                        pyc_path = Path(importlib.util.cache_from_source(str(py_path)))
                        marker_path = pyc_path.parent / f'{pyc_path.name}.pyne'

                        need_recompile = False

                        if pyc_path.exists():
                            if not marker_path.exists():
                                # No marker - definitely need recompile
                                need_recompile = True
                            else:
                                # Check if marker has the correct py mtime
                                try:
                                    stored_mtime = marker_path.read_text().strip()
                                    current_mtime = str(py_path.stat().st_mtime)
                                    if stored_mtime != current_mtime:
                                        # .py file changed - need recompile
                                        need_recompile = True
                                except (OSError, ValueError):
                                    # Can't read marker or invalid content - need recompile
                                    need_recompile = True

                        if need_recompile:
                            # Force recompile by removing the old bytecode
                            try:
                                pyc_path.unlink()
                                if marker_path.exists():
                                    marker_path.unlink()  # Also remove old marker
                            except (OSError, PermissionError):
                                pass  # Ignore if we can't delete

                    return importlib.util.spec_from_file_location(
                        fullname,
                        py_path,
                        loader=PyneLoader(fullname, str(py_path))
                    )
        return None


# Install the import hook
sys.meta_path.insert(0, PyneImportHook())

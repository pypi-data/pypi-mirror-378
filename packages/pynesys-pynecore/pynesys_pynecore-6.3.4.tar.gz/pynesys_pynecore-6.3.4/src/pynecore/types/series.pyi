from __future__ import annotations
import os
from typing import TypeVar, Generic, Any, Union, Protocol, TypeAlias, Self
from .na import NA

T = TypeVar('T')

# Pycharm is less strict and use more heuristics to infer types, so we can use a simpler and better implementation
if os.environ.get("TYPECHECKER") == "pycharm":
    T_co = TypeVar('T_co', covariant=True)

    class _SeriesIndexer(Protocol[T_co]):
        def __getitem__(self, index: int) -> T_co: ...

    class _SeriesType(Generic[T_co], _SeriesIndexer[T_co]):
        """
        This is the runtime, do nothing implementation of the Series type. The actual Series behavior is
        implented in AST Transformers and the SeriesImpl class.
        """

    # The type definition that allows both uses
    Series: TypeAlias = Union[T_co, _SeriesType[T_co]]
    # The persistent version of the Series type
    PersistentSeries: TypeAlias = Union[T_co, _SeriesType[T_co]]


# Pyright is more strict and requires a more complex implementation, this does not work in PyCharm,
#  because for this to work you need to switch off some type checking options
# For pyright you need to disable some checks, unfortunately, becuase of static analysis
else:
    class Series(Generic[T]):
        """
        Internal helper class for Series type checking.
        Implements indexing protocol while allowing value assignment.
        """

        # The value to store
        value: list[T | NA[T]]

        def __init__(self, value: T | Self) -> None:
            """
            Initialize the Series with a value.
            :param value: The initial value of the Series.
            """
            ...

        def __getitem__(self, index: int) -> T:
            ...

        # Forward all common operations to the inner value
        def __add__(self, other: Any) -> T: ...

        def __sub__(self, other: Any) -> T: ...

        def __mul__(self, other: Any) -> T: ...

        def __truediv__(self, other: Any) -> T: ...

        def __floordiv__(self, other: Any) -> T: ...

        def __mod__(self, other: Any) -> T: ...

        def __pow__(self, other: Any) -> T: ...

        # Reverse operators
        def __radd__(self, other: Any) -> T: ...

        def __rsub__(self, other: Any) -> T: ...

        def __rmul__(self, other: Any) -> T: ...

        def __rtruediv__(self, other: Any) -> T: ...

        def __rfloordiv__(self, other: Any) -> T: ...

        def __rmod__(self, other: Any) -> T: ...

        def __rpow__(self, other: Any) -> T: ...

        # Comparison operators
        def __lt__(self, other: Any) -> bool: ...

        def __le__(self, other: Any) -> bool: ...

        def __eq__(self, other: Any) -> bool: ...

        def __ne__(self, other: Any) -> bool: ...

        def __gt__(self, other: Any) -> bool: ...

        def __ge__(self, other: Any) -> bool: ...

        # Other common operators
        def __abs__(self) -> T: ...

        def __neg__(self) -> T: ...

        def __pos__(self) -> T: ...

        def __round__(self, ndigits: int = 0) -> T: ...

        def __int__(self) -> int: ...

        def __float__(self) -> float: ...

        def __str__(self) -> str: ...

        def __bool__(self) -> bool: ...

        def __len__(self) -> int: ...

        def __repr__(self) -> str: ...

    PersistentSeries = Series

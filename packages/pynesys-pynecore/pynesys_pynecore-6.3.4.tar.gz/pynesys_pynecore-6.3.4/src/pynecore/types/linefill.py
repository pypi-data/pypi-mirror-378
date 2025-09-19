from dataclasses import dataclass

from ..lib import color as _color
from .line import Line


@dataclass(slots=True)
class LineFill:
    line1: Line  # First line object
    line2: Line  # Second line object
    color: _color.Color  # Fill color

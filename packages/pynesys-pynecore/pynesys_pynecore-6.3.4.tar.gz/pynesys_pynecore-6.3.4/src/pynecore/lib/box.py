from copy import copy as _copy

from ..core.overload import overload
from ..core.module_property import module_property

from ..types.box import Box
from ..types.na import NA
from ..types.chart import ChartPoint
from ..lib import (color as _color, extend as _extend, xloc as _xloc, size as _size, line as _line,
                   text as _text, font as _font)

_registry: list[Box] = []


@overload
def new(top_left: ChartPoint, bottom_right: ChartPoint, border_color: _color.Color = _color.blue,
        border_width: int = 1, border_style: _line.LineEnum = _line.style_solid,
        extend: _extend.Extend = _extend.none, xloc: _xloc.XLoc = _xloc.bar_index,
        bgcolor: _color.Color = _color.blue, text: str = "", text_size: _size.Size = _size.auto,
        text_color: _color.Color = _color.black, text_halign: _text.AlignEnum = _text.align_center,
        text_valign: _text.AlignEnum = _text.align_center, text_wrap: _text.WrapEnum = _text.wrap_none,
        text_font_family: _font.FontFamilyEnum = _font.family_default, force_overlay: bool = False,
        text_formatting: _text.FormatEnum = _text.format_none):
    """
    Creates a new box object.

    :param top_left: chart.point object that specifies the top-left corner location
    :param bottom_right: chart.point object that specifies the bottom-right corner location
    :param border_color: Color of the four borders
    :param border_width: Width of the four borders, in pixels
    :param border_style: Style of the four borders
    :param extend: When extend.none is used, the horizontal borders start at the left border and end at the right border
    :param xloc: Determines whether the arguments to 'left' and 'right' are a bar index or a time value
    :param bgcolor: Background color of the box
    :param text: The text to be displayed inside the box
    :param text_size: Size of the box's text
    :param text_color: The color of the text
    :param text_halign: The horizontal alignment of the box's text
    :param text_valign: The vertical alignment of the box's text
    :param text_wrap: Whether to wrap text. Wrapped text starts a new line
    :param text_font_family: The font family of the text
    :param force_overlay: If true, the drawing will display on the main chart pane
    :param text_formatting: The formatting of the displayed text
    :return: A box object
    """
    # Extract coordinates from ChartPoint objects based on xloc
    if xloc == _xloc.bar_time:
        left, top = top_left.time, top_left.price
        right, bottom = bottom_right.time, bottom_right.price
    else:  # xloc.bar_index (default)
        left, top = top_left.index, top_left.price
        right, bottom = bottom_right.index, bottom_right.price

    box = Box(
        left=left,
        top=top,
        right=right,
        bottom=bottom,
        border_color=border_color,
        border_width=border_width,
        border_style=border_style,
        extend=extend,
        xloc=xloc,
        bgcolor=bgcolor,
        text=text,
        text_size=text_size,
        text_color=text_color,
        text_halign=text_halign,
        text_valign=text_valign,
        text_wrap=text_wrap,
        text_font_family=text_font_family,
        text_formatting=text_formatting,
        force_overlay=force_overlay,
    )
    _registry.append(box)
    return box


@overload
def new(left: int, top: float, right: int, bottom: float,
        border_color: _color.Color = _color.blue, border_width: int = 1,
        border_style: _line.LineEnum = _line.style_solid, extend: _extend.Extend = _extend.none,
        xloc: _xloc.XLoc = _xloc.bar_index, bgcolor: _color.Color = _color.blue, text: str = "",
        text_size: _size.Size = _size.auto, text_color: _color.Color = _color.black,
        text_halign: _text.AlignEnum = _text.align_center, text_valign: _text.AlignEnum = _text.align_center,
        text_wrap: _text.WrapEnum = _text.wrap_none, text_font_family: _font.FontFamilyEnum = _font.family_default,
        force_overlay: bool = False, text_formatting: _text.FormatEnum = _text.format_none):
    """
    Creates a new box object.

    :param left: Bar index (if xloc = xloc.bar_index) or UNIX time (if xloc = xloc.bar_time) of the
                 left border of the box
    :param top: Price of the top border of the box
    :param right: Bar index (if xloc = xloc.bar_index) or UNIX time (if xloc = xloc.bar_time) of the
                  right border of the box
    :param bottom: Price of the bottom border of the box
    :param border_color: Color of the four borders. Optional. The default is color.blue
    :param border_width: Width of the four borders, in pixels. Optional. The default is 1 pixel
    :param border_style: Style of the four borders. Possible values: line.style_solid,
                         line.style_dotted, line.style_dashed
    :param extend: When extend.none is used, the horizontal borders start at the left border and end at the right border
    :param xloc: Determines whether the arguments to 'left' and 'right' are a bar index or a time value
    :param bgcolor: Background color of the box. Optional. The default is color.blue
    :param text: The text to be displayed inside the box. Optional. The default is empty string
    :param text_size: Size of the box's text
    :param text_color: The color of the text. Optional. The default is color.black
    :param text_halign: The horizontal alignment of the box's text
    :param text_valign: The vertical alignment of the box's text
    :param text_wrap: Whether to wrap text. Wrapped text starts a new line
    :param text_font_family: The font family of the text
    :param force_overlay: If true, the drawing will display on the main chart pane
    :param text_formatting: The formatting of the displayed text
    :return: A box object
    """
    box = Box(
        left=left,
        top=top,
        right=right,
        bottom=bottom,
        border_color=border_color,
        border_width=border_width,
        border_style=border_style,
        extend=extend,
        xloc=xloc,
        bgcolor=bgcolor,
        text=text,
        text_size=text_size,
        text_color=text_color,
        text_halign=text_halign,
        text_valign=text_valign,
        text_wrap=text_wrap,
        text_font_family=text_font_family,
        text_formatting=text_formatting,
        force_overlay=force_overlay,
    )
    _registry.append(box)
    return box


# noinspection PyShadowingBuiltins
@module_property
def all() -> list[Box]:
    """Returns all box objects"""
    return _registry


# noinspection PyShadowingBuiltins
def delete(id):
    if isinstance(id, NA):
        return
    _registry.remove(id)


# noinspection PyShadowingBuiltins
def copy(id):
    if isinstance(id, NA):
        return NA(Box)
    return _copy(id)


# Setter methods

# noinspection PyShadowingBuiltins
def set_bgcolor(id: Box, color: _color.Color) -> None:
    """Sets the background color of the box."""
    if isinstance(id, NA):
        return
    id.bgcolor = color


# noinspection PyShadowingBuiltins
def set_border_color(id: Box, color: _color.Color) -> None:
    """Sets the border color of the box."""
    if isinstance(id, NA):
        return
    id.border_color = color


# noinspection PyShadowingBuiltins
def set_border_style(id: Box, style: _line.LineEnum) -> None:
    """Sets the border style of the box."""
    if isinstance(id, NA):
        return
    id.border_style = style


# noinspection PyShadowingBuiltins
def set_border_width(id: Box, width: int) -> None:
    """Sets the border width of the box."""
    if isinstance(id, NA):
        return
    id.border_width = width


# noinspection PyShadowingBuiltins
def set_bottom(id: Box, bottom: float) -> None:
    """Sets the bottom coordinate of the box."""
    if isinstance(id, NA):
        return
    id.bottom = bottom


# noinspection PyShadowingBuiltins
def set_bottom_right_point(id: Box, point: ChartPoint) -> None:
    """Sets the bottom-right corner location of the box to point."""
    if isinstance(id, NA):
        return
    if id.xloc == _xloc.bar_time:
        id.right = point.time
    else:
        id.right = point.index
    id.bottom = point.price


# noinspection PyShadowingBuiltins
def set_extend(id: Box, extend: _extend.Extend) -> None:
    """Sets extending type of the border of this box object."""
    if isinstance(id, NA):
        return
    id.extend = extend


# noinspection PyShadowingBuiltins
def set_left(id: Box, left: int) -> None:
    """Sets the left coordinate of the box."""
    if isinstance(id, NA):
        return
    id.left = left


# noinspection PyShadowingBuiltins
def set_lefttop(id: Box, left: int, top: float) -> None:
    """Sets the left and top coordinates of the box."""
    if isinstance(id, NA):
        return
    id.left = left
    id.top = top


# noinspection PyShadowingBuiltins
def set_right(id: Box, right: int) -> None:
    """Sets the right coordinate of the box."""
    if isinstance(id, NA):
        return
    id.right = right


# noinspection PyShadowingBuiltins
def set_rightbottom(id: Box, right: int, bottom: float) -> None:
    """Sets the right and bottom coordinates of the box."""
    if isinstance(id, NA):
        return
    id.right = right
    id.bottom = bottom


# noinspection PyShadowingBuiltins


def set_text(id: Box, text: str) -> None:
    """Sets the text in the box."""
    if isinstance(id, NA):
        return
    id.text = text


# noinspection PyShadowingBuiltins
def set_text_color(id: Box, text_color: _color.Color) -> None:
    """Sets the color of the text inside the box."""
    if isinstance(id, NA):
        return
    id.text_color = text_color


# noinspection PyShadowingBuiltins
def set_text_font_family(id: Box, text_font_family: _font.FontFamilyEnum) -> None:
    """Sets the font family of the text inside the box."""
    if isinstance(id, NA):
        return
    id.text_font_family = text_font_family


# noinspection PyShadowingBuiltins
def set_text_formatting(id: Box, text_formatting: _text.FormatEnum) -> None:
    """Sets the formatting attributes the drawing applies to displayed text."""
    if isinstance(id, NA):
        return
    id.text_formatting = text_formatting


# noinspection PyShadowingBuiltins
def set_text_halign(id: Box, text_halign: _text.AlignEnum) -> None:
    """Sets the horizontal alignment of the box's text."""
    if isinstance(id, NA):
        return
    id.text_halign = text_halign


# noinspection PyShadowingBuiltins
def set_text_size(id: Box, text_size: _size.Size) -> None:
    """Sets the size of the box's text."""
    if isinstance(id, NA):
        return
    id.text_size = text_size


# noinspection PyShadowingBuiltins
def set_text_valign(id: Box, text_valign: _text.AlignEnum) -> None:
    """Sets the vertical alignment of the box's text."""
    if isinstance(id, NA):
        return
    id.text_valign = text_valign


# noinspection PyShadowingBuiltins
def set_text_wrap(id: Box, text_wrap: _text.WrapEnum) -> None:
    """Sets the mode of wrapping of the text inside the box."""
    if isinstance(id, NA):
        return
    id.text_wrap = text_wrap


# noinspection PyShadowingBuiltins
def set_top(id: Box, top: float) -> None:
    """Sets the top coordinate of the box."""
    if isinstance(id, NA):
        return
    id.top = top


# noinspection PyShadowingBuiltins
def set_top_left_point(id: Box, point: ChartPoint) -> None:
    """Sets the top-left corner location of the box to point."""
    if isinstance(id, NA):
        return
    if id.xloc == _xloc.bar_time:
        id.left = point.time
    else:
        id.left = point.index
    id.top = point.price


# noinspection PyShadowingBuiltins
def set_xloc(id: Box, left: int, right: int, xloc: _xloc.XLoc) -> None:
    """Sets the left and right borders of a box and updates its xloc property."""
    if isinstance(id, NA):
        return
    id.left = left
    id.right = right
    id.xloc = xloc


# Getter methods

# noinspection PyShadowingBuiltins
def get_bottom(id: Box) -> float | NA:
    """Returns the price value of the bottom border of the box."""
    if isinstance(id, NA):
        return NA(float)
    return id.bottom


# noinspection PyShadowingBuiltins
def get_left(id: Box) -> int | NA:
    """
    Returns the bar index or the UNIX time (depending on the last value used for 'xloc') of the
    left border of the box.
    """
    if isinstance(id, NA):
        return NA(int)
    return id.left


# noinspection PyShadowingBuiltins
def get_right(id: Box) -> int | NA:
    """
    Returns the bar index or the UNIX time (depending on the last value used for 'xloc') of the
    right border of the box.
    """
    if isinstance(id, NA):
        return NA(int)
    return id.right


# noinspection PyShadowingBuiltins
def get_top(id: Box) -> float | NA:
    """Returns the price value of the top border of the box."""
    if isinstance(id, NA):
        return NA(float)
    return id.top

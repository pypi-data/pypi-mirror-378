from enum import StrEnum, auto
from typing import Required, TypedDict


class Position(StrEnum):
    RIGHT = auto()
    LEFT = auto()
    TOP = auto()
    BOTTOM = auto()


class ColorPalette(StrEnum):
    QUAL = auto()
    QUANT = auto()
    DIV = auto()


class AxisScale(StrEnum):
    LINEAR = auto()
    LOG = auto()


class LineKind(StrEnum):
    SOLID = auto()
    DOTTED = auto()
    DASHED = auto()
    DOT_DASHED = auto()


class LineMode(StrEnum):
    NORMAL = auto()
    BEFORE = auto()
    CENTER = auto()
    AFTER = auto()


LEGEND_DIMS = {"color", "symbol", "style", "stack"}
CBAR_DIMS = {"color"}


## Facets
class FacetCommonArgs(TypedDict, total=False):
    sharex: bool
    sharey: bool


class FacetDimArgs(FacetCommonArgs, total=False):
    dim: Required[str]
    wrap: int | None


class FacetRowColArgs(FacetCommonArgs, total=False):
    row: Required[str]
    col: Required[str]


## Axes
class NumericAxisOptions(TypedDict, total=False):
    name: Required[str]
    scale: AxisScale


class CategoricalAxisOptions(TypedDict, total=False):
    name: Required[str]
    buffer: int


## Geom - Point
class PointColorOptions(TypedDict, total=False):
    name: Required[str]
    scale: AxisScale
    # TODO: allow for cmin,cmax only for QUANT, DIV
    palette: ColorPalette
    reverse: bool
    midpoint: int


class PointSizeOptions(TypedDict, total=False):
    name: Required[str]
    range: tuple[float, float]
    scale: AxisScale


class PointSymbolOptions(TypedDict, total=False):
    name: Required[str]
    sequence: list[str]


## Geom - Line
class LineColorOptions(TypedDict, total=False):
    name: Required[str]
    scale: AxisScale
    # TODO: allow for cmin,cmax only for QUANT, DIV
    palette: ColorPalette
    reverse: bool
    midpoint: int


class LineStyleOptions(TypedDict, total=False):
    name: Required[str]
    kind: LineKind


## Geom - Bar
class BarStackOptions(TypedDict, total=False):
    name: Required[str]


class BarGroupOptions(TypedDict, total=False):
    name: Required[str]


class BarColorOptions(TypedDict, total=False):
    name: Required[str]

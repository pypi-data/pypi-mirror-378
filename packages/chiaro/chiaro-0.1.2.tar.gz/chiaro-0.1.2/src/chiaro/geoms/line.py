from typing import Self

import narwhals as nw
from bokeh.plotting import ColumnDataSource, figure

from chiaro.core.base import ChartBase
from chiaro.core.types import (
    AxisScale,
    ColorPalette,
    LineColorOptions,
    LineKind,
    LineMode,
    LineStyleOptions,
    NumericAxisOptions,
)


class ChartLine(ChartBase):
    def __init__(
        self,
        df: nw.DataFrame,
        source: ColumnDataSource,
        markers: bool = True,
        mode: LineMode = LineMode.NORMAL,
    ) -> None:
        """Init"""
        super().__init__(df, source)
        self.markers = markers
        self.mode = mode

    def dimensions(
        self,
        x: str | NumericAxisOptions,
        y: str | NumericAxisOptions,
        color: str | LineColorOptions | None = None,
        style: str | LineStyleOptions | None = None,
    ) -> Self:
        self._dims_used["x"] = {"name": x, "scale": AxisScale.LINEAR} if isinstance(x, str) else x
        self._dims_used["y"] = {"name": y, "scale": AxisScale.LINEAR} if isinstance(y, str) else y
        if color is not None:
            if not isinstance(color, str):
                self._dims_used["color"] = color
            else:
                if self._df[color].dtype.is_numeric():
                    chosen_palette = ColorPalette.QUANT
                else:
                    chosen_palette = ColorPalette.QUAL
                self._dims_used["color"] = {
                    "name": color,
                    "palette": chosen_palette,
                    "reverve": False,
                }
        if style is not None:
            self._dims_used["style"] = (
                {"name": style, "kind": LineKind.SOLID} if isinstance(style, str) else style
            )
        return self

    def build(self) -> Self:
        # TODO: chart building logic
        p = figure()
        self.bokeh_obj = p
        return self

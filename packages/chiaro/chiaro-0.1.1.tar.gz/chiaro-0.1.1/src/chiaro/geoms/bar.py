from typing import Self

import narwhals as nw
from bokeh.plotting import ColumnDataSource, figure

from chiaro.core.base import ChartBase
from chiaro.core.types import (
    AxisScale,
    BarColorOptions,
    BarGroupOptions,
    BarStackOptions,
    CategoricalAxisOptions,
    NumericAxisOptions,
)


class ChartBar(ChartBase):
    def __init__(
        self,
        df: nw.DataFrame,
        source: ColumnDataSource,
        width: float = 0.5,
    ) -> None:
        """Init"""
        super().__init__(df, source)
        self.width = width

    def dimensions(
        self,
        x: str | CategoricalAxisOptions,
        y: str | NumericAxisOptions,
        stack: str | BarStackOptions | None = None,
        group: str | BarGroupOptions | None = None,
        color: str | BarColorOptions | None = None,
    ) -> Self:
        self._dims_used["x"] = {"name": x} if isinstance(x, str) else x
        self._dims_used["y"] = {"name": y, "scale": AxisScale.LINEAR} if isinstance(y, str) else y
        # TODO: ensure combinations of stack/group/color are valid
        if stack is not None:
            self._dims_used["stack"] = {"name": stack} if isinstance(stack, str) else stack
        if group is not None:
            self._dims_used["group"] = {"name": group} if isinstance(group, str) else group
        if color is not None:
            self._dims_used["color"] = {"name": color} if isinstance(color, str) else color
        return self

    def build(self) -> Self:
        # TODO: chart building logic
        p = figure()
        self.bokeh_obj = p
        return self

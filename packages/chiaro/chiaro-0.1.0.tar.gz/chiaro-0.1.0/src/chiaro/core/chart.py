from typing import Literal

import narwhals as nw
from bokeh.plotting import ColumnDataSource
from narwhals.typing import IntoDataFrame

from chiaro.core.types import LineMode
from chiaro.geoms import (
    ChartBar,
    ChartLine,
    ChartPoint,
)


class Chart:
    def __init__(self, data: IntoDataFrame) -> None:
        """Init"""
        self._df = nw.from_native(data)
        self._source = ColumnDataSource(
            self._df.to_dict(as_series=False),  # pyright: ignore[reportArgumentType]
        )

    def geom_point(
        self,
        size: int = 5,
        opacity: float = 1.0,
    ) -> ChartPoint:
        return ChartPoint(
            df=self._df,
            source=self._source,
            size=size,
            opacity=opacity,
        )

    def geom_line(
        self,
        markers: bool = True,
        mode: LineMode = LineMode.NORMAL,
    ) -> ChartLine:
        return ChartLine(
            df=self._df,
            source=self._source,
            markers=markers,
            mode=mode,
        )

    def geom_bar(
        self,
        width: float = 0.5,
    ) -> ChartBar:
        return ChartBar(
            df=self._df,
            source=self._source,
            width=width,
        )

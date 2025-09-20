from typing import Literal

from narwhals.typing import IntoDataFrame

from chiaro.core.chart import Chart
from chiaro.core.types import LineMode
from chiaro.geoms import (
    ChartBar,
    ChartLine,
    ChartPoint,
)


def scatter(
    data: IntoDataFrame,
    x: str,
    y: str,
    color: str | None = None,
    size: str | None = None,
    symbol: str | None = None,
    opacity: float = 1,
) -> ChartPoint:
    """Quick scatter plot"""
    chart = (
        Chart(data)
        .geom_point(
            opacity=opacity,
        )
        .dimensions(
            x=x,
            y=y,
            color=color,
            size=size,
            symbol=symbol,
        )
        .build()
    )
    return chart


def line(
    data: IntoDataFrame,
    x: str,
    y: str,
    color: str | None = None,
    style: str | None = None,
    markers: bool = True,
    mode: LineMode = LineMode.NORMAL,
) -> ChartLine:
    """Quick line plot"""
    chart = (
        Chart(data)
        .geom_line(
            markers=markers,
            mode=mode,
        )
        .dimensions(
            x=x,
            y=y,
            color=color,
            style=style,
        )
        .build()
    )
    return chart


def bar(
    data: IntoDataFrame,
    x: str,
    y: str,
    stack: str | None = None,
    group: str | None = None,
    color: str | None = None,
    width: float = 0.5,
) -> ChartBar:
    """Quick bar chart"""
    chart = (
        Chart(data)
        .geom_bar(
            width=width,
        )
        .dimensions(
            x=x,
            y=y,
            stack=stack,
            group=group,
            color=color,
        )
        .build()
    )
    return chart

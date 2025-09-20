import warnings
from typing import Any, Self, Unpack, overload

import narwhals as nw
from bokeh.embed import file_html
from bokeh.plotting import ColumnDataSource, figure, show
from bokeh.resources import CDN

from chiaro.core.io import Runtime, detect_runtime_environment
from chiaro.core.types import (
    CBAR_DIMS,
    LEGEND_DIMS,
    FacetCommonArgs,
    Position,
)


class ChartBase:
    def __init__(
        self,
        df: nw.DataFrame,
        source: ColumnDataSource,
    ) -> None:
        """Init"""
        self._df = df
        self._source = source
        # TODO: use proper strict union type here
        self._dims_used: dict[str, Any] = {}
        self._labels: dict[str, str | None] = {}
        self.bokeh_obj: figure | None = None

    @overload
    def facets(
        self,
        *,
        facet_dim: str,
        wrap: int | None = None,
        **kwargs: Unpack[FacetCommonArgs],
    ) -> Self: ...

    @overload
    def facets(
        self,
        *,
        facet_row: str,
        facet_col: str,
        **kwargs: Unpack[FacetCommonArgs],
    ) -> Self: ...

    def facets(self, **kwargs: Any) -> Self:
        has_dim = "facet_dim" in kwargs
        has_row_col = "facet_row" in kwargs and "facet_col" in kwargs

        if not (has_dim ^ has_row_col):
            raise ValueError(
                "Provide either 'facet_dim' (with optional 'wrap') OR both 'facet_row' and 'facet_col'",
            )

        # TODO: store the additional opts
        if kwargs.get("facet_dim"):
            self._dims_used["facet_dim"] = kwargs["facet_dim"]

        if kwargs.get("facet_row") and kwargs.get("facet_col"):
            self._dims_used["facet_row"] = kwargs["facet_row"]
            self._dims_used["facet_col"] = kwargs["facet_col"]

        return self

    def labels(
        self,
        title: str | None = None,
        subtitle: str | None = None,
        caption: str | None = None,
        x: str | None = None,
        y: str | None = None,
        color: str | None = None,
        symbol: str | None = None,
        style: str | None = None,
        stack: str | None = None,
        group: str | None = None,
        facet_dim: str | None = None,
        facet_row: str | None = None,
        facet_col: str | None = None,
    ) -> Self:
        # Check that only used dims get labels
        dim_labels = {
            k: v
            for k, v in locals().items()
            if k not in ["self", "title", "subtitle", "caption"] and v is not None
        }
        invalid_dims = set(dim_labels.keys()) - self._dims_used.keys()

        # TODO: assert that `facet_dim/row/col` should have 1 format placeholder {}

        if invalid_dims:
            raise ValueError(f"Cannot set labels for unused dimensions: {', '.join(invalid_dims)}")

        self._labels["title"] = title
        self._labels["subtitle"] = subtitle
        self._labels["caption"] = caption
        self._labels["x"] = x or self._dims_used.get("x", {}).get("name")
        self._labels["y"] = y or self._dims_used.get("y", {}).get("name")
        self._labels["color"] = color or self._dims_used.get("color", {}).get("name")
        self._labels["symbol"] = symbol or self._dims_used.get("symbol", {}).get("name")
        self._labels["style"] = style or self._dims_used.get("style", {}).get("name")
        self._labels["stack"] = stack or self._dims_used.get("stack", {}).get("name")
        self._labels["group"] = group or self._dims_used.get("group", {}).get("name")
        # TODO: process facet labels with format strings properly, will need work in build methods
        self._labels["facet_dim"] = facet_dim
        self._labels["facet_row"] = facet_row
        self._labels["facet_col"] = facet_col

        return self

    def guides(
        self,
        legend: bool | None = None,
        legend_position: str = Position.RIGHT,
        cbar: bool | None = None,
        cbar_position: str = Position.RIGHT,
        grid_x: bool = True,
        grid_y: bool = True,
    ) -> Self:
        is_legend_needed = len(self._dims_used.keys() & LEGEND_DIMS) > 0
        if not is_legend_needed and legend:
            warnings.warn(
                "Cannot set 'legend` if atleast one of 'legend dimensions' are not set.\n"
                f"Possible 'legend dimensions': {', '.join(LEGEND_DIMS)}\n"
                "This argument will be ignored.",
                category=UserWarning,
                stacklevel=2,
            )
        if legend is None and is_legend_needed:
            # Implicit legend
            legend = True

        is_cbar_needed = len(self._dims_used.keys() & CBAR_DIMS) > 0
        if not is_cbar_needed and cbar_position is not None:
            warnings.warn(
                "Cannot set 'cbar_position` if atleast one of 'cbar dimensions' are not set.\n"
                f"Possible 'cbar dimensions': {', '.join(CBAR_DIMS)}\n"
                "This argument will be ignored.",
                category=UserWarning,
                stacklevel=2,
            )
        if cbar is None and is_cbar_needed:
            # Implicit cbar
            cbar = True

        return self

    def tools(self) -> Self:
        return self

    def layout(
        self,
        min_height: int = 400,
        auto_width: bool = True,
    ) -> Self:
        return self

    def _repr_html_(self):  # noqa: ANN202
        if self.bokeh_obj is None:
            raise ValueError(
                "Please call `build()` method on the chart before trying to render it.",
            )

        runtime = detect_runtime_environment()
        if runtime == Runtime.NOT_SUPPORTED:
            mod_name = __name__.split(".")[0]
            raise ImportError(
                f"Can only render plots {mod_name} from a Notebook environment.\n"
                f"If you want to run in headless mode, consider using some export functions from `{mod_name}.io`",
            )

        if runtime == Runtime.DATABRICKS:
            # NOTE: This function will always be in databricks runtime globals
            globals()["displayHTML"](file_html(self.bokeh_obj, CDN, "temp"))
        else:
            # NOTE: The builtin bokeh rendering should work here
            # TODO: Test this on Colab
            show(self.bokeh_obj)

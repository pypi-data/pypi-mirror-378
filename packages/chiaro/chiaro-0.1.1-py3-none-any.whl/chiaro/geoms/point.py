import warnings
from random import shuffle
from typing import Self

import bokeh.palettes
import narwhals as nw
from bokeh.models import ColorBar, LinearColorMapper, Title
from bokeh.plotting import ColumnDataSource, figure
from bokeh.transform import factor_cmap

from chiaro.core.base import ChartBase
from chiaro.core.types import (
    AxisScale,
    ColorPalette,
    NumericAxisOptions,
    PointColorOptions,
    PointSizeOptions,
    PointSymbolOptions,
)


class ChartPoint(ChartBase):
    def __init__(
        self,
        df: nw.DataFrame,
        source: ColumnDataSource,
        size: int = 5,
        opacity: float = 1.0,
    ) -> None:
        """Init"""
        super().__init__(df, source)
        self.size = size
        self.opacity = opacity

    def dimensions(
        self,
        x: str | NumericAxisOptions,
        y: str | NumericAxisOptions,
        color: str | PointColorOptions | None = None,
        size: str | PointSizeOptions | None = None,
        symbol: str | PointSymbolOptions | None = None,
    ) -> Self:
        self._dims_used["x"] = {"name": x, "scale": AxisScale.LINEAR} if isinstance(x, str) else x
        self._dims_used["y"] = {"name": y, "scale": AxisScale.LINEAR} if isinstance(y, str) else y

        if color is not None:
            if not isinstance(color, str):
                if color.get("palette") == ColorPalette.DIV and not color.get("midpoint"):
                    raise ValueError(
                        "Can not use diverging color palette without explicit 'midpoint' set.",
                    )
                if (
                    (passed_palette := color.get("palette")) is not None
                    and passed_palette
                    in [
                        ColorPalette.QUAL,
                        ColorPalette.QUANT,
                    ]
                    and color.get("midpoint")
                ):
                    raise ValueError(
                        f"Can not use midpoint with {passed_palette.value} color palette.",
                    )
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
        if size is not None:
            if not isinstance(size, str):
                col_minmax_range = (
                    self._df[size["name"]].min().item(),
                    self._df[size["name"]].max().item(),
                )
                if not size.get("range"):
                    size["range"] = col_minmax_range
                self._dims_used["size"] = size
            else:
                col_minmax_range = (
                    self._df[size].min().item(),
                    self._df[size].max().item(),
                )
                self._dims_used["size"] = {
                    "name": size,
                    "range": col_minmax_range,
                    "scale": AxisScale.LINEAR,
                }
        if symbol is not None:
            self._dims_used["symbol"] = (
                {
                    "name": symbol,
                    "sequence": [
                        "circle",
                        "diamond",
                        "square",
                        "triangle",
                        "hex",
                        "star",
                        "plus",
                    ],
                }
                if isinstance(symbol, str)
                else symbol
            )
        return self

    def build(self) -> Self:
        p = figure(
            # TODO: use auto_width from base here. also add min_width?
            sizing_mode="stretch_width",
            # TODO: use min_height from base here
            height=400,
            title=(
                Title(text=self._labels["title"], text_font_size="14pt")  # pyright: ignore[reportArgumentType]
                if self._labels.get("title")
                else None
            ),
            x_axis_label=self._labels.get("x"),
            y_axis_label=self._labels.get("y"),
        )
        if not self._dims_used.get("color"):
            if not self._dims_used.get("size"):
                r = p.scatter(
                    source=self._source,
                    x=self._dims_used["x"]["name"],
                    y=self._dims_used["y"]["name"],
                    size=self.size,
                )
            else:
                col = nw.col(self._dims_used["size"]["name"])
                range_min, range_max = self._dims_used["size"]["range"]
                min_max_scale_expr = (
                    (range_min + col - col.min())
                    / (col.max() - col.min())
                    * (range_max - range_min)
                )
                sub_source = ColumnDataSource(
                    self._df.with_columns(size_scaled=min_max_scale_expr),  # pyright: ignore[reportArgumentType]
                )
                r = p.scatter(
                    source=sub_source,
                    x=self._dims_used["x"]["name"],
                    y=self._dims_used["y"]["name"],
                    size="size_scaled",
                )
        else:
            color_cat_vals = sorted(self._df[self._dims_used["color"]["name"]].unique().to_list())
            if self._dims_used["color"]["palette"] != ColorPalette.QUAL:
                if self._dims_used["color"]["palette"] == ColorPalette.QUANT:
                    mapper = LinearColorMapper(
                        palette=bokeh.palettes.Plasma256,
                        low=self._df[self._dims_used["color"]["name"]].min().item(),  # pyright: ignore[reportArgumentType]
                        high=self._df[self._dims_used["color"]["name"]].max().item(),  # pyright: ignore[reportArgumentType]
                    )
                else:
                    mapper = LinearColorMapper(
                        palette=bokeh.palettes.diverging_palette(
                            bokeh.palettes.Oranges256,
                            bokeh.palettes.Purples256,
                            n=256,
                            midpoint=self._dims_used["color"]["midpoint"],
                        ),
                        low=self._df[self._dims_used["color"]["name"]].min().item(),  # pyright: ignore[reportArgumentType]
                        high=self._df[self._dims_used["color"]["name"]].max().item(),  # pyright: ignore[reportArgumentType]
                    )
                r = p.scatter(
                    source=self._source,
                    x=self._dims_used["x"]["name"],
                    y=self._dims_used["y"]["name"],
                    size=self.size,
                    color={"field": self._dims_used["color"]["name"], "transform": mapper},
                )
                color_bar = ColorBar(
                    color_mapper=mapper,
                    label_standoff=12,
                    location=(0, 0),
                    title=self._labels.get("color"),
                )
                p.add_layout(color_bar, "right")
            else:
                color_cat_col_nvals = int(self._df[self._dims_used["color"]["name"]].n_unique())
                if color_cat_col_nvals <= 2:
                    palette = bokeh.palettes.Set1[3][:color_cat_col_nvals]
                elif color_cat_col_nvals <= 9:
                    palette = bokeh.palettes.Set1[color_cat_col_nvals]
                elif color_cat_col_nvals <= 12:
                    palette = bokeh.palettes.Set3[color_cat_col_nvals]
                elif color_cat_col_nvals <= 20:
                    palette = bokeh.palettes.Category20[color_cat_col_nvals]
                else:
                    warnings.warn(
                        f"Found {color_cat_col_nvals:,} unique values for color dimension column '{self._dims_used['color']['name']}', so using a shuffled quantitative colormap.",
                        category=UserWarning,
                        stacklevel=2,
                    )
                    palette = list(bokeh.palettes.Viridis256)
                    shuffle(palette)
                    palette = palette[:color_cat_col_nvals]
                renderers = []
                for color_cat_val in color_cat_vals:
                    color_cat_val_source = ColumnDataSource(
                        self._df.filter(  # pyright: ignore[reportArgumentType]
                            nw.col(self._dims_used["color"]["name"]) == color_cat_val,
                        ).to_dict(as_series=False)
                    )
                    r = p.scatter(
                        x=self._dims_used["x"]["name"],
                        y=self._dims_used["y"]["name"],
                        source=color_cat_val_source,
                        size=self.size,
                        color=factor_cmap(
                            self._dims_used["color"]["name"],
                            palette=palette,
                            factors=color_cat_vals,
                        ),
                        legend_label=str(color_cat_val),
                        muted_alpha=0.1,
                    )
                    renderers.append(r)
                legend = p.legend[0]
                legend.title = self._labels.get("color")
                legend.click_policy = "mute"
                p.add_layout(legend, "right")

        if subtitle_lab := self._labels.get("subtitle"):
            subtitle = Title(
                text=subtitle_lab,
                align="left",
                text_font_size="12pt",
            )
            p.add_layout(subtitle, "above")
        if caption_lab := self._labels.get("caption"):
            caption = Title(
                text=caption_lab,
                align="left",
                text_font_size="9pt",
            )
            p.add_layout(caption, "below")

        self.bokeh_obj = p
        return self

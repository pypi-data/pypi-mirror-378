# Chiaro

[![CI](https://github.com/Rabeez/chiaro/actions/workflows/ci.yml/badge.svg)](https://github.com/Rabeez/chiaro/actions/workflows/ci.yml)

A Grammar of Graphics charting library for Python, built on top of Bokeh.

## Features

- **Grammar of Graphics**: Intuitive, layered approach to building visualizations
- **Bokeh Backend**: Leverage Bokeh's interactive capabilities
- **Multiple Data Backends**: Works with pandas, polars, and more via narwhals
- **Express API**: Quick plots with sensible defaults

## Quick Example

```python
import chiaro as cha

# Basic scatter plot
chart = (
    cha.Chart(data)
    .geom_point()
    .dims(x="height", y="weight", color="species")
    .labels(title="My Plot")
)

# Or use express API
import chiaro.express as cx

cx.scatter(data, x="height", y="weight", color="species")
```

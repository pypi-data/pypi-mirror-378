"""Bar plot example with Bokeh
===============================

This example shows how to create a bar plot using Bokeh and export as PNG.
"""

import pandas as pd

import chiaro.express as cx

df = pd.DataFrame({"x": [1, 2, 3], "y": [1, 4, 9]})
chart = cx.scatter(df, x="x", y="y", opacity=0.3)
chart

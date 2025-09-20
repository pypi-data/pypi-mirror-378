"""Chiaro - Fluent Grammar-of-Graphics in Python"""

from bokeh.io import output_notebook

from .core.chart import Chart
from .core.io import Runtime, detect_runtime_environment

try:
    from ._version import version as __version__
except Exception:  # noqa: BLE001
    __version__ = "0+unknown"
__all__ = [
    "Chart",
]


runtime = detect_runtime_environment()
if runtime != Runtime.NOT_SUPPORTED:
    mod_name = __name__.split(".")[0]
    try:
        output_notebook()
    except Exception as e:
        raise ImportError("Could not setup Bokeh Notebook rendering in current environment") from e
    else:
        print(
            f"{mod_name} is now setup to render plots in Notebook environment via Bokeh.\n"
            f"Detected notebook runtime: {runtime.value}",
        )

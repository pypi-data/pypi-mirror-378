import os
from enum import StrEnum, auto

from IPython.core.getipython import get_ipython


class Runtime(StrEnum):
    JUPYTER = auto()
    DATABRICKS = auto()
    COLAB = auto()
    NOT_SUPPORTED = auto()


def detect_runtime_environment() -> Runtime:
    """Detect the runtime where code is running."""
    try:
        shell = get_ipython().__class__.__name__
    except Exception as _:  # noqa: BLE001
        return Runtime.NOT_SUPPORTED

    if shell != "ZMQInteractiveShell":
        return Runtime.NOT_SUPPORTED

    if any(k in os.environ for k in ("COLAB_GPU", "GCE_METADATA_TIMEOUT", "COLAB_TPU_ADDR")):
        return Runtime.COLAB

    if "DATABRICKS_RUNTIME_VERSION" in os.environ:
        return Runtime.DATABRICKS

    return Runtime.JUPYTER

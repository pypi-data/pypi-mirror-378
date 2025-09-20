import pandas as pd

import chiaro as cha
import chiaro.express as cx


def test_dummy() -> None:
    assert True


def test_migration() -> None:
    df = pd.DataFrame({"x": [1, 2, 3], "y": [1, 4, 9]})
    _ = cha.Chart(df).geom_point().dimensions(x="x", y="y")


def test_express() -> None:
    df = pd.DataFrame({"x": [1, 2, 3], "y": [1, 4, 9]})
    _ = cx.scatter(df, x="x", y="y")

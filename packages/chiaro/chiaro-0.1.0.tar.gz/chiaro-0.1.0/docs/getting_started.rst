Getting Started
===============

This is a placeholder page for new users.

Features
----------
* Grammar of Graphics: Intuitive, layered approach to building visualizations
* Bokeh Backend: Leverage Bokeh's interactive capabilities
* Multiple Data Backends: Works with pandas, polars, and more via narwhals
* Express API: Quick plots with sensible defaults

Installation
------------

.. code-block:: bash

   pip install chiaro


Usage
-------

.. code-block:: python

    import chiaro as cha

    # Basic scatter plot
    chart = (
        cha.Chart(data)
        .geom_point()
        .dims(x="height", y="weight", color="species")
        .labels(title="My Plot")
        .build()
    )
    chart.show()


Or use express API

.. code-block:: python

    import chiaro.express as cx

    chart = cx.scatter(data, x="height", y="weight", color="species")

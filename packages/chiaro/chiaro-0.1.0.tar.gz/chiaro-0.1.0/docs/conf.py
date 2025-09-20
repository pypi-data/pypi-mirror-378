import sys
from pathlib import Path

sys.path.insert(0, str(Path("../src").resolve()))

project = "Chiaro"
author = "Rabeez Riaz"

extensions = [
    "sphinx.ext.autodoc",  # API docs from docstrings
    "sphinx.ext.napoleon",  # Google/NumPy style
    # "sphinx_gallery.gen_gallery",  # Gallery from scripts
    "nbsphinx",  # Optional: embed notebooks
    # "sphinx.ext.viewcode",  # optional, shows links to source code
    "sphinx.ext.autosummary",  # optional, generates summary tables
    # "bokeh.sphinxext.bokeh_plot",
    "sphinx_copybutton",
]

# # sphinx-gallery config
# sphinx_gallery_conf = {
#     "examples_dirs": "../example_scripts",  # path to your examples
#     "gallery_dirs": "gallery",  # where SG will generate rst pages
#     "image_scrapers": (
#         ("bokeh", bokeh_scraper),  # name + callable
#     ),
#     # optional: provide a screenshot command if you have headless chromium installed
#     # e.g. "chromium --headless --screenshot={out} --window-size=900,600 {in}"
#     "bokeh_screenshot_cmd": "chromium --headless --disable-gpu --screenshot={out} --window-size=900,600 {in}",
# }

templates_path = ["_templates"]
exclude_patterns = []

autosummary_generate = True
autosummary_imported_members = True

html_theme = "pydata_sphinx_theme"
html_static_path = ["_static"]
html_css_files = [
    "gallery.css",
    "custom.css",
]
html_theme_options = {
    "navbar_persistent": ["search-button", "theme-switcher"],
    "navbar_end": ["navbar-icon-links"],
    # Ensure all nav items stay visible
    "navbar_align": "left",
    # Force navbar items to not collapse
    "collapse_navigation": False,
    # Prevent navbar from hiding items
    "navbar_center": ["navbar-nav"],
}
html_context = {
    "default_mode": "dark",
    "github_repo": "github.com/rabeez/chiaro",
}

# Tell nbsphinx where to find notebooks outside docs/
nbsphinx_source_suffix = {
    ".ipynb": None,
}
# Allow referencing files outside docs/
exclude_patterns = [
    "_build",
    "gallery/*.ipynb",  # Stop processing gallery notebooks as tutorials
]
nbsphinx_execute = "never"
nbsphinx_timeout = 60

import runpy
from pathlib import Path

from bokeh.embed import file_html
from bokeh.io.export import export_png
from bokeh.resources import CDN

EXAMPLES = Path("example_scripts")
DOCS_GALLERY = Path("docs/gallery")
INDEX_RST = DOCS_GALLERY / "index.rst"
HTML_DIR = Path("docs/_static/gallery/html")
PNG_DIR = Path("docs/_static/gallery/thumbs")

DOCS_GALLERY.mkdir(parents=True, exist_ok=True)
HTML_DIR.mkdir(parents=True, exist_ok=True)
PNG_DIR.mkdir(parents=True, exist_ok=True)


def render_example(src_file: Path) -> tuple[Path, Path]:
    """Run example, export PNG, return (html_path, png_path)."""
    stem = src_file.stem
    png_out = PNG_DIR / f"{stem}.png"
    html_out = HTML_DIR / f"{stem}.html"

    # run the script and grab the chart
    ns = runpy.run_path(str(src_file))
    chart = ns.get("chart", None)
    if chart is None:
        raise RuntimeError(f"No `chart` found in {src_file}")

    fig = chart.bokeh_obj
    orig_mode = getattr(fig, "sizing_mode", None)
    fig.sizing_mode = None
    fig.width = 500
    fig.height = 500
    export_png(fig, filename=str(png_out))
    fig.sizing_mode = orig_mode

    # export standalone HTML with CDN resources
    html = file_html(chart.bokeh_obj, CDN, title=stem)
    html_out.write_text(html, encoding="utf-8")

    return html_out, png_out


def make_example_rst(src_file: Path, html_out: Path, png_out: Path) -> Path:
    stem = src_file.stem
    rst_file = DOCS_GALLERY / f"{stem}.rst"

    # read first non-empty docstring line for title
    title = stem
    with open(src_file, "r", encoding="utf-8") as f:
        lines = f.readlines()
    if lines and lines[0].startswith('"""'):
        for l in lines[1:]:
            if l.strip() and not l.strip().startswith("="):
                title = l.strip()
                break

    rst_content = f"""{title}
{"=" * len(title)}

Source Code
-----------

.. literalinclude:: /../example_scripts/{src_file.name}
   :language: python
   :caption: Example code

Interactive Plot
----------------

.. raw:: html

   <iframe src="../_static/gallery/html/{html_out.name}" width="100%" height=500 style="border:none; max-width:100%; display:block;"></iframe>
"""
    rst_file.write_text(rst_content, encoding="utf-8")
    return rst_file


def build_index(pages: list[tuple[Path, str]]) -> None:
    items = []
    for rst_file, title in pages:
        stem = rst_file.stem
        png_name = f"{stem}.png"
        # link to the generated .rst page
        items.append(
            f'<div class="gallery-item">\n'
            f'  <a href="{stem}.html">\n'
            f'    <img src="../_static/gallery/thumbs/{png_name}" alt="{title}" />\n'
            f'    <div class="caption">{title}</div>\n'
            f"  </a>\n"
            f"</div>\n"
        )

    # add blank line before raw HTML, indent contents properly
    raw_html = "".join(items)
    raw_html_indented = "   " + raw_html.replace("\n", "\n   ")
    grid_html = f"\n.. raw:: html\n\n{raw_html_indented}\n"

    # build index content with header and description
    index_content = (
        "Gallery of Examples\n"
        "===================\n\n"
        "This gallery shows usage examples for Chiaro.\n\n"
        "Each example contains:\n\n"
        "- The Python code\n"
        "- The resulting interactive plots\n"
        f"{grid_html}\n"
    )

    # append hidden toctree so Sphinx knows all pages
    toctree_entries = "\n   ".join([rst_file.stem for rst_file, _ in pages])
    index_content += f".. toctree::\n   :maxdepth: 1\n   :hidden:\n\n   {toctree_entries}\n"

    INDEX_RST.write_text(index_content, encoding="utf-8")


if __name__ == "__main__":
    pages = []
    for src_file in sorted(Path("example_scripts").glob("*.py")):
        html_out, png_out = render_example(src_file)
        rst_file = make_example_rst(src_file, html_out, png_out)

        # extract first non-empty line of docstring for title
        title = src_file.stem
        with open(src_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
            if lines and lines[0].startswith('"""'):
                for l in lines[1:]:
                    if l.strip() and not l.strip().startswith("="):
                        title = l.strip()
                        break
        pages.append((rst_file, title))

    # generate gallery index.rst using new pages structure
    build_index(pages)

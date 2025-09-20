from collections.abc import Sequence

import svg
from exonviz.draw import draw_exons
from exonviz.mutalyzer import build_exons
from mutalyzer.description import Description
from mutalyzer.viewer import view_variants

config = {
    "width": 768,
    "height": 20,
    "scale": 1.0,
    "noncoding": True,
    "gap": 0,
    "color": "#4C72B7",
    "exonnumber": True,
    "firstexon": 1,
    "lastexon": 9999,
    "variantcolors": ["#BA1C30", "#DB6917", "#EBCE2B", "#702C8C", "#C0BD7F"],
    "variantshape": "pin",
}


def draw(d: Description) -> str:
    view = view_variants(d.input_description)
    exons, dropped_variants = build_exons(
        transcript=d.input_description,
        mutalyzer=d.output()["selector_short"],
        view_variants=view,
        config=config,
    )

    fig = draw_exons(exons, config=config)

    # Make the figure scalable with CSS by resetting the width and height
    # and setting a viewBox
    width = fig.width
    height = fig.height
    fig.viewBox = svg.ViewBoxSpec(0, 0, width, height)

    fig.width = None
    fig.height = None

    return str(fig)

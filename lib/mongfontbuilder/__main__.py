"""
uv run python -m mongfontbuilder
"""

from argparse import ArgumentParser
from pathlib import Path

from ufoLib2 import Font

from . import data
from .data.types import LocaleID
from .otl import MongFeaComposer
from .spec import applySpecToFont

parser = ArgumentParser()
parser.add_argument(
    "input",
    type=Path,
    help="path to read source UFO font from",
)
parser.add_argument(
    "output",
    type=Path,
    help="path to write constructed UFO font to",
)
parser.add_argument(
    "--locales",
    metavar="LOCALE",
    choices=data.locales,
    nargs="+",
    required=True,
    help="targeted locales, one or more from: " + ", ".join(data.locales),
)

args = parser.parse_args()
input: Path = args.input
output: Path = args.output
locales: list[LocaleID] = args.locales

font = Font.open(input)

c = MongFeaComposer(
    cmap={j: i for i in font.keys() for j in font[i].unicodes},
    glyphs=[*font.keys()],
    locales=locales,
)
spec = c.compose()
applySpecToFont(spec, font)
font.features.text = c.asFeatureFile().asFea()

output.parent.mkdir(parents=True, exist_ok=True)
font.save(output, overwrite=True)

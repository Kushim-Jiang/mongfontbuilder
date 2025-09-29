"""
uv run python -m mongfontbuilder
"""

from argparse import ArgumentParser
from pathlib import Path

from ufoLib2 import Font

from . import constructFont, data
from .data.types import LocaleID

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
constructFont(font, locales)
output.parent.mkdir(parents=True, exist_ok=True)
font.save(output, overwrite=True)

"""
poetry run python -m mongfontbuilder
"""

from argparse import ArgumentParser
from pathlib import Path

from ufoLib2 import Font

from . import constructFont
from .data import locales

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
    choices=locales,
    nargs="+",
    required=True,
    help="targeted locales, one or more from: " + ", ".join(locales),
)

args = parser.parse_args()
font = Font.open(args.input)
constructFont(font, args.locales)
font.save(args.output, overwrite=True)

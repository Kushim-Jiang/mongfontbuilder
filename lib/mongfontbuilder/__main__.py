"""
uv run python -m mongfontbuilder input_ufo output [--locales ...]
"""

from argparse import ArgumentParser
from os import environ
from pathlib import Path

from ufo2ft import OTFCompiler
from ufo2ft.constants import CFFOptimization
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
    help="path to write constructed font to (.ufo or .otf)",
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

suffix = output.suffix.lower()
if suffix == ".ufo":
    font.save(output, overwrite=True)
elif suffix == ".otf":
    environ["FONTTOOLS_LOOKUP_DEBUGGING"] = "1"
    compiler = OTFCompiler(
        useProductionNames=False,
        optimizeCFF=CFFOptimization.NONE,
        featureWriters=[],
    )
    compiler.compile(font).save(output)
    print(f"Generated: {output}")
else:
    msg = f"unsupported output format: {suffix} (use .ufo or .otf)"
    raise ValueError(msg)

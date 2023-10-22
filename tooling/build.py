import argparse
import re
from dataclasses import dataclass
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Literal, cast

import yaml
from fontmake.font_project import FontProject
from fontTools.feaLib.parser import Parser
from fontTools.misc.transform import Identity
from fontTools.ttLib import TTFont
from fontTools.ttLib.tables._n_a_m_e import table__n_a_m_e
from glyphsLib.builder import UFOBuilder
from glyphsLib.parser import load
from ufoLib2.objects import Component, Font, Glyph, Info

parser = argparse.ArgumentParser()
parser.add_argument("font", type=Path)
parser.add_argument(
    "--glyph-name-mapping",
    type=Path,
    help="A maping from source glyph names to UTN glyph names, in YAML format.",
)
parser.add_argument("--family-name")
parser.add_argument("--output-dir", type=Path)
parser.add_argument("--debug", action="store_true")

tooling_dir = Path(__file__).parent
repo_dir = tooling_dir / ".."
data_dir = repo_dir / "data"
glyphs_dir = data_dir / "glyphs"
otl_dir = tooling_dir / "otl"


LEFT_SPACING = 40
RIGHT_SPACING = 100


def main():
    args = parser.parse_args()
    font_path: Path = args.font
    glyph_name_mapping_path: Path | None = args.glyph_name_mapping
    family_name: str | None = args.family_name
    output_dir: Path | None = args.output_dir

    assert font_path.suffix in {".ufo", ".glyphs", ".glyphspackage"}
    if font_path.suffix == ".ufo":
        ufo = Font.open(font_path)
    else:
        builder = UFOBuilder(load(font_path))
        (ufo,) = builder.masters

    glyph_name_mapping: dict[str, str] = {}
    if glyph_name_mapping_path:
        with glyph_name_mapping_path.open() as f:
            data: dict[str, str | None | Literal[False]] = yaml.safe_load(f)
            for source_name, utn_name in data.items():
                glyph_name_mapping[source_name] = utn_name or source_name

    construct_glyph_set(ufo, glyph_name_mapping)

    build(
        ufo=ufo,
        family_name=family_name,
        output_dir=output_dir,
        debug=args.debug,
    )


@dataclass
class UTNGlyphName(str):
    uni_name: str | None
    written_units: list[str]
    joining_position: str | None  # isol | init | medi | fina

    def __init__(self, name: str):
        parts = name.split(".")
        if len(parts) == 1:
            self.uni_name, self.written_units, self.joining_position = parts[0], [], None
            return

        if len(parts) == 3:
            self.uni_name = parts[0]
            written_units_part, self.joining_position = parts[1:]
        else:  # 2
            self.uni_name = None
            written_units_part, self.joining_position = parts
        self.written_units = re.findall("[A-Z][a-z0-9]*", written_units_part)

    def code_point(self) -> int | None:
        if self.uni_name:
            return int(self.uni_name.removeprefix("uni"), 16)
        else:
            return None

    def code_point_agnostic(self) -> str:
        return ".".join(i for i in ["".join(self.written_units), self.joining_position] if i)


def get_units(glyph_name: str | None):
    if not glyph_name or "._" in glyph_name:
        return None
    else:
        return UTNGlyphName(glyph_name).code_point_agnostic()


def quote_glyph(old_glyphs: list[Glyph | int], new_glyph: Glyph):
    for glyph in old_glyphs:
        if isinstance(glyph, int):
            new_glyph.width += glyph
        else:
            component = Component(glyph.name or "", Identity.translate(int(new_glyph.width), 0))
            new_glyph.components.append(component)
            new_glyph.width += glyph.width


def construct_glyph_set(ufo: Font, glyph_name_mapping: dict[str, str]):
    # FIXME: currently any glyphs not specified in the expected glyph set are skipped, eg, digits and punctuation marks.

    # prefix existing glyph names with "__", to skip them and isolate them from constructed glyph names
    for glyph_name in [*ufo.keys()]:
        for component in ufo[glyph_name].components:
            component.baseGlyph = "__" + component.baseGlyph
        ufo.renameGlyph(glyph_name, "__" + glyph_name)
        ufo["__" + glyph_name].unicode = None
    ufo.lib["public.skipExportGlyphs"] = sorted(ufo.keys())

    glyph_name_mapping = {"__" + k: v for k, v in glyph_name_mapping.items()}

    glyph = ufo.newGlyph(".notdef")
    quote_glyph([ufo["__.notdef"]], glyph)
    glyph_order = [".notdef"]

    # Multiple source names may map to the same UTN name:
    utn_name_to_source_names = dict[str, list[str]]()
    for source_name, utn_name in glyph_name_mapping.items():
        utn_name_to_source_names.setdefault(utn_name, []).append(source_name)

    # Multiple UTN names may share the same code-point-agnostic name:
    cp_agnostic_name_to_source_names = dict[str, list[str]]()
    for utn_name, source_names in utn_name_to_source_names.items():
        if "._" in utn_name:
            continue
        cp_agnostic_name = UTNGlyphName(utn_name).code_point_agnostic()
        cp_agnostic_name_to_source_names.setdefault(cp_agnostic_name, []).extend(source_names)

    # Load data files:

    with (data_dir / "representative-glyphs.yaml").open() as f:
        nominal_mapping: dict[str, str] = yaml.safe_load(f)

    expected_glyph_names = dict[str, dict[str, None]]()
    for path in glyphs_dir.glob("*.yaml"):
        with path.open() as f:
            expected_glyph_names[path.stem] = yaml.safe_load(f)

    # variant glyphs
    for glyph_name in expected_glyph_names["variants"]:
        glyph = ufo.newGlyph(glyph_name)
        if source_names := utn_name_to_source_names.get(glyph_name, []):
            ref_glyph = ufo[source_names[0]]
            quote_glyph([ref_glyph], glyph)
        elif source_names := cp_agnostic_name_to_source_names.get(get_units(glyph_name) or "", []):
            ref_glyph = ufo[source_names[0]]
            quote_glyph([ref_glyph], glyph)
        elif "_" not in glyph_name:
            print(f"we don't have {glyph_name}")
        glyph.unicode = None
        glyph_order.append(glyph_name)

    for glyph_name in expected_glyph_names["variants"]:  # depends on the loop above
        if "._" in glyph_name:
            if glyph_name.endswith("isol"):
                quote_glyph([LEFT_SPACING, ufo[glyph_name[:-6]], RIGHT_SPACING], ufo[glyph_name])
            elif glyph_name.endswith("init"):
                quote_glyph([LEFT_SPACING, ufo[glyph_name[:-6]]], ufo[glyph_name])
            elif glyph_name.endswith("fina"):
                quote_glyph([ufo[glyph_name[:-6]], RIGHT_SPACING], ufo[glyph_name])

    # nominal glyphs
    for glyph_name, written_units in nominal_mapping.items():
        glyph = ufo.newGlyph(glyph_name)
        cmap_glyphs = [
            glyph for glyph in ufo if glyph.unicode == UTNGlyphName(glyph_name).code_point()
        ]
        if len(cmap_glyphs):
            ref_glyph = cmap_glyphs[0]
            quote_glyph([ref_glyph], glyph)
        else:
            quote_glyph(
                [LEFT_SPACING, ufo[glyph_name + "." + written_units], RIGHT_SPACING],
                glyph,
            )
        glyph.unicode = UTNGlyphName(glyph_name).code_point()
        glyph_order.append(glyph_name)

    # ligatures and format controls
    for glyph_name in expected_glyph_names["ligatures"] | expected_glyph_names["format-controls"]:
        glyph = ufo.newGlyph(glyph_name)
        if source_names := utn_name_to_source_names.get(glyph_name, []):
            ref_glyph = ufo[source_names[0]]
            quote_glyph([ref_glyph], glyph)
        else:
            print(f"we don't have {glyph_name}")
        glyph_order.append(glyph_name)

    # empty glyphs
    for glyph_name in expected_glyph_names["empty"]:
        glyph = ufo.newGlyph(glyph_name)
        glyph_order.append(glyph_name)

    ufo.glyphOrder = glyph_order


def build(
    ufo: Font,
    otl_code_path=otl_dir / "main.fea",
    family_name: str | None = None,
    output_dir: Path | None = None,
    keep_info=False,
    debug=False,
) -> Path:
    """Common logic for building fonts."""

    output_dir = output_dir or Path.cwd()
    if debug:
        import os

        os.environ["FONTTOOLS_LOOKUP_DEBUGGING"] = "1"

    if not keep_info:
        ufo.info = Info()  # drop all existing info data
    ufo.info.familyName = family_name

    parser = Parser(featurefile=otl_code_path, glyphNames=ufo.keys())
    feature_file = parser.parse()
    ufo.features.text = feature_file.asFea()

    with TemporaryDirectory() as temp_dir:
        FontProject().run_from_ufos(
            ufos=[ufo],
            output={"otf"},
            remove_overlaps=False,
            output_dir=temp_dir,
        )
        temp_paths = [*Path(temp_dir).iterdir()]
        ttfont = TTFont(temp_paths[0])  # only dealing with a single output
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / make_font_filename(ttfont)
        ttfont.save(output_path)
        return output_path


def make_font_filename(font: TTFont) -> str:
    table = cast(table__n_a_m_e, font["name"])
    postscript_name = cast(str, table.getDebugName(6))
    if "fvar" in font:  # variable font only shows family name in filename
        stem, _, _ = postscript_name.partition("-")
    else:
        stem = postscript_name

    suffix = ".otf" if {"CFF ", "CFF2"}.intersection(font.keys()) else ".ttf"

    return stem + suffix


if __name__ == "__main__":
    main()

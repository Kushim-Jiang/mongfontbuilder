import argparse
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import cast

import yaml
from fontmake.font_project import FontProject
from fontTools.feaLib.parser import Parser
from fontTools.misc.transform import Identity
from fontTools.ttLib import TTFont
from fontTools.ttLib.tables._n_a_m_e import table__n_a_m_e
from glyphsLib.builder import UFOBuilder
from glyphsLib.parser import load
from ufoLib2.objects import Component, Font, Glyph, Info

tooling_dir = Path(__file__).parent
repo_dir = tooling_dir / ".."

data_dir = repo_dir / "data"
otl_dir = tooling_dir / "otl"
glyph_dir = data_dir / "glyphs.yaml"
nominal_dir = data_dir / "nominal.yaml"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("font", type=Path)
    parser.add_argument("--glyph-name-mapping", type=Path)
    parser.add_argument("--family-name")
    parser.add_argument("--output-dir", type=Path)

    args = parser.parse_args()
    font_path: Path = args.font
    glyph_name_mapping_path: Path | None = args.glyph_name_mapping

    assert font_path.suffix in {".ufo", ".glyphs", ".glyphspackage"}
    if font_path.suffix == ".ufo":
        ufo = Font.open(font_path)
    else:
        builder = UFOBuilder(load(font_path))
        (ufo,) = builder.masters

    glyph_mapping: dict[str, str | None] = {}
    if glyph_name_mapping_path:
        with glyph_name_mapping_path.open() as f:
            glyph_mapping = yaml.safe_load(f)

    construct_glyph_set(ufo, glyph_mapping)

    # ufo.save(Path.cwd() / "res.ufo")
    build(
        ufo=ufo,
        family_name=args.family_name,
        output_dir=args.output_dir,
    )


def get_units(glyph_name: str | None):
    if glyph_name is None:
        return None
    if "_" in glyph_name:
        return None
    glyph_names = glyph_name.split(".")
    if len(glyph_names) == 2:
        return ".".join(glyph_names)
    if len(glyph_names) == 3:
        return ".".join(glyph_names[1:])
    return None


def get_cp(glyph_name: str):
    return int(glyph_name[3:], 16)


def quote_glyph(old_glyphs: list[Glyph | int], new_glyph: Glyph):
    for glyph in old_glyphs:
        if isinstance(glyph, int):
            new_glyph.width += glyph
        else:
            component = Component(glyph.name or "", Identity.translate(int(new_glyph.width), 0))
            new_glyph.components.append(component)
            new_glyph.width += glyph.width


def construct_glyph_set(ufo: Font, glyph_mapping: dict[str, str | None]):
    # add __
    for glyph_name in [*ufo.keys()]:
        for component in ufo[glyph_name].components:
            component.baseGlyph = "__" + component.baseGlyph
        ufo.renameGlyph(glyph_name, "__" + glyph_name)
        ufo["__" + glyph_name].unicode = None
    glyph_mapping = {"__" + k: v for k, v in glyph_mapping.items()}
    ufo.lib["public.skipExportGlyphs"] = [glyph.name for glyph in ufo]

    glyph = ufo.newGlyph(".notdef")
    quote_glyph([ufo["__.notdef"]], glyph)
    ufo.glyphOrder = [".notdef"]

    with glyph_dir.open() as f:
        expected_glyph_names: dict[str, dict[str, None]] = yaml.safe_load(f)

    exact_mapping = {
        expected_name: [
            glyph_name
            for glyph_name in glyph_mapping
            if glyph_mapping.get(glyph_name) == expected_name
        ]
        for expected_name in {*glyph_mapping.values()}
    }
    unit_mapping = {
        expected_name: [
            glyph_name
            for glyph_name in glyph_mapping
            if get_units(glyph_mapping.get(glyph_name)) == expected_name
        ]
        for expected_name in {*[get_units(glyph_name) for glyph_name in glyph_mapping]} - {None}
    }

    # parse presentation glyphs
    for glyph_name in expected_glyph_names.get("presentation", {}):
        glyph = ufo.newGlyph(glyph_name)
        exact_glyphs = exact_mapping.get(glyph_name, [])
        unit_glyphs = unit_mapping.get(glyph_name, [])
        if len(exact_glyphs):
            ref_glyph = ufo[exact_glyphs[0]]
            quote_glyph([ref_glyph], glyph)
        elif len(unit_glyphs):
            ref_glyph = ufo[unit_glyphs[0]]
            quote_glyph([ref_glyph], glyph)
        glyph.unicode = None
        ufo.glyphOrder += [glyph_name]

    LEFT_SPACING = 40
    RIGHT_SPACING = 100
    for glyph_name in expected_glyph_names.get("presentation", {}):
        if "_" in glyph_name:
            if glyph_name.endswith("isol"):
                quote_glyph([LEFT_SPACING, ufo[glyph_name[:-6]], RIGHT_SPACING], ufo[glyph_name])
            elif glyph_name.endswith("init"):
                quote_glyph([LEFT_SPACING, ufo[glyph_name[:-6]]], ufo[glyph_name])
            elif glyph_name.endswith("fina"):
                quote_glyph([ufo[glyph_name[:-6]], RIGHT_SPACING], ufo[glyph_name])

    # parse nominal glyphs
    with nominal_dir.open() as f:
        nominal_mapping = yaml.safe_load(f)
    for glyph_name in expected_glyph_names.get("nominal", {}):
        glyph = ufo.newGlyph(glyph_name)
        cmap_glyphs = [glyph for glyph in ufo if glyph.unicode == get_cp(glyph_name)]
        if len(cmap_glyphs):
            ref_glyph = cmap_glyphs[0]
            quote_glyph([ref_glyph], glyph)
        else:
            quote_glyph([LEFT_SPACING, ufo[nominal_mapping[glyph_name]], RIGHT_SPACING], glyph)
        glyph.unicode = get_cp(glyph_name)
        ufo.glyphOrder += [glyph_name]

    # parse ligature and control glyphs
    ligature_glyphs: dict[str, None] = expected_glyph_names.get("ligature", {})
    control_glyphs: dict[str, None] = expected_glyph_names.get("control", {})

    for glyph_name in [*ligature_glyphs, *control_glyphs]:
        glyph = ufo.newGlyph(glyph_name)
        exact_glyphs = exact_mapping.get(glyph_name, [])
        if len(exact_glyphs):
            ref_glyph = ufo[exact_glyphs[0]]
            quote_glyph([ref_glyph], glyph)
        ufo.glyphOrder += [glyph_name]

    # parse empty glyphs
    for glyph_name in expected_glyph_names.get("empty", {}):
        glyph = ufo.newGlyph(glyph_name)
        ufo.glyphOrder += [glyph_name]


def build(
    ufo: Font,
    otl_code_path=otl_dir / "main.fea",
    family_name: str | None = None,
    output_dir: Path | None = None,
    keep_info=False,
) -> Path:
    """Common logic for building fonts."""

    output_dir = output_dir or Path.cwd()

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

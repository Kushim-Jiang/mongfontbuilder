import argparse
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import cast

import yaml
from fontmake.font_project import FontProject
from fontTools.feaLib.parser import Parser
from fontTools.ttLib import TTFont
from fontTools.ttLib.tables._n_a_m_e import table__n_a_m_e
from glyphsLib.builder import UFOBuilder
from glyphsLib.parser import load
from ufoLib2.objects import Font, Glyph, Info
from ufoLib2.pointPens.glyphPointPen import GlyphPointPen

tooling_dir = Path(__file__).parent
repo_dir = tooling_dir / ".."

data_dir = repo_dir / "data"
otl_dir = tooling_dir / "otl"
glyph_dir = data_dir / "glyphs.yaml"


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
        design_ufo = Font.open(font_path)
    else:
        builder = UFOBuilder(load(font_path))
        (design_ufo,) = builder.masters

    glyph_mapping: dict[str, str | None] = {}
    if glyph_name_mapping_path:
        with glyph_name_mapping_path.open() as f:
            glyph_mapping = yaml.safe_load(f)

    ufo = construct_glyph_set(design_ufo, glyph_mapping)

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


def copy_glyph(old_glyph: Glyph, new_glyph: Glyph):
    new_pen = GlyphPointPen(new_glyph)
    for component in old_glyph.components:
        component.drawPoints(new_pen)
    old_glyph.clearComponents()
    new_glyph.copyDataFromGlyph(old_glyph)


def construct_glyph_set(design_ufo: Font, glyph_mapping: dict[str, str | None]) -> Font:
    ufo = Font(info=design_ufo.info)
    glyph = ufo.newGlyph(".notdef")
    glyph.copyDataFromGlyph(design_ufo[".notdef"])
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
    presentation_glyphs: dict[str, None] = expected_glyph_names.get("presentation") or {}
    for glyph_name in presentation_glyphs:
        glyph = ufo.newGlyph(glyph_name)
        exact_glyphs = exact_mapping.get(glyph_name) or []
        unit_glyphs = unit_mapping.get(glyph_name) or []
        if len(exact_glyphs):
            old_glyph = design_ufo[exact_glyphs[0]]
            copy_glyph(old_glyph, glyph)
        elif len(unit_glyphs):
            old_glyph = design_ufo[unit_glyphs[0]]
            copy_glyph(old_glyph, glyph)
        glyph.unicode = None
        ufo.glyphOrder += [glyph_name]

    # parse nominal glyphs
    nominal_glyphs: dict[str, None] = expected_glyph_names.get("nominal") or {}
    for glyph_name in nominal_glyphs:
        glyph = ufo.newGlyph(glyph_name)
        cmap_glyphs = [glyph for glyph in design_ufo if glyph.unicode == get_cp(glyph_name)]
        if len(cmap_glyphs):
            old_glyph = cmap_glyphs[0]
            copy_glyph(old_glyph, glyph)
        glyph.unicode = get_cp(glyph_name)
        ufo.glyphOrder += [glyph_name]

    # parse ligature and control glyphs
    ligature_glyphs: dict[str, None] = expected_glyph_names.get("ligature") or {}
    control_glyphs: dict[str, None] = expected_glyph_names.get("control") or {}

    for glyph_name in [*ligature_glyphs, *control_glyphs]:
        glyph = ufo.newGlyph(glyph_name)
        exact_glyphs = exact_mapping.get(glyph_name) or []
        if len(exact_glyphs):
            old_glyph = design_ufo[exact_glyphs[0]]
            copy_glyph(old_glyph, glyph)
        ufo.glyphOrder += [glyph_name]

    # parse empty glyphs
    empty_glyphs: dict[str, None] = expected_glyph_names.get("empty") or {}
    for glyph_name in empty_glyphs:
        glyph = ufo.newGlyph(glyph_name)
        ufo.glyphOrder += [glyph_name]

    return ufo


def rename_glyphs(ufo: Font, name_mapping: dict[str, str]):
    for glyph in ufo:
        for component in glyph.components:
            if new_name := name_mapping.get(component.baseGlyph):
                component.baseGlyph = new_name

    for old_name, new_name in name_mapping.items():
        if new_name in ufo:
            continue  # TODO: duplicated new names should not be allowed in name_mapping
        ufo.renameGlyph(old_name, new_name)


def constructMissingGlyphs(ufo: Font):
    with (data_dir / "glyphs.yaml").open() as f:
        expected_glyph_names: dict[str, None] = yaml.safe_load(f)

    for expected_glyph_name in expected_glyph_names.keys():
        if expected_glyph_name not in ufo:
            glyph = ufo.newGlyph(expected_glyph_name)
            # FIXME: populate glyph.components

    assert ufo.keys() >= expected_glyph_names.keys()


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

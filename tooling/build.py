import argparse
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import cast

import yaml
from fontmake.font_project import FontProject
from fontTools.feaLib.parser import Parser
from fontTools.ttLib import TTFont
from fontTools.ttLib.tables._n_a_m_e import table__n_a_m_e
from glyphsLib import GSFont
from glyphsLib.builder import UFOBuilder
from ufoLib2.objects import Font, Info

tooling_dir = Path(__file__).parent
repo_dir = tooling_dir / ".."

data_dir = repo_dir / "data"
otl_dir = tooling_dir / "otl"


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
        builder = UFOBuilder(GSFont(font_path))
        (ufo,) = builder.masters

    source_glyph_name_to_expected: dict[str, str]
    if glyph_name_mapping_path:
        with glyph_name_mapping_path.open() as f:
            data: dict[str, str | None] = yaml.safe_load(f)
        source_glyph_name_to_expected = {k: v or k for k, v in data.items()}
    else:
        source_glyph_name_to_expected = {}
    assert source_glyph_name_to_expected.keys() <= ufo.keys(), (
        source_glyph_name_to_expected.keys() - ufo.keys()
    )

    constructMissingGlyphs(ufo)

    build(
        ufo=ufo,
        family_name=args.family_name,
        output_dir=args.output_dir,
    )


def constructMissingGlyphs(ufo: Font):
    with (data_dir / "glyphs.yaml").open() as f:
        expected_glyph_names: dict[str, None] = yaml.safe_load(f)

    for expected_glyph_name in expected_glyph_names.keys():
        if expected_glyph_name not in ufo:
            ufo.newGlyph(expected_glyph_name)

    # TODO

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

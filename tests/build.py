import argparse
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Literal, cast

import yaml
from fontmake.font_project import FontProject
from fontTools.ttLib import TTFont
from fontTools.ttLib.tables._n_a_m_e import table__n_a_m_e
from glyphsLib.builder import UFOBuilder
from glyphsLib.parser import load
from mongfontbuilder import constructFont
from ufoLib2.objects import Font, Info

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


def main() -> None:
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
        with glyph_name_mapping_path.open(encoding="utf-8") as f:
            data: dict[str, str | None | Literal[False]] = yaml.safe_load(f)
            for source_name, utn_name in data.items():
                glyph_name_mapping[source_name] = utn_name or source_name

    constructFont(ufo)

    build(
        ufo=ufo,
        family_name=family_name,
        output_dir=output_dir,
        debug=args.debug,
    )


def build(
    ufo: Font,
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

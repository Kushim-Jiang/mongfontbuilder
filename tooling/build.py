import argparse
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import cast

from fontmake.font_project import FontProject
from fontTools.feaLib.parser import Parser
from fontTools.ttLib import TTFont
from fontTools.ttLib.tables._n_a_m_e import table__n_a_m_e
from ufoLib2.objects import Font, Info

tooling_dir = Path(__file__).parent


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("ufo", type=Path)
    parser.add_argument("family_name")
    parser.add_argument("--output-dir", type=Path, default=Path.cwd())
    args = parser.parse_args()

    build(
        ufo=Font.open(args.ufo),
        otl_code_path=tooling_dir / "otl" / "main.fea",
        family_name=args.family_name,
        output_dir=args.output_dir,
    )


def build(
    ufo: Font,
    otl_code_path: Path,
    family_name: str,
    output_dir: Path,
    keep_info=False,
) -> Path:
    """Common logic for building fonts."""

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

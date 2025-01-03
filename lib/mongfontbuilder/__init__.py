import re
from collections.abc import Iterable
from dataclasses import dataclass
from importlib.resources import files

import yaml
from fontTools.feaLib.ast import FeatureFile
from fontTools.feaLib.parser import Parser
from fontTools.misc.transform import Identity
from ufoLib2.objects import Component, Font, Glyph


def makeFeatureFile(availableGlyphs: Iterable[str] = ()) -> FeatureFile:
    """
    Specify `availableGlyphs` to validate the glyph set against the feature file’s requirement.
    An empty set is ignored by `Parser`.
    """

    assert __package__
    path = files(__package__) / "otl" / "main.fea"
    with path.open(encoding="utf-8") as f:
        return Parser(featurefile=f, glyphNames=availableGlyphs).parse()


@dataclass
class UTNGlyphName(str):
    """
    Besides the graphical .joining_position, there’s also a joining position in terms of shaping logic that may appear in a glyph name. For example, uni1828.N.init._isol is an isol glyph in terms of shaping, but graphically it’s actually N.init.
    """

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


def constructGlyphSet(
    ufo: Font, glyph_name_mapping: dict[str, str], left_spacing=40, right_spacing=100
):
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
    _quote_glyph([ufo["__.notdef"]], glyph)
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

    nominal_mapping = dict[str, str]()  # FIXME

    expected_glyph_names = dict[str, dict[str, None]]()
    assert __package__
    dir = files(__package__) / "data" / "glyphs"
    suffix = ".yaml"
    for path in dir.iterdir():
        if path.name.endswith(suffix):
            with path.open(encoding="utf-8") as f:
                expected_glyph_names[path.name.removesuffix(suffix)] = yaml.safe_load(f)

    # variant glyphs
    for glyph_name in expected_glyph_names["variants"]:
        glyph = ufo.newGlyph(glyph_name)
        if source_names := utn_name_to_source_names.get(glyph_name, []):
            ref_glyph = ufo[source_names[0]]
            _quote_glyph([ref_glyph], glyph)
        elif source_names := cp_agnostic_name_to_source_names.get(_get_units(glyph_name) or "", []):
            ref_glyph = ufo[source_names[0]]
            _quote_glyph([ref_glyph], glyph)
        elif "_" not in glyph_name:
            print(f"we don't have {glyph_name}")
        glyph.unicode = None
        glyph_order.append(glyph_name)

    for glyph_name in expected_glyph_names["variants"]:  # depends on the loop above
        if "._" in glyph_name:
            if glyph_name.endswith("isol"):
                _quote_glyph([left_spacing, ufo[glyph_name[:-6]], right_spacing], ufo[glyph_name])
            elif glyph_name.endswith("init"):
                _quote_glyph([left_spacing, ufo[glyph_name[:-6]]], ufo[glyph_name])
            elif glyph_name.endswith("fina"):
                _quote_glyph([ufo[glyph_name[:-6]], right_spacing], ufo[glyph_name])

    # nominal glyphs
    for glyph_name, written_units in nominal_mapping.items():
        glyph = ufo.newGlyph(glyph_name)
        cmap_glyphs = [
            glyph for glyph in ufo if glyph.unicode == UTNGlyphName(glyph_name).code_point()
        ]
        if len(cmap_glyphs):
            ref_glyph = cmap_glyphs[0]
            _quote_glyph([ref_glyph], glyph)
        else:
            _quote_glyph(
                [left_spacing, ufo[glyph_name + "." + written_units], right_spacing],
                glyph,
            )
        glyph.unicode = UTNGlyphName(glyph_name).code_point()
        glyph_order.append(glyph_name)

    # ligatures and format controls
    for glyph_name in expected_glyph_names["ligatures"] | expected_glyph_names["format-controls"]:
        glyph = ufo.newGlyph(glyph_name)
        if source_names := utn_name_to_source_names.get(glyph_name, []):
            ref_glyph = ufo[source_names[0]]
            _quote_glyph([ref_glyph], glyph)
        else:
            print(f"we don't have {glyph_name}")
        glyph_order.append(glyph_name)

    # empty glyphs
    for glyph_name in expected_glyph_names["empty"]:
        glyph = ufo.newGlyph(glyph_name)
        glyph_order.append(glyph_name)

    ufo.glyphOrder = glyph_order


def _get_units(glyph_name: str | None):
    if not glyph_name or "._" in glyph_name:
        return None
    else:
        return UTNGlyphName(glyph_name).code_point_agnostic()


def _quote_glyph(old_glyphs: list[Glyph | int], new_glyph: Glyph):
    for glyph in old_glyphs:
        if isinstance(glyph, int):
            new_glyph.width += glyph
        else:
            component = Component(glyph.name or "", Identity.translate(int(new_glyph.width), 0))
            new_glyph.components.append(component)
            new_glyph.width += glyph.width

"""
Generate ``tests/unified.ufo``.

``unified.ufo`` is the single source font that carries every written unit, every
ligature (already combined), the control characters, the digits and the
punctuation of all seven locales at once, so that one font can be composed for
every writing system:

    uv run python -m mongfontbuilder tests/unified.ufo out.otf \\
        --locales MNG MNGx TOD TODx SIB MCH MCHx

Outlines are copied from Noto Sans Mongolian wherever a glyph of the same
written form exists; anchors are dropped, because the composed font builds its
own mark attachments; a glyph that has no Noto counterpart is created empty.

Usage:

    uv run python tools/make_unified_ufo.py
"""

from __future__ import annotations

import json
import re
from copy import deepcopy
from pathlib import Path
from typing import cast

from fontTools import unicodedata
from ufoLib2 import Font

from mongfontbuilder.data.types import LocaleID

REPO = Path(__file__).resolve().parents[1]
DATA_DIR = REPO / "lib" / "mongfontbuilder" / "data"
TEMPLATE_UFO = REPO / "tests" / "hudum.ufo"
OUTPUT_UFO = REPO / "tests" / "unified.ufo"
NOTO_UFO = Path("D:/Github/notofonts-mongolian/sources/NotoSansMongolian.ufo")

POSITIONS = ("isol", "init", "medi", "fina")

# Shapes the composer draws other glyphs from, e.g. the wide MVS from the space and the
# nirugu written unit from the nirugu. They come before the written forms, so that a
# reader of the font meets the building blocks first.
BASE_GLYPHS = ("mvs.narrow", "nirugu", "space")

CONTROL_GLYPHS = (
    "mvs",
    "mvs.narrow",
    "mvs.nominal",
    "nirugu",
    "space",
    "nnbsp",
    "fvs1",
    "fvs2",
    "fvs3",
    "fvs4",
    "zwj",
    "zwnj",
)

# Characters that are not drawn as written units, in the order the font lists them: the
# marks of the Mongolian block that the punctuation table names, the digits, and the
# letters and signs outside the cursive letter inventories.
MONGOLIAN_MARK_CODEPOINTS = (
    0x1800,
    *range(0x11660, 0x1166D),
    *range(0x1801, 0x1807),
    0x1808,
    0x1809,
)

DIGIT_CODEPOINTS = tuple(range(0x1810, 0x181A))

OTHER_LETTER_CODEPOINTS = (
    0x1880,
    0x1881,
    0x1882,
    0x1883,
    0x1884,
    0x1885,
    0x1886,
    0x18A9,
)

# Letters of the above that are drawn in a shape of their own before FVS1.
FVS1_VARIANT_CODEPOINTS = (0x1880, 0x1881)

# The dotted circle, which stands in for a written unit with no letter around it.
DOTTED_CIRCLE_CODEPOINT = 0x25CC

# Noto names a few standalone characters descriptively instead of `uniXXXX`.
NOTO_ALIASES = {0x1885: "baluda", 0x1886: "tribaluda", 0x18A9: "dagalga"}

# Noto draws several written units that this project names differently — `Dw` is its
# `Ds`, `Sx2` its `Sx`, `Zz2` its `Zc`, `Zz3` its `Zz` — and some whose Noto name does not
# follow its usual `uniXXXX.‹units›.‹position›` shape. Such a glyph names its source here;
# the name is only a hint, so a glyph whose source is missing is still left empty.
NOTO_GLYPH = {
    "_Cx.fina": "uni1878.Cx.medi._fina",
    "_Cx.init": "uni1878.Cx.init",
    "_Cx.medi": "uni1878.Cx.medi",
    "_Dw.medi": "uni18A1.Ds.medi",
    "_Dz.init": "uni1898.Dz.init",
    "_Dz.medi": "uni1898.Dz.medi",
    "_Hx2.fina": "uni1874.Hx.fina",
    "_Hx.fina.mvs": "Hx.fina.mvs",
    "_Kh.fina": "uni186C.Kh.medi._fina",
    "_N2.init": "N2.init.mvs",
    "_N.fina.mvs": "N.fina.mvs",
    "_Sx2.init": "uni18A2.Sx.init",
    "_Sx2.medi": "uni18A2.Sx.medi",
    "_Sx2.fina": "uni18A2.Sx.fina",
    "_WpA.fina": "WpA2.fina",
    "_Zr2.init": "uni188C.Zr.init",
    "_Zr2.medi": "uni188C.Zr.medi",
    "_Zr2.fina": "uni188C.Zr.fina",
    "_Zs2I.isol": "ZsI.isol",
    "_Zs2I.init": "ZsI.init",
    "_Zs2I.medi": "ZsI.medi",
    "_Zs2I.fina": "ZsI.fina",
    "_Zz2.init": "uni185C.Zc.init",
    "_Zz2.medi": "uni185C.Zc.medi",
    # `_Zz2.fina` has no counterpart in Noto, and is deliberately left empty.
    "_Zz3.init": "uni1896.Zz.init",
    "_Zz3.medi": "uni1896.Zz.medi",
    "_Zz3.fina": "uni1896.Zz.fina",
    # The em dash and its upright form are drawn as the fullwidth hyphen-minus and its
    # upright form, which Noto draws as such.
    "u2014": "uniFF0D",
    "u2014.vert": "uniFF0D.vert",
}


def readJson(name: str):
    return json.loads((DATA_DIR / f"{name}.json").read_text(encoding="utf-8"))


def punctuationEntries() -> list[tuple[str, int]]:
    """Names and code points of the punctuation table in ``data/writtenUnits.ts``."""

    source = (REPO / "data" / "writtenUnits.ts").read_text(encoding="utf-8")
    block = source.split("export const punctuation = {")[1].split("} as const;")[0]
    return [
        (name, int(codePoint, 16))
        for name, codePoint in re.findall(r"(\w+): \{ unicode: (0x[0-9A-Fa-f]+)", block)
    ]


# Noto names a written-unit glyph either `<units>.<position>` (a shared ligature) or
# `uniXXXX.<units>.<position>` (drawn per character); the leading `_` and the code
# point segment carry no meaning for this project, which shares written units.
WRITTEN_UNIT = re.compile(r"^_?uni[0-9A-F]{4,6}\.([A-Za-z0-9_]+\.[a-z]+)$")
NOTO_UNIT_WITH_CODE_POINT = re.compile(r"^_?uni([0-9A-F]{4,6})\.([A-Za-z0-9_]+\.[a-z]+)$")
NOTO_UNIT_ALONE = re.compile(r"^_?([A-Za-z0-9_]+\.[a-z]+)$")
NOTO_STANDALONE = re.compile(r"^_?uni([0-9A-F]{4,6})$|^_?u([0-9A-F]{5,6})$")


UNIT_WITH_CODE_POINTS = re.compile(r"^_?u([0-9A-F]{4,6})(?:_u[0-9A-F]{4,6})*\.(.+)$")
POSITION = re.compile(r"^_?(isol|init|medi|fina)$")


def bodyOf(name: str) -> str | None:
    """`‹units›.‹position›` of a project written-unit glyph, else None.

    The code points that prefix a variant glyph say which character drew it, which
    this project does not care about: it shares one written unit across characters.
    """

    stripped = name.removeprefix("_")
    body = match.group(2) if (match := UNIT_WITH_CODE_POINTS.match(stripped)) else stripped
    segments = body.split(".")
    if len(segments) == 2 and POSITION.match(segments[1]):
        return body
    return None


def isLvs(written: str) -> bool:
    """Whether a written form ends in the long vowel sign written unit (`Lv`)."""

    return written.endswith("Lv")


# Noto's descriptive names for characters this project names by code point.
NOTO_NAME_REVERSAL = {v: f"u{k:04X}" for k, v in NOTO_ALIASES.items()}


def projectNameFor(notoName: str) -> str:
    """This project's glyph name for a glyph of Noto's.

    Noto draws a written unit once per character, so the code point segment is what
    distinguishes its glyphs; this project shares one glyph across characters and
    therefore drops that segment.
    """

    if notoName in CONTROL_GLYPHS:
        return notoName
    if reversedAlias := NOTO_NAME_REVERSAL.get(notoName):
        return reversedAlias
    if match := NOTO_UNIT_WITH_CODE_POINT.match(notoName):
        return "_" + match.group(2)
    if match := NOTO_STANDALONE.match(notoName):
        return f"u{int(match.group(1) or match.group(2), 16):04X}"
    if match := NOTO_UNIT_ALONE.match(notoName):
        return "_" + match.group(1)
    return notoName


def notoCandidates(name: str, index: dict[str, list[str]]) -> list[str]:
    """Noto glyphs that can stand in for a glyph of this project, best first."""

    found = list[str]()
    if override := NOTO_GLYPH.get(name):
        found.append(override)
    if body := bodyOf(name):
        found.extend(index.get(body, []))
    if match := UNIT_WITH_CODE_POINTS.match(name):
        # Keep the code points, for glyphs Noto draws per character with a suffix of
        # its own, such as `u1880.fvs1`.
        codePoint = int(match.group(1), 16)
        prefix = f"uni{codePoint:04X}" if codePoint <= 0xFFFF else f"u{codePoint:X}"
        found.append(f"{prefix}.{match.group(2)}")
    if name in CONTROL_GLYPHS:
        found.append(name)
    if match := re.fullmatch(r"u([0-9A-F]{4,6})", name):
        codePoint = int(match.group(1), 16)
        if codePoint in NOTO_ALIASES:
            found.append(NOTO_ALIASES[codePoint])
        else:
            found.append(f"uni{codePoint:04X}" if codePoint <= 0xFFFF else f"u{codePoint:X}")
    return found


def buildNotoIndex(noto: Font) -> dict[str, list[str]]:
    """Map `‹units›.‹position›` to the Noto glyphs that draw it."""

    index: dict[str, list[str]] = {}
    for name in noto.keys():
        # A glyph is also indexed under its own name, for Noto glyphs that draw a
        # written unit without naming a character.
        body = match.group(1) if (match := WRITTEN_UNIT.match(name)) else name
        index.setdefault(body, []).append(name)
    return {k: sorted(v) for k, v in index.items()}


def resolveAlias(noto: Font, name: str) -> str:
    """Follow Noto's single-component aliases to the glyph that holds the drawing.

    Noto marks a written unit borrowed from another joining position by aliasing it,
    e.g. `uni1869.Th.init` is a lone component pointing at `uni1869.Th.init._isol`.
    """

    seen = set[str]()
    while name not in seen:
        seen.add(name)
        glyph = noto[name]
        bases = [i.baseGlyph for i in glyph.components]
        if glyph.contours or len(bases) != 1 or bases[0] not in noto:
            return name
        name = bases[0]
    return name


# Glyphs the composer creates itself, from written units and their variants.
COMPOSER_GLYPH = re.compile(
    r"^u[0-9A-F]{4,6}(\.[A-Za-z0-9_]+\.(isol|init|medi|fina)(\.[A-Za-z_]+)*)?$"
)


def composerGlyphNames(known: list[str]) -> tuple[set[str], set[str]]:
    """Glyph names the composer references, and the glyphs it builds by itself.

    The composer names most variant glyphs after a written form and a joining
    position, but some names no dataset lists — the TODO long vowel sign combinations,
    the FVS forms of the Ali Gali anusvara and visarga, the post-wa form of isolated A
    — so they are read off the composer itself rather than re-derived here.
    """

    from mongfontbuilder import data
    from mongfontbuilder.otl import MongFeaComposer

    composer = MongFeaComposer(cmap={}, glyphs=known, locales=[*data.locales])
    referenced = set[str]()
    spec = composer.compose()
    referenced.update(GLYPH_NAME.findall(composer.asFeatureFile().asFea()))
    return referenced, {*spec.newGlyphs}


# A glyph name the composer uses for a variant: a character's code points, then the
# written form. A bare code point is not one of them: those glyphs are the cmap entries
# the composer builds from the written units.
GLYPH_NAME = re.compile(r"\bu[0-9A-F]{4,6}(?:_u[0-9A-F]{4,6})*\.[A-Za-z0-9_]+(?:\.[A-Za-z0-9_]+)*")


def lvsWrittenForms() -> set[str]:
    """Source written forms a long vowel sign variant is drawn from.

    The composer builds `u1820_u1843.AALv.isol` as a component of `_AALv.isol`, so that
    written form is what the source font has to carry.
    """

    from mongfontbuilder import GlyphDescriptor, data
    from mongfontbuilder.utils import getAliasesByLocale, getCharNameByAlias

    names = set[str]()
    for locale in data.locales:
        for alias in getAliasesByLocale(locale):
            charName = getCharNameByAlias(locale, alias)
            for position, fvsToVariant in data.variants[charName].items():
                for variant in fvsToVariant.values():
                    if not (locale in variant.locales and variant.locales[locale].lvs):
                        continue
                    base = GlyphDescriptor.fromData(
                        charName,
                        position,
                        variant,
                        locale=cast(LocaleID, locale.removesuffix("x")),
                    )
                    names.add(str(GlyphDescriptor([], base.units + ["Lv"], base.position)))
    return names


def main() -> None:
    writtenUnits: dict[str, dict[str, object]] = readJson("writtenUnits")
    ligatures: dict[str, dict[str, list[str]]] = readJson("ligatures")
    variants: dict[str, object] = readJson("variants")

    # Characters the composer derives from written units itself: their `uXXXX`
    # glyph is created as a component of a written-unit glyph, so it must not be
    # defined in the source font.
    letterCodePoints = {ord(unicodedata.lookup(name)) for name in variants}

    # name -> unicodes
    wanted: dict[str, list[int]] = {}

    def want(name: str, unicodes: list[int] | None = None) -> None:
        wanted.setdefault(name, [] if unicodes is None else unicodes)

    # The building blocks first, in the order a written form draws them.
    for name in BASE_GLYPHS:
        want(name)

    # Then the variants: every written unit, at each joining position it is drawn in, in
    # alphabetical order of the written unit and isol/init/medi/fina order of the
    # position. A written unit drawn before an MVS follows the plain one.
    for unit in sorted(i for i in writtenUnits if not isLvs(i)):
        for position in POSITIONS:
            if position not in writtenUnits[unit]:
                continue
            want(f"_{unit}.{position}")
            if "pre_mvs" in cast(dict[str, object], writtenUnits[unit][position]):
                want(f"_{unit}.{position}.mvs")

    # Then the variants with the long vowel sign: the `Lv` written unit itself, and the
    # written forms a long vowel sign follows, e.g. `_AALv.isol`.
    lvsUnits = {
        f"_{unit}.{position}"
        for unit in writtenUnits
        if isLvs(unit)
        for position in POSITIONS
        if position in writtenUnits[unit]
    }
    for name in sorted(lvsUnits | lvsWrittenForms()):
        want(name)

    # Then the ligatures, the plain ones first and those with the long vowel sign after.
    for lvs in (False, True):
        for table in ligatures.values():
            for name in sorted(i for i in table if isLvs(i) == lvs):
                for position in sorted(table[name], key=POSITIONS.index):
                    want(f"_{name}.{position}")

    # Then the characters that are not written as written units: the marks of the
    # punctuation table that belong to the Mongolian block, the digits, and the letters
    # and signs outside the cursive letter inventories.
    for codePoint in (
        *MONGOLIAN_MARK_CODEPOINTS,
        *DIGIT_CODEPOINTS,
        *OTHER_LETTER_CODEPOINTS,
    ):
        if codePoint in letterCodePoints:
            continue  # the composer builds this one from its written units
        want(f"u{codePoint:04X}", [codePoint])
        if codePoint in FVS1_VARIANT_CODEPOINTS:
            want(f"u{codePoint:04X}.fvs1")

    # Then the punctuation of the other scripts, in code point order, each followed by
    # the upright form the composer draws for it.
    for name, codePoint in sorted(punctuationEntries(), key=lambda i: i[1]):
        if codePoint in MONGOLIAN_MARK_CODEPOINTS:
            continue  # an entry of the Mongolian marks above
        want(f"u{codePoint:04X}", [codePoint])
        if name.startswith("China"):
            want(f"u{codePoint:04X}.vert")

    # Then the dotted circle, which stands in for a written unit that has no letter
    # around it, and the control characters that shape the written forms.
    want(f"u{DOTTED_CIRCLE_CODEPOINT:04X}", [DOTTED_CIRCLE_CODEPOINT])
    for name in CONTROL_GLYPHS:
        want(name)

    # Whatever the composer references but neither the datasets above nor the composer
    # itself provide: a character whose default written form differs in every writing
    # system, for example.
    referenced, created = composerGlyphNames([*wanted])
    for name in sorted(referenced - created - {*wanted}):
        want(name)

    # Glyphs the composer builds by itself are not source glyphs, even where the data
    # above names them: the wide MVS is built from the space, the nirugu written unit
    # from the nirugu.
    for name in sorted(created & {*wanted}):
        del wanted[name]

    font = Font.open(TEMPLATE_UFO)
    # Keep the template's font info, but start from a clean glyph set. The template
    # already carries the project's code point assignments for the control glyphs,
    # which are authoritative, so they are snapshotted before the glyphs go away.
    controlUnicodes = {name: [*font[name].unicodes] for name in CONTROL_GLYPHS if name in font}
    for name in [*font.keys()]:
        if name != ".notdef":
            del font[name]

    noto = Font.open(NOTO_UFO)
    notoIndex = buildNotoIndex(noto)
    copiedCount = 0
    empty: list[str] = []

    for name, unicodes in wanted.items():
        glyph = font.newGlyph(name)
        glyph.unicodes = [*controlUnicodes.get(name, unicodes)]
        candidates = [i for i in notoCandidates(name, notoIndex) if i in noto]
        # Prefer a candidate whose drawing is actually drawn somewhere: Noto leaves a
        # few written-unit glyphs empty and aliases others to a sibling glyph.
        resolved = [(i, resolveAlias(noto, i)) for i in candidates]
        pair = next(
            ((i, d) for i, d in resolved if noto[d].contours),
            resolved[0] if resolved else None,
        )
        if pair is None:
            empty.append(name)
            continue
        source, drawingName = pair
        glyph.width = noto[source].width
        drawing = noto[drawingName]
        for contour in drawing.contours:
            glyph.contours.append(deepcopy(contour))
        for component in drawing.components:
            baseGlyph = projectNameFor(component.baseGlyph)
            known = baseGlyph in wanted or COMPOSER_GLYPH.match(baseGlyph)
            if baseGlyph == name or not known:
                continue
            copiedComponent = deepcopy(component)
            copiedComponent.baseGlyph = baseGlyph
            glyph.components.append(copiedComponent)
        # Anchors are deliberately not copied.
        copiedCount += 1

    # Glyph order: the building blocks, the variants, the ligatures, then the rest — the
    # order the glyphs were created in above.
    font.lib["public.glyphOrder"] = [".notdef", *wanted]
    font.lib.pop("public.skipExportGlyphs", None)

    font.save(OUTPUT_UFO, overwrite=True)

    print(f"wrote {OUTPUT_UFO}")
    print(f"  glyphs: {len(font)}")
    print(f"  copied from Noto: {copiedCount}")
    print(f"  left empty: {len(empty)}")
    for name in sorted(empty):
        print(f"    {name}")


if __name__ == "__main__":
    main()

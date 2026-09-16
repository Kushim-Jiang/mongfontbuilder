"""Compose the unified source font.

``tests/unified.ufo`` carries the written units of every writing system at once, so the
whole block composes from a single source font. This module builds that font for all
writing systems and leaves the composed UFO and OTF in ``temp/`` for inspection:

    uv run pytest tests/test_unified.py -s
"""

from collections import Counter
from collections.abc import Iterator
from dataclasses import replace
from functools import cache
from pathlib import Path
from re import match as reMatch

import pytest
import uharfbuzz as hb
from _pytest.mark.structures import ParameterSet
from fontTools import unicodedata
from fontTools.feaLib import ast
from ufoLib2 import Font

from fixtures import EAC_UNIFIED_XFAIL, compileOTF, loadRawTestCases
from mongfontbuilder import GlyphDescriptor, data, splitWrittens
from mongfontbuilder.data.types import JoiningPosition, LocaleID, fina
from mongfontbuilder.otl import MongFeaComposer
from mongfontbuilder.otl.iii import lvsVariants
from mongfontbuilder.spec import FontSpec, GlyphSpec, applySpecToFont
from mongfontbuilder.utils import getAliasesByLocale, getCharNameByAlias
from utils import parseAliases, parseLetter, parseWrittenUnits, tempDir, testsDir

SOURCE = testsDir / "unified.ufo"
composedUFO = tempDir / "unified.ufo"
composedOTF = tempDir / "unified.otf"

# The language system each writing system is shaped under: a writing system and its Ali
# Gali extension are declared in the same language system.
LANGUAGE = {
    "hud": "MNG ",
    "hag": "MNG ",
    "tod": "TOD ",
    "tag": "TOD ",
    "sib": "SIB ",
    "man": "MCH ",
    "mag": "MCH ",
}

# The test suites to shape the composed font with: the EAC suite of Hudum, which is the
# only writing system the EAC documents, and the suites of the Chinese national standard.
TEST_SUITES = {
    "eac": ["hud"],
    "core": ["hud", "hag", "tod", "tag", "sib", "man", "mag"],
}

# How this font carries out the stretching of the stem at Phase IIb.4. A bowed written form
# leaves a stem to the written form that follows it, and the stem is stretched with the
# nirugu where that written form extends.
#
# The written forms that a bowed written form leaves a stem to: the medial and final forms
# of the letters that stretch, read off `otl/lookups-general-optional.fea` of Noto Sans
# Mongolian, whose glyph names differ from this font's only in their code point prefix.
EXTENDING = [
    "u1820.A.medi",
    "u1820.A.fina",
    "u1821.A.medi",
    "u1821.A.fina",
    "u1823.O.medi",
    "u1823.O.fina",
    "u1823.U.fina",
    "u1824.O.medi",
    "u1824.O.fina",
    "u1824.U.fina",
    "u1825.O.medi",
    "u1825.OI.medi",
    "u1825.O.fina",
    "u1825.U.fina",
    "u1826.O.medi",
    "u1826.OI.medi",
    "u1826.O.fina",
    "u1826.U.fina",
    "u1828.A.fina",
    "u1828.N.fina",
    "u182A.B.medi",
    "u182A.B.fina",
    "u182B.P.medi",
    "u182B.P.fina",
    "u182D.G.fina",
    "u182E.M.medi",
    "u182E.M.fina",
    "u182F.L.medi",
    "u182F.L.fina",
    "u1832.T.medi",
    "u1832.T.fina",
    "u1833.Dd.medi",
    "u1833.Dd.fina",
    "u1835.I.fina",
    "u1836.I.fina",
    "u1839.F.medi",
    "u1839.F.fina",
    "u183B.K.medi",
    "u183B.K.fina",
    "u183A.K2.medi",
    "u183A.K2.fina",
]

# The written forms that are drawn with a stem of their own, and so are the ones that the
# preceding bowed written form leaves that stem to. Read off the same file.
BOWED_EXTENSIONS = [
    "u182A.B.init",
    "u182A.B.medi",
    "u182B.P.init",
    "u182B.P.medi",
    "u182D.G.init",
    "u182D.G.medi",
    "u182D.Gx.init",
    "u182D.Gx.medi",
    "u182C.G.init",
    "u182C.G.medi",
    "u182C.Gx.init",
    "u182C.Gx.medi",
    "u182E.M.init",
    "u182E.M.medi",
    "u182F.L.init",
    "u182F.L.medi",
    "u1839.F.init",
    "u1839.F.medi",
    "u183B.K.init",
    "u183B.K.medi",
    "u183A.K2.init",
    "u183A.K2.medi",
    "u1897.Q.init",
    "u1897.Q.medi",
]

# The letters whose bow an extending written form would touch.
BOWED = ["b", "p", "f", "k", "k2"]

# The Ali Gali vowel written forms, which an extended written form stands before.
VOWELS = {"MNG": ["a", "ue", "ee", "o"], "MNGx": ["a", "iX", "ue", "ee", "o"]}

# The margin the punctuation marks are drawn with, at each side of the drawing: a mark is
# drawn with this much space to its left and to its right, and its vertical form is drawn
# with the same margin above and below. The margin is what `verticalMargins` gives a
# vertical form, and it is why this font writes no `vpal` feature.
VERTICAL_MARGIN = 100

# The marks that are drawn over the written form they follow rather than beside it, which
# `markAnchors` anchors at the origin so that they stay where they were drawn, and the
# writing systems that write with them. A mark of another writing system is not anchored:
# whether a mark is written over a written form is a choice each writing system makes.
MARK_GLYPHS = ["u1885", "u1886", "u18A9"]
MARK_LOCALES: list[LocaleID] = ["MNG", "MNGx"]
MARK_CLASS_NAME = "Mongolian"

# How this font draws the written form of a letter and the long vowel sign, one rule per
# written form the sign is written with. The key is the written units the sign follows,
# whose consonant is filled in for `{C}`; the value is the drawings of each joining
# position, in the order the written form draws them.
#
# The sign is the written unit of the joining position the written form ends at, or its
# mark where the sign closes a shape that is drawn as one piece — the mark comes before
# the shape there, so that the two share the origin of the written form.
#
# How a written form of the sign is drawn is a choice a font makes — Noto draws the vowel
# forms of Hudum and this font draws all of them — so the rules are held here with the
# rest of the unified font's choices, not in the library.
LVS_FORMS: list[tuple[str, dict[str, list[str]]]] = [
    ("{C}A", {"init": ["_{C}A.init", "_Lv.mark"], "medi": ["_{C}A.medi", "_Lv.mark"]}),
    ("{C}Aa", {"isol": ["_{C}A.init", "_AaLv.fina"], "fina": ["_{C}A.medi", "_AaLv.fina"]}),
    (
        "{C}E",
        {
            "isol": ["_{C}E.isol", "_Lv.mark"],
            "init": ["_{C}E.init", "_Lv.mark"],
            "medi": ["_{C}E.medi", "_Lv.mark"],
            "fina": ["_{C}E.fina", "_Lv.mark"],
        },
    ),
    (
        "{C}O",
        {
            "isol": ["_{C}O.init", "_Lv.fina"],
            "init": ["_{C}O.init", "_Lv.medi"],
            "medi": ["_{C}O.medi", "_Lv.medi"],
            "fina": ["_{C}O.medi", "_Lv.fina"],
        },
    ),
    (
        "{C}Ob",
        {
            "isol": ["_{C}Ob.init", "_Lv.fina"],
            "init": ["_{C}Ob.init", "_Lv.medi"],
            "medi": ["_{C}Ob.medi", "_Lv.medi"],
            "fina": ["_{C}Ob.medi", "_Lv.fina"],
        },
    ),
    (
        "{C}Ot",
        {
            "isol": ["_{C}Ot.init", "_Lv.fina"],
            "init": ["_{C}Ot.init", "_Lv.medi"],
            "medi": ["_{C}Ot.medi", "_Lv.medi"],
            "fina": ["_{C}Ot.medi", "_Lv.fina"],
        },
    ),
    (
        "{C}Ip",
        {
            "isol": ["_{C}Ip.init", "_IyLv.fina"],
            "init": ["_{C}Ip.init", "_Lv.mark"],
            "medi": ["_{C}Ip.medi", "_Lv.medi"],
            "fina": ["_{C}Ip.medi", "_Lv.fina"],
        },
    ),
    ("Aa", {"fina": ["_Lv.mark", "_Aa.fina"]}),
    ("Iy", {"fina": ["_Lv.mark", "_Iy.fina"]}),
    ("O", {"medi": ["_O.medi", "_Lv.medi"], "fina": ["_O.medi", "_Lv.fina"]}),
    (
        "AO",
        {
            "isol": ["_A.init", "_O.medi", "_Lv.fina"],
            "init": ["_A.init", "_O.medi", "_Lv.medi"],
        },
    ),
]


class UnifiedMongFeaComposer(MongFeaComposer):
    """A composer with the optional treatments the unified font takes.

    The library leaves these open: they are choices a font makes, and the per-writing-system
    fonts stay as they are by not taking them. The unified font takes them, so the code lives
    here rather than in the library.
    """

    def compose(self) -> FontSpec:
        # The written forms of the sign are drawn before Phase III ligates the sign, so that
        # the ligature of the sign finds a written form to be built from, and after the
        # written units are initials, which the written forms are drawn from.
        self.spliceLvsWrittenForms()
        spec = super().compose()
        self.composeVerticalForms()
        self.composeMarkAnchors()
        self.iib4()
        return spec

    def composeMarkAnchors(self) -> None:
        """Anchor the marks that are drawn over a written form, which the library leaves open.

        The source font carries no anchors, because the marks of this font are drawn over
        the whole written form rather than at a place on it, and whether a font positions
        them at all is a choice a font makes. This font takes the choice.
        """

        self.markAnchors()

    def markAnchors(self) -> None:
        """Anchor every mark of the font at the origin, and every written form under it.

        The marks `baluda`, `tribaluda` and `dagalga` are drawn over the written form they
        follow rather than beside it, so both the mark and the written form are anchored at
        the origin and the mark stays where it was drawn. The written forms that carry them
        are the ones of Hudum and Hudum Ali Gali, which are the writing systems the marks
        are written with, and the dotted circle, which stands in for a written form that is
        written with no letter around it.

        A written form may be drawn under a mark in any of its joining positions, so every
        position of the letters of the two writing systems is anchored, and so are the
        written units they are drawn with.
        """

        markNames = [self.glyphNameProcessor(i) for i in MARK_GLYPHS if i in self.glyphs]
        if not markNames:
            return
        bases = self.markAnchorBases()
        if not bases:
            return
        markClass = ast.MarkClass(MARK_CLASS_NAME)
        definition = ast.MarkClassDefinition(
            markClass, ast.Anchor(0, 0), self.glyphClass(markNames)
        )
        markClass.addDefinition(definition)
        self.current.append(definition)
        with self.Lookup("Ib.marks.posit", feature="mark"):
            self.current.append(
                ast.MarkBasePosStatement(self.glyphClass(bases), [(ast.Anchor(0, 0), markClass)])
            )

    def markAnchorBases(self) -> list[str]:
        """The written forms the marks of this font are drawn over.

        The marks belong to Hudum and its Ali Gali extension, so the written forms of those
        two writing systems are the ones that carry them: every writing form of every letter
        they write, in every joining position the letter is drawn in.
        """

        written = set[str]()
        for locale in MARK_LOCALES:
            if locale not in self.locales:
                continue
            for alias in getAliasesByLocale(locale):
                charName = getCharNameByAlias(locale, alias)
                for position in data.variants[charName]:
                    for variant in data.variants[charName][position].values():
                        written.add(str(GlyphDescriptor.fromData(charName, position, variant)))
        return sorted(i for i in written if i in self.glyphs or i in self.spec.newGlyphs)

    def composeVerticalForms(self) -> None:
        """Write the vertical forms of the punctuation marks, which Phase Ib leaves open.

        The library leaves Phase Ib empty: whether a font writes a punctuation mark with a
        vertical form, and how that form is drawn, is a choice a font makes. This font takes
        the choice, so the phase is written here.
        """

        self.verticalForms()

    def verticalForms(self) -> None:
        """Write the vertical form of every punctuation mark that is drawn with one.

        The vertical form of a mark is the mark turned on its side, drawn as `uXXXX.vert`
        beside `uXXXX` in the source font. The mark is written with that form when the text
        runs vertically, which is what the `vert` feature asks for.

        Noto carries a second feature, `vpal`, whose proportional placements pull the
        vertical forms of the brackets and the quotes onto a common height. This font gives
        every vertical form the margin the horizontal form is drawn with — `VERTICAL_MARGIN`
        at each end of the drawing, by `verticalMargins` — so no proportional placement is
        needed and `vpal` is not written.
        """

        verticalForms = self.verticalFormNames()
        if not verticalForms:
            return
        with self.Lookup("Ib.punctuation.vertical", feature="vert"):
            for name in verticalForms:
                self.sub(name.removesuffix(".vert"), by=name)

    def verticalFormNames(self) -> list[str]:
        """The marks of this font that are drawn with a vertical form.

        A mark is drawn with a vertical form when the source font carries `uXXXX.vert`
        beside it, which is where the drawing of the turned mark is.
        """

        return [name for name in self.glyphs if name.endswith(".vert")]

    def verticalMargins(self, font: Font) -> None:
        """Give each vertical form a margin of `VERTICAL_MARGIN` at both ends of its drawing.

        The marks are drawn with 100 units of space above and below, which is the margin the
        horizontal forms carry on their sides, so a vertical form is moved to start that far
        above the baseline and its advance is set to the drawing plus the margin at each end.
        The drawing itself is left as it is: the margin is what the layout reads, and it is
        applied to the composed font rather than to the source font.
        """

        for name in self.verticalFormNames():
            glyph = font[name]
            points = [point for contour in glyph.contours for point in contour.points]
            yMin = min((point.y for point in points), default=0)
            yMax = max((point.y for point in points), default=0)
            height = yMax - yMin
            if not height:
                continue  # a vertical form with no drawing has no margin to be given
            glyph.move((0, VERTICAL_MARGIN - yMin))
            glyph.width = height + 2 * VERTICAL_MARGIN

    def iib4(self) -> None:
        """**Phase IIb.4: Stretching the stem where a bow is followed by an extending form**

        The library leaves Phase IIb.4 empty: whether a font stretches the stem at all, and
        which written forms it stretches it between, is a choice a font makes. This font
        takes the choice, so the phase is written here.

        A written form drawn with a bow leaves a stem to the written form that follows it,
        and the stem is stretched with the nirugu where that written form extends. The nirugu
        is the stem extender of the script, and carrying the stretching out in the font keeps
        the user from inserting U+180A by hand, which is how it is otherwise done.

        The inserted segment draws the same stem as the nirugu control does, but as a base of
        its own, so that the extended written form still joins the bow.
        """

        bowed = self.bowedWrittens()
        if not bowed:
            return

        self.spec.newGlyphs["nirugu.extend"] = GlyphSpec([self.glyphNameProcessor("nirugu")])
        self.spec.openTypeCategories["nirugu.extend"] = "base"

        # The action of the treatment: the written form keeps its drawing and takes the
        # extending stem after it.
        with self.Lookup("_.nirugu.extending") as extending:
            for name in BOWED_EXTENSIONS:
                self.sub(name, by=[name, "nirugu.extend"])

        with self.Lookup("IIb.nirugu.extending", feature="rclt", flags={"IgnoreMarks": True}):
            extendingClass = self.namedGlyphClass("IIb.extending", EXTENDING)
            bowedClass = self.namedGlyphClass("IIb.bowed", bowed)
            self.sub(self.input(bowedClass, extending), extendingClass, by=None)
            self.sub(self.input("u1821.A.init", extending), by=None)
            if q := self.qWrittens():
                vowels = self.vowelWrittens()
                self.sub(self.input(self.namedGlyphClass("IIb.q", q), extending), vowels, by=None)

    def bowedWrittens(self) -> list:
        """The bowed written forms of every targeted writing system.

        The treatment acts on written units that every writing system shares, so each
        writing system contributes the written forms of the letters it draws with a bow.
        """

        members = list()
        for locale in self.locales:
            aliases = getAliasesByLocale(locale)
            for alias in BOWED:
                if alias in aliases:
                    members.append(self.classes[f"{locale}-{alias}"])
            # `G` is a written unit rather than a letter, so it comes as a list of names.
            members.extend(self.writtens(locale, ["G", "Gx"]).glyphSet())
        return members

    def qWrittens(self) -> list:
        """The written forms of the Ali Gali letter _q_, which the bows join."""

        for locale in self.locales:
            if "qX" in getAliasesByLocale(locale):
                return [self.classes[f"{locale}-qX"]]
        return []

    def vowelWrittens(self):
        """The vowel written forms that an extended written form stands before."""

        return self.glyphClass(
            self.classes[f"{locale}-{alias}"]
            for locale, aliases in VOWELS.items()
            if locale in self.locales
            for alias in aliases
        )

    def spliceLvsWrittenForms(self) -> None:
        """Draw each written form of a long vowel sign that the source font does not draw.

        The sign is written as one written form with the letter it follows, and that written
        form is what the ligature glyph of the sign is built from — `_BALv.init` draws
        `u184B_u1820_u1843.BALv.init`. A source font draws the written forms of the vowels
        and leaves the rest to the font maker, so a written form the font does not carry is
        drawn here from the written forms the letter and the sign are drawn with.

        A written form may be built from another drawn one — `_BAaLv.isol` draws `_AaLv.fina`
        — so the written forms are drawn in passes until none is left to draw.

        How the written form of a letter and the sign is drawn is a choice this font makes,
        which `LVS_FORMS` spells out, so the code lives here rather than in the library.
        """

        todo = self.lvsWrittenForms()
        drawn = set[str]()
        while todo:
            drawnNow = {
                name
                for name, members in todo.items()
                if all(i in self.glyphs or i in drawn for i in members)
            }
            if not drawnNow:
                break  # what is left is built from written forms that are nowhere to be drawn
            for name in drawnNow:
                self.spec.newGlyphs[self.glyphNameProcessor(name)] = GlyphSpec(
                    [self.glyphNameProcessor(i) for i in todo[name]]
                )
                del todo[name]
            drawn |= drawnNow

    def lvsWrittenForms(self) -> dict[str, list[str]]:
        """Each written form of a long vowel sign that the source font does not draw.

        The written forms are the ones the ligature table builds glyphs from: every ligature
        that carries the sign — `BALv`, `AOLv` — names a written form with the sign, and
        that written form is what the ligature glyph of the sign is built from. A written
        form the font carries is kept as it is, and only the missing ones are drawn, each as
        the written form of the letter and the drawing of the sign that `lvsFormMembers`
        reads off the written form and the joining position.
        """

        forms = dict[str, list[str]]()
        for name in sorted(self.lvsWrittenFormNames()):
            if name in self.glyphs or name in forms or name in self.spec.newGlyphs:
                continue  # the font draws this written form; it is kept as it is
            if members := self.lvsFormMembers(name, forms):
                forms[name] = members
        return forms

    def lvsWrittenFormNames(self) -> Iterator[str]:
        """The written forms with the sign that the font has to carry.

        The ligature table names the written form of every letter and sign, and the written
        forms the sign is written with read off the letters that carry it. The written form
        of a letter that carries the sign on its own is read off the letters as well, and
        the rules of `LVS_FORMS` name the written forms the consonants fill in.
        """

        yield from self.lvsWrittenFormsOfLetters()
        for rule, positions in LVS_FORMS:
            if "{C}" in rule:
                continue  # the written forms of this rule are named by the consonants
            for position in positions:
                yield f"_{rule}Lv.{position}"
        for table in data.ligatures.values():
            for name, positions in table.items():
                if not name.endswith("Lv"):
                    continue
                for position in positions:
                    yield f"_{name}.{position}"

    def lvsWrittenFormsOfLetters(self) -> Iterator[str]:
        """The written form of each letter of every writing system the sign is written with.

        The sign follows a letter that is drawn with a written form that carries it, which
        the data marks, and the written form of the two is the written units of the letter
        and the sign at the joining position the letter is drawn in.
        """

        for locale in ["TOD", "TODx"]:
            if locale not in self.locales:
                continue
            for charName, position, variant in lvsVariants(locale):
                written = GlyphDescriptor.fromData(charName, position, variant)
                yield str(GlyphDescriptor([], written.units + ["Lv"], written.position))

    def lvsFormMembers(self, name: str, forms: dict[str, list[str]]) -> list[str]:
        """The drawings a written form of the sign is drawn from.

        The written form of the sign is drawn as the written form of the letter followed by
        the sign, and the sign is drawn by the written unit of the joining position the
        written form ends at. A letter whose written form is drawn as one shape of its own —
        `Aa`, `Iy` — takes the mark the shape is closed with instead, drawn before the shape
        so that the two share the origin of the written form.

        The drawings are the ones the font carries or the ones another written form of this
        table draws, so a written form whose members are only drawn by a later pass is
        listed as well and is resolved as the passes go.
        """

        written = GlyphDescriptor.parse(name)
        units = written.units[:-1]  # the sign is the last written unit
        rules = sorted(LVS_FORMS, key=lambda i: len(i[0].replace("{C}", "")), reverse=True)
        for rule, positions in rules:
            consonant = lvsRuleConsonant(units, rule)
            if consonant is None:
                continue
            memberNames = positions.get(written.position)
            if not memberNames:
                continue
            return [i.replace("{C}", consonant) for i in memberNames]
        return []


def lvsRuleConsonant(units: list[str], rule: str) -> str | None:
    """The consonant of the written form that *rule* answers, or None if it answers none.

    A rule that carries `{C}` answers the written forms that end with the written units of
    the rule, whatever consonant they begin with — `{C}Ob` answers `BOb` and `GOb` alike —
    and the consonant is the written units before that ending.
    """

    written = "".join(units)
    if "{C}" not in rule:
        return "" if written == rule else None
    ending = rule.replace("{C}", "")
    if not written.endswith(ending):
        return None
    return written.removesuffix(ending) or None


def composeUnified(locales: list[LocaleID] = [*data.locales]) -> Font:
    """Compose the unified source font, targeting *locales* (every writing system)."""

    font = Font.open(SOURCE)
    # The names the source font carries are taken before the composition adds to them:
    # a glyph the source font draws is not a generated one.
    sourceNames = frozenset(font.keys())
    composer = UnifiedMongFeaComposer(
        cmap={j: i for i in font.keys() for j in font[i].unicodes},
        glyphs=[*font.keys()],
        locales=locales,
    )
    spec = composer.compose()
    applySpecToFont(spec, font)
    composer.verticalMargins(font)
    markGeneratedGlyphs(font, composer, spec, sourceNames)
    font.features.text = composer.asFeatureFile().asFea()
    return font


# The colours the composed font marks a generated glyph with, by the kind of glyph it is.
# A UFO colour is an RGBA list held as the comma-separated string the format prescribes.
#
# A font maker reads the marks as the work the composed font still owes: a glyph of the
# source font is drawn, a written unit and its ligatures are built from the source font and
# want checking, and a glyph with a code point or a variant of one is built by the composer
# and wants drawing.
WRITTEN_UNIT_MARK_COLOR = "0.75,0.75,0.75,1"  # light grey
COMPOSED_MARK_COLOR = "0.45,0.45,0.45,1"  # dark grey


def markGeneratedGlyphs(
    font: Font,
    composer: UnifiedMongFeaComposer,
    spec: FontSpec,
    sourceNames: frozenset[str],
) -> None:
    """Mark every glyph the composed font generates, in the colour its kind calls for.

    The composed font is not the source font: what the source font draws is kept, and
    everything else is built by the two steps of the composition.

    - A glyph the source font draws is left unmarked.
    - A written unit, and a ligature of written units, is built from the drawings the
      source font carries — `I4` from `I`, `WpA` from `Wp` and `A`, the written forms of
      the long vowel sign from the written form and the sign — so it is marked in light
      grey, as a drawing that is there to be checked.
    - A glyph the composer builds for a character or one of its variants is built from the
      written units alone and carries a code point, so it is marked in dark grey, as a
      drawing that is not there yet.

    The kind is read off the glyph name, which is the only thing that tells the two apart:
    a name with a code point is a character or a variant of one, and a name without one is
    a written unit or a ligature of written units.
    """

    for name in spec.newGlyphs:
        if name in sourceNames:
            continue
        font[name].lib["public.markColor"] = (
            COMPOSED_MARK_COLOR if hasCodePoint(name) else WRITTEN_UNIT_MARK_COLOR
        )


def hasCodePoint(name: str) -> bool:
    """Whether a glyph name names a character or a variant of one.

    The composer names a character's glyph `uXXXX`, and a variant of it `uXXXX.…` or
    `uXXXX_uXXXX.…` — the code points that drew the variant, then the written form. A
    written unit has no code point: it is shared between the characters that write with it.

    >>> hasCodePoint("u1820")
    True
    >>> hasCodePoint("u1820_u1843.AALv.isol")
    True
    >>> hasCodePoint("_BALv.init")
    False
    >>> hasCodePoint("I4")
    False
    """

    return bool(reMatch(r"_?u[0-9A-F]{4,6}(?:_u[0-9A-F]{4,6})*(\.|$)", name))


@pytest.fixture(scope="session")
def unifiedFont() -> Path:
    """The unified font, composed once for the whole session.

    Composing the font and compiling it takes a while, so the whole session shares one
    build; the composed UFO and OTF are left in ``temp/``.
    """

    print("composing the unified font …", flush=True)
    font = composeUnified()
    tempDir.mkdir(parents=True, exist_ok=True)
    print(f"  composed {len(font)} glyphs, writing the UFO …", flush=True)
    font.save(composedUFO, overwrite=True)
    print("  compiled the UFO, compiling the OTF …", flush=True)
    compileOTF(font).save(composedOTF)
    print(f"composed {composedOTF}", flush=True)
    return composedOTF


def test_unified(unifiedFont: Path) -> None:
    assert composedUFO.exists() and unifiedFont.exists()


# A case of the suites: the index, the letters, the locale and what they shape to, or the
# same, parametrized, with the marks made on it.
Case = tuple[str, str, str, str] | ParameterSet


@cache
def languageOf(tag: str) -> str:
    """The language string that selects the OpenType language system *tag*."""

    return hb.ot_tag_to_language(tag)  # type: ignore


def caseValues(case: Case) -> tuple[str, str, str, str]:
    """The index, letters, locale and goal of *case*.

    A case is a plain tuple, or a parametrized case that carries the marks made on it.
    """

    return tuple(case.values) if isinstance(case, ParameterSet) else case  # type: ignore


def caseMarks(case: Case) -> list:
    """The marks made on *case*, which a plain tuple carries none of."""

    return [*case.marks] if isinstance(case, ParameterSet) else []


def caseIsXfail(case: Case) -> bool:
    """Whether *case* is one the suites expect the font to answer differently."""

    return any(mark.name == "xfail" for mark in caseMarks(case))


def conformanceCases() -> list:
    """The cases of the suites, marked where the unified font answers differently.

    The EAC suite settles the cases below by one writing system alone, and another writing
    system that shares the character answers them differently, so the font that writes with
    every writing system at once is the one that has to be marked; a font that writes with
    one of them answers them as the suite expects.
    """

    cases = list()
    for case in loadRawTestCases(TEST_SUITES, "MNG"):
        values = caseValues(case)
        marks = caseMarks(case)
        if reason := EAC_UNIFIED_XFAIL.get(values[0]):
            marks.append(pytest.mark.xfail(reason=reason))
        cases.append(pytest.param(*values, marks=marks) if marks else case)
    return cases


def caseIndexes(cases: list) -> Iterator[str]:
    """The `‹suite› > ‹index›` name of every case of *cases*."""

    for case in cases:
        yield caseValues(case)[0]


# The cases of the suites, and how far a run of them has come. There are thousands of
# cases and each one is shaped against the composed font, so the console is told where the
# run is; run pytest with `-s` to see it.
CASES = conformanceCases()
doneCases = Counter[str]()
totalCases = Counter[str](index.split(" > ")[0] for index in caseIndexes(CASES))


def report(index: str, result: str) -> None:
    """Tell the console where the run of the suites has come."""

    suite, name = index.split(" > ", 1)
    doneCases[suite] += 1
    print(f"{suite} {doneCases[suite]}/{totalCases[suite]} {name}: {result}", flush=True)


@pytest.mark.parametrize(
    ("index", "letters", "locale", "goal"),
    CASES,
)
def test_conformance(
    index: str,
    letters: str,
    locale: str,
    goal: str,
    unifiedFont: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    parsedText = parseLetter(letters, locale)
    codes = parseAliases(parsedText, locale)
    result = parseWrittenUnits(parsedText, unifiedFont, languageOf(LANGUAGE[locale]))
    with capsys.disabled():
        report(index, "ok" if result == goal else "failed")
    assert result == goal, f"ind:  {index}\ncode: {codes}\nres:  {result}\ngoal: {goal}"

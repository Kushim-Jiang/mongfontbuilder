"""Compose the unified source font.

``tests/unified.ufo`` carries the written units of every writing system at once, so the
whole block composes from a single source font. This module builds that font for all
writing systems and leaves the composed UFO and OTF in ``temp/`` for inspection:

    uv run pytest tests/test_unified.py -s

The build on its own, without the suites, is ``tests/build.py``.
"""

from collections import Counter
from collections.abc import Iterator
from functools import cache
from pathlib import Path
from re import match as reMatch

import pytest
import uharfbuzz as hb
from _pytest.mark.structures import ParameterSet
from fontTools.feaLib import ast
from ufoLib2 import Font
from ufoLib2.objects import Glyph

from fixtures import EAC_UNIFIED_XFAIL, compileOTF, loadRawTestCases
from mongfontbuilder import GlyphDescriptor, data
from mongfontbuilder.data.types import LocaleID
from mongfontbuilder.otl import MongFeaComposer
from mongfontbuilder.otl.iii import lvsVariants
from mongfontbuilder.spec import FontSpec, GlyphSpec, applySpecToFont
from mongfontbuilder.utils import getAliasesByLocale
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

# The margin the punctuation marks are drawn with, at each end of the drawing: a mark is
# drawn with this much space before it and after it, and its vertical form is drawn with the
# same margin at each end of it. A vertical form is read along the line, which is the
# direction its advance is taken in, so the margin of a vertical form is taken along y. The
# margin is what `verticalProportions` gives a vertical form through `vpal`.
VERTICAL_MARGIN = 100

# The height of the line a vertical form is read in, and so the vertical advance of every
# vertical form and the `vhea` of the font. It is the sum of the `openTypeVheaVertTypoAscender`
# and `openTypeVheaVertTypoDescender` of the source font, which the fontinfo declares as
# 500 and -500: a vertical form of this font is read in a box of 1000 along the line, not in
# the 1226 the horizontal line takes from the ascender to the descender of the font.
#
# A glyph is given this height through `vmtx`, which is what tells the layout that the
# glyph has a vertical advance of its own. Without it the layout synthesizes a vertical
# origin for the glyph, places the glyph by that origin rather than by the line, and the
# margin a vertical form is drawn with is not the margin it is read with.
VERTICAL_HEIGHT = 1000

# The marks that are drawn over the written form they follow rather than beside it, which
# `markAnchors` anchors at the origin so that they stay where they were drawn, and the
# writing systems that write with them. Hudum and Manchu write with them, and so do their
# Ali Gali extensions; a mark of another writing system is not anchored, because whether a
# mark is written over a written form is a choice each writing system makes.
MARK_GLYPHS = ["u1885", "u1886", "u18A9"]
MARK_LOCALES: list[LocaleID] = ["MNG", "MNGx", "MCH", "MCHx"]
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


def inkBox(glyph: Glyph) -> tuple[float, float, float, float]:
    """The box the drawing of *glyph* fills, as the least and most of x and of y.

    The box is read off the points of the drawing rather than from the outline, which is what
    the drawings of this font are drawn and positioned by. A glyph that draws nothing fills a
    box with no sides.
    """

    points = [point for contour in glyph.contours for point in contour.points]
    if not points:
        return 0, 0, 0, 0
    x = [point.x for point in points]
    y = [point.y for point in points]
    return min(x), min(y), max(x), max(y)


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
        self.iib4()
        return spec

    def composeVerticalForms(self) -> None:
        """Write the vertical forms of the punctuation marks, which Phase Ib leaves open.

        The library leaves Phase Ib empty: whether a font writes a punctuation mark with a
        vertical form, and how that form is drawn, is a choice a font makes. This font takes
        the choice, so the phase is written here.
        """

        self.verticalForms()

    def markAnchors(self, font: Font) -> None:
        """Anchor every mark of the font at the origin, and every written form under it.

        This is written after the composition rather than during it, because the bases are
        the glyphs that carry an advance and the advance is only settled once the spec is
        applied. Writing it twice is not possible either: the mark class is declared with the
        definition, and a second declaration of the same class is rejected.

        The marks `baluda`, `tribaluda` and `dagalga` are drawn over the written form they
        follow rather than beside it, so both the mark and the written form are anchored at
        the origin and the mark stays where it was drawn.

        The written form is what is positioned, so the lookup has to hold every written form
        a mark can follow. `markAnchorBases` names them.
        """

        markNames = [self.glyphNameProcessor(i) for i in MARK_GLYPHS if i in self.glyphs]
        if not markNames:
            return
        bases = self.markAnchorBases(font)
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

    def markAnchorBases(self, font: Font) -> list[str]:
        """The glyphs a mark of this font can be drawn over.

        A mark is drawn over the written form it follows, and it is the written form that is
        positioned against the mark: the layout looks the base of the mark up in the lookup,
        and a written form the lookup does not hold leaves the mark unpositioned. An
        unpositioned mark is not left where it was drawn — the pen has already passed it —
        so the mark is flung past the written form it belongs over rather than drawn on it.

        The set is therefore every glyph a mark can follow, which is every glyph of the font
        that is not itself a mark. Whether a glyph is a mark is what its advance says: a mark
        carries no advance of its own, and a glyph that carries one is a written form, a
        ligature, or a control that stands where a written form does. That is what keeps the
        set complete — a mark is written over the ligatures and the localized written forms
        as well as over the plain ones, and over the dotted circle that stands in for a
        written form written with no letter around it — where naming the written forms of
        the writing systems the marks belong to left the ligatures out and flung the mark
        past them.

        The glyphs are read off *font* rather than off `self.glyphs`, because the ligatures
        and the localized written forms are built by the composition and are not in the
        source font the composer was given.
        """

        return sorted(name for name in font.keys() if font[name].width)

    def verticalForms(self) -> None:
        """Write the vertical form of every punctuation mark that is drawn with one.

        The vertical form of a mark is the mark turned on its side, drawn as `uXXXX.vert`
        beside `uXXXX` in the source font. The mark is written with that form when the text
        runs vertically, which is what the `vert` feature asks for.

        Noto carries a second feature, `vpal`, whose proportional placements pull the
        vertical forms of the brackets and the quotes onto a common length. This font gives
        most of its vertical forms the margin the horizontal form is drawn with —
        `VERTICAL_MARGIN` at each end of the drawing, by `verticalProportions` — and leaves
        the forms that are read at the edge of the line in the box of the line, which
        `NO_VPAL` holds, so `vpal` is written here.
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

    def verticalProportions(self, font: Font) -> None:
        """**Write `vpal`: the box of a vertical form is its drawing plus the margin**

        A drawing is read along the line, and a vertical form is read along the line by its y
        axis, which is the direction the layout takes its advance in. A font that gives a
        glyph no vertical advance of its own gives every glyph the height of the line — from
        the ascender to the descender — and the source font draws each vertical form in that
        box, wherever in it the mark belongs.

        A vertical form is given `VERTICAL_HEIGHT` as its height first, which is what makes
        the font carry `vmtx` at all: a glyph whose height is set has a vertical advance of
        its own, and the layout then reads the glyph by the line the font gives it rather
        than by a vertical origin it synthesizes. The synthesized origin is what a reading
        is otherwise placed by, and it is taken across the line from the width of the glyph
        rather than from the drawing, so a vertical form read without `vmtx` does not keep
        the margin it is drawn with. The height is the same for every form, so `vhea` is
        written once and every vertical form shares the line.

        A horizontal form of this font is drawn with the margin the mark is read with: its
        ink runs from `VERTICAL_MARGIN` to the advance less `VERTICAL_MARGIN`, so the mark is
        read with the same margin before it and after it and nothing else. A vertical form is
        the same mark turned onto the line, so it is read with that same margin at each end
        of it along the line. The advance of a vertical form is therefore set to its drawing
        plus `VERTICAL_MARGIN` at each end of it, and the drawing is moved so that it sits
        `VERTICAL_MARGIN` from the start of that advance.

        Both are proportional placements: values the layout reads rather than ink on the
        glyph. The drawing is what the source font drew, and the placement is what `vpal` is
        for; the advance a glyph of this font is looked up with is the height of the line, so
        the placement is what the advance of the form is read as.

        The placement is written for the default script as well as for the Mongolian one.
        A layout reads the placement of the script its text is written with, and only the
        writing systems of this font are registered under `mong`; a layout that resolves
        its text to another script — or to no script at all — reads `DFLT`, and a `vpal`
        of the Mongolian script alone would be a placement that layout never reads. The
        box of a vertical form is a property of the form itself, so it is written once for
        every layout that reads the font.
        """

        verticalForms = self.verticalFormNames()
        if not verticalForms:
            return
        for name in verticalForms:
            font[name].height = VERTICAL_HEIGHT
        # The placement of a vertical form is read from the top of the horizontal line, so
        # the font has to declare that line. The vertical line is the one the fontinfo
        # declares through the vhea metrics, which is `VERTICAL_HEIGHT`, not the ascender to
        # the descender of the horizontal line.
        ascender = font.info.ascender
        assert ascender is not None
        with self.Lookup(
            "Ib.punctuation.proportions",
            feature="vpal",
            languageSystems={"DFLT": {"dflt"}, **self.languageSystems},
        ):
            for name in verticalForms:
                ink = inkBox(font[name])
                drawing = ink[3] - ink[1]
                if not drawing:
                    continue  # a vertical form with no drawing has no box to be given
                box = drawing + 2 * VERTICAL_MARGIN
                self.current.append(
                    ast.SinglePosStatement(
                        [
                            (
                                ast.GlyphName(self.glyphNameProcessor(name)),
                                ast.ValueRecord(
                                    yPlacement=int(ascender - VERTICAL_MARGIN - ink[3]),
                                    yAdvance=box - VERTICAL_HEIGHT,
                                ),
                            )
                        ],
                        [],
                        [],
                        False,
                    )
                )

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

        members = []
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
                yield str(GlyphDescriptor([], [*written.units, "Lv"], written.position))

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


def composeUnified(locales: list[LocaleID] | None = None) -> Font:
    """Compose the unified source font, targeting *locales* (every writing system)."""

    if locales is None:
        locales = [*data.locales]
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
    # The marks are positioned against every glyph of the font that carries an advance, and a
    # glyph the composition built knows its advance only once the spec is applied, so the
    # lookup is written here rather than during the composition.
    composer.markAnchors(font)
    composer.verticalProportions(font)
    markGeneratedGlyphs(font, composer, spec, sourceNames)
    font.features.text = composer.asFeatureFile().asFea()
    return font


def buildUnifiedFont() -> Path:
    """Compose the unified font and write the composed UFO and OTF to ``temp/``.

    The suites compose the font on the way to shaping it, which is a run of thousands of
    cases; this is the build by itself, which ``tests/build.py`` and ``tests/failures.py``
    are run for.
    """

    print("composing the unified font …", flush=True)
    font = composeUnified()
    tempDir.mkdir(parents=True, exist_ok=True)
    print(f"  composed {len(font)} glyphs, writing the UFO …", flush=True)
    font.save(composedUFO, overwrite=True)
    print("  wrote the UFO, compiling the OTF …", flush=True)
    compileOTF(font).save(composedOTF)
    print(f"composed {composedOTF}", flush=True)
    return composedOTF


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

    return buildUnifiedFont()


def test_unified(unifiedFont: Path) -> None:
    assert composedUFO.exists()
    assert unifiedFont.exists()


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

    cases = []
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

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

import pytest
import uharfbuzz as hb
from _pytest.mark.structures import ParameterSet
from ufoLib2 import Font

from fixtures import compileOTF, loadRawTestCases
from mongfontbuilder import GlyphDescriptor, data
from mongfontbuilder.data.types import LocaleID
from mongfontbuilder.otl import MongFeaComposer
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

# The EAC suite settles an FVS by the Hudum standard alone, which calls a sequence after a
# letter invalid there. In the unified font the same character is valid in the writing
# systems that share it, so the sequence is not invalid, and the written form the suite
# expects of an invalid FVS does not follow.
XFAIL = {
    "eac-hud > MND11-2",
    "eac-hud > MNS11-26",
    "eac-hud > MNZ11-3",
    "eac-hud > MNZ21-5",
    "eac-hud > MNM10-2",
    "eac-hud > MNM11-2",
    "eac-hud > XIM11-11",
    "eac-hud > XIM11-675",
    "eac-hud > XIM11-678",
    "eac-hud > XIM11-681",
    "eac-hud > XIM11-684",
    "eac-hud > XIM11-687",
    "eac-hud > XIM11-690",
    "eac-hud > XIM11-694",
}

# Written forms that a bowed written form leaves a stem to: the medial and final forms
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
    "u182E.M.fina",
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

# The written forms that are drawn with a stem of their own, and so are the ones that
# the preceding bowed written form leaves that stem to. Read off the same file.
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

# The Ali Gali vowel written forms, and the ligature of the long vowel sign with _a_.
VOWELS = {"MNG": ["a", "ue", "ee", "o"], "MNGx": ["a", "iX", "ue", "ee", "o"]}

# The writing systems that draw the final form of the letter _m_ with a large tail.
LARGE_TAIL = ["SIB", "MCH"]

# The written forms of a long vowel sign are not drawn in the source font. Each keeps the
# drawing of the written form it extends and takes the sign after it — as the mark the
# sign is drawn with, or as the written unit of the joining position the form ends at.
#
# A written form of a consonant is keyed by the written units the sign follows, whose
# leading consonant is filled in for `{C}`: `_BELv.isol` is built from `_BE.isol` and the
# mark, and `_BhOLv.isol` from `_BhO.init` and the written unit of the sign.
LVS_FORMS: list[tuple[str, dict[str, list[str]]]] = [
    # A written form of its own: the mark comes before the drawing it closes, so that the
    # two drawings share the origin of the written form.
    ("Aa", {"fina": ["_Lv.mark", "_Aa.fina"]}),
    ("Iy", {"fina": ["_Lv.mark", "_Iy.fina"]}),
    # The written unit of the sign itself, after the written form it ends.
    (
        "O",
        {
            "medi": ["_O.medi", "_Lv.medi"],
            "fina": ["_O.medi", "_Lv.fina"],
        },
    ),
    # No drawing of its own: the written forms it is built from.
    (
        "AO",
        {
            "isol": ["_A.init", "_O.medi", "_Lv.fina"],
            "init": ["_A.init", "_O.medi", "_Lv.medi"],
        },
    ),
    # The same written forms after a consonant, whose leading written unit `{C}` is the
    # consonant of the form.
    (
        "{C}A",
        {
            "init": ["_{C}A.init", "_Lv.mark"],
            "medi": ["_{C}A.medi", "_Lv.mark"],
        },
    ),
    (
        "{C}Aa",
        {
            "isol": ["_{C}A.init", "_AaLv.fina"],
            "fina": ["_{C}A.medi", "_AaLv.fina"],
        },
    ),
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
]


class UnifiedMongFeaComposer(MongFeaComposer):
    """A composer with the optional treatments of phase IIb.3.

    The library leaves IIb.3 open: its treatments are choices a font makes, and the
    per-writing-system fonts stay as they are by not taking them. The unified font takes
    them, so the code lives here rather than in the library.
    """

    def compose(self) -> FontSpec:
        spec = super().compose()
        self.iib3()
        return spec

    def iib3(self) -> None:
        """
        **Phase IIb.3: Optional treatments**

        (1) Extend the stem with the nirugu where a bowed written form is followed by an
        extending one, so that the vowel does not touch the bow.

        (2) Give Sibe and Manchu the final form of the letter _m_ that they write, which
        the cross-writing-system default of the character does not carry.

        Both treatments run on written units that every writing system shares, so neither
        is restricted to a language system, except for (2), whose whole point is the
        difference between the writing systems.
        """

        self.niruguExtending()
        self.loclMFina()

    def niruguExtending(self) -> None:
        """Stretch the stem between a bow and the extending written form after it.

        The nirugu is the stem extender of the script. Carrying the stretching out in
        the font keeps the user from inserting U+180A, which is how it is done by hand.
        The inserted segment draws the same stem as the nirugu control does, but as a
        base of its own, so that the extended written form still joins the bow.
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

        with self.Lookup(
            "IIb.nirugu.extending",
            feature="rclt",
            flags={"IgnoreMarks": True},
        ):
            extendingClass = self.namedGlyphClass("IIb.extending", EXTENDING)
            bowedClass = self.namedGlyphClass("IIb.bowed", bowed)
            self.sub(self.input(bowedClass, extending), extendingClass, by=None)
            self.sub(self.input("u1821.A.init", extending), by=None)
            if q := self.qWrittens():
                vowels = self.vowelWrittens()
                self.sub(self.input(self.namedGlyphClass("IIb.q", q), extending), vowels, by=None)

    def loclMFina(self) -> None:
        """Give the writing systems with a large-tailed _m_ the final form they write.

        The character has one final form across the writing systems it is shared by, so
        the font keeps the Hudum design as the default one and localizes it here.

        The localized form runs in `rclt` rather than in `locl`: an engine applies `locl`
        before cursive joining, when the character is still its bare glyph, so the
        written unit to replace does not exist yet.
        """

        if not (languages := [i for i in LARGE_TAIL if i in self.locales]):
            return
        # The language system of a writing system is named after it, padded to four
        # characters, as the OpenType script/language tags are.
        tags = {i for i in self.languageSystems["mong"] if i.strip() in languages}
        with self.Lookup(
            "IIb.localized.M.fina",
            feature="rclt",
            languageSystems={"mong": tags},
        ):
            self.sub("u182E.M.fina", by="u182E.M3.fina")

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

    def lvsForms(self, font: Font) -> None:
        """Draw the written forms of a long vowel sign, which the library leaves empty.

        A written form with the sign is never drawn into the source font: the library
        builds the variant glyphs of the sign as components of the written form the sign
        follows — `u1849_u1843.OLv.init` of `_OLv.init`, say — and leaves that written
        form for the font maker to draw. The drawing is the written form it extends plus
        the sign itself, which `LVS_FORMS` spells out per written form and position.

        The source font has to be at hand because Noto draws some of these written forms
        already: a form that has a drawing keeps it.
        """

        forms = dict[str, list[str]]()
        variants = dict[str, str]()
        for key, definition in self.classes.items():
            if "_lvs." not in key:
                continue
            for glyph in definition.glyphSet():
                variant = GlyphDescriptor.parse(glyph.glyph)  # type: ignore
                name = str(replace(variant, codePoints=[]))
                if name in font and (font[name].contours or font[name].components):
                    continue  # Noto draws this written form; the library already draws with it
                variants[glyph.glyph] = name  # type: ignore
                units = "".join(variant.units).removesuffix("Lv")
                if members := self.lvsMembers(units, variant.position):
                    forms[name] = members

        # A written form that another one is built from comes first, so that the source
        # glyph is there when the component is resolved.
        created = set[str]()
        for name in sorted(forms, key=lambda i: any(j in forms for j in forms[i])):
            if all(i in self.glyphs or i in created for i in forms[name]):
                self.spec.newGlyphs[name] = GlyphSpec(forms[name])
                created.add(name)

        # The library left the variant glyph of the sign empty, because the source font
        # does not carry the written form the sign follows; the variant is drawn with the
        # written form created above instead, and specified after it.
        for variantName, name in variants.items():
            glyphSpec = self.spec.newGlyphs.get(variantName)
            if glyphSpec is not None and not glyphSpec.components and name in created:
                del self.spec.newGlyphs[variantName]
                self.spec.newGlyphs[variantName] = GlyphSpec([name])

        # A glyph built from a written form created above has to be specified after it,
        # and the library may have specified it before.
        for name, glyphSpec in [*self.spec.newGlyphs.items()]:
            if any(i in created for i in glyphSpec.components):
                del self.spec.newGlyphs[name]
                self.spec.newGlyphs[name] = glyphSpec

    def lvsMembers(self, units: str, position: str) -> list[str]:
        """The drawings a written form of a long vowel sign is built from."""

        for form, positions in LVS_FORMS:
            if "{C}" not in form:
                if form == units:
                    return positions.get(position, [])
                continue
            suffix = form.replace("{C}", "")
            consonant = units.removesuffix(suffix)
            if consonant and consonant != units and units.endswith(suffix):
                return [i.replace("{C}", consonant) for i in positions.get(position, [])]
        return []


def composeUnified(locales: list[LocaleID] = [*data.locales]) -> Font:
    """Compose the unified source font, targeting *locales* (every writing system)."""

    font = Font.open(SOURCE)
    composer = UnifiedMongFeaComposer(
        cmap={j: i for i in font.keys() for j in font[i].unicodes},
        glyphs=[*font.keys()],
        locales=locales,
    )
    spec = composer.compose()
    composer.lvsForms(font)
    applySpecToFont(spec, font)
    font.features.text = composer.asFeatureFile().asFea()
    return font


@pytest.fixture(scope="session")
def unifiedFont() -> Path:
    """The unified font, composed once for the whole session.

    Composing the font and compiling it takes a while, so the whole session shares one
    build; the composed UFO and OTF are left in ``temp/``.
    """

    print("composing the unified font …", flush=True)
    font = composeUnified()
    tempDir.mkdir(parents=True, exist_ok=True)
    font.save(composedUFO, overwrite=True)
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


def conformanceCases() -> list:
    """The cases of the suites, marked where the unified font answers differently."""

    cases = list()
    for case in loadRawTestCases(TEST_SUITES, "MNG"):
        values = caseValues(case)
        marks = caseMarks(case)
        if values[0] in XFAIL:
            marks.append(pytest.mark.xfail(reason="The EAC expects an FVS to be invalid"))
        cases.append(pytest.param(*values, marks=marks) if marks else values)
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

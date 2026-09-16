from collections.abc import Iterable, Iterator

from fontTools.feaLib import ast

from .. import GlyphDescriptor, data, getPosition
from ..data.logic import choosesLvs
from ..data.types import (
    CharacterName,
    JoiningPosition,
    LocaleID,
    ParticleData,
    VariantData,
    fina,
    init,
    isol,
    medi,
)
from ..utils import getCharNameByAlias, getVariants
from . import MongFeaComposer
from .iib import implementLigature

MARKER_MASCULINE, MARKER_FEMININE = "marker.masculine", "marker.feminine"
MARKER_INITIAL = "marker.initial"
MARKER_MASCULINE_FALSE, MARKER_MASCULINE_TRUE = "marker.masculine.false", "marker.masculine.true"

# The position a letter before the Todo long vowel sign takes in the buffer, by the position
# it takes at the end of the word: the long vowel sign joins the letter, so the letter is
# drawn one joining position before the one it ends the word in.
JOINED_BEFORE: dict[JoiningPosition, JoiningPosition] = {isol: init, fina: medi}


def compose(c: MongFeaComposer) -> None:
    iii0(c)
    iii1(c)
    iii2(c)
    iii3(c)
    iii4(c)
    iii5(c)
    iii6(c)
    iii7(c)


def iii0(c: MongFeaComposer) -> None:
    """
    **Phase III.0: Control character preprocessing**
    """

    iii0a(c)
    if "MNG" in c.locales:
        iii0b(c)


def iii0a(c: MongFeaComposer) -> None:
    """
    Before Mongolian-specific shaping steps, nirugu, Todo (Ali Gali) long vowel sign and FVS need to be substituted to ignored glyphs, while MVS needs to be substituted to invalid glyph. ZWNJ and ZWJ also need to be substituted to ignored glyphs to avoid HarfBuzz converting them to zero-width spaces.

    Specifically, for Todo (Ali Gali) long vowel sign, the final long vowel sign closes the word, so the letter before it is drawn in the joining position it takes at the end of a word (from `init` to `isol`, from `medi` to `fina`).
    """

    with c.Lookup("III.controls.preprocessing", feature="rclt"):
        c.sub(
            c.input(
                c.glyphClass(["zwnj", "zwj", "nirugu", c.classes["fvs"]]),
                c.conditions["_.ignored"],
            ),
            by=None,
        )

    with c.Lookup("III.mvs.preserving.A", feature="rclt"):
        c.sub("mvs", by=["mvs.wide", "mvs.wide"])

    with c.Lookup("III.mvs.preserving.B", feature="rclt"):
        c.sub("mvs.wide", "mvs.wide", by="mvs")

    for locale in ["TOD", "TODx"]:
        if locale in c.locales:
            preprocessLvs(c, locale)


def preprocessLvs(c: MongFeaComposer, locale: LocaleID) -> None:
    """Draw each letter that the final Todo long vowel sign follows as it is drawn at the end of a word.

    The long vowel sign joins the letter before it, so the letter holds the joining position
    before the last one — an `init` where it ends the word as an `isol`, a `medi` where it
    ends it as a `fina`. The final long vowel sign closes the word, so the letter is drawn in
    the position it ends a word in, and the FVS lookups of Phase III.6 select the variant of
    that position that the text asks for; `ligateLvs` then draws the letter and the long
    vowel sign as one written form. A long vowel sign that another letter follows is drawn in
    the middle of a word, and the letter before it is drawn in the position it holds.
    """

    lvs = GlyphDescriptor.fromData(getCharNameByAlias("TOD", "lvs"), fina)
    with c.Lookup(f"III.lvs.preprocessing.{locale}", feature="rclt", flags={"IgnoreMarks": True}):
        for charName, position in lvsLetters(locale):
            before = GlyphDescriptor.fromData(charName, JOINED_BEFORE[position])
            after = GlyphDescriptor.fromData(charName, position)
            c.sub(c.input(str(before)), str(lvs), by=str(after))


def ligateLvs(c: MongFeaComposer) -> None:
    """Draw each letter and the final Todo long vowel sign that follows it as one written form.

    The written form that the two make is named by the written form of the letter that the
    long vowel sign is written with — `Ir` and `Lv` are drawn as the written form of `IrLv`
    — and the letter is only drawn with that written form after the FVS lookups of Phase
    III.6 have selected it, so this runs after them and before the ligatures of Phase IIb.1,
    which would draw the letter with the written form that the long vowel sign is a part of.
    """

    lvs = GlyphDescriptor.fromData(getCharNameByAlias("TOD", "lvs"), fina)
    for locale in ["TOD", "TODx"]:
        if locale not in c.locales:
            continue
        with c.Lookup(f"III.lvs.ligature.{locale}", feature="rclt", flags={"IgnoreMarks": True}):
            for charName, position, variant in lvsVariants(locale):
                written = GlyphDescriptor.fromData(charName, position, variant)
                ligature = GlyphDescriptor(
                    [*written.codePoints, *lvs.codePoints],
                    [*written.units, "Lv"],
                    position,
                )
                implementLigature(c, (written, lvs), ligature)


def lvsVariants(locale: LocaleID) -> list[tuple[CharacterName, JoiningPosition, VariantData]]:
    """The written forms of *locale* that a Todo long vowel sign is written with.

    A letter is drawn with such a written form when the long vowel sign follows it, which
    the data marks on the written form; the letter may be drawn with any of its variants
    there, including the one an FVS selects.
    """

    return [
        (charName, position, variant)
        for _alias, charName, position, _fvs, variant in getVariants(locale)
        if choosesLvs(locale, variant)
    ]


def lvsLetters(locale: LocaleID) -> list[tuple[CharacterName, JoiningPosition]]:
    """Every letter of *locale* that a Todo long vowel sign is written with, and the joining
    position it takes at the end of a word there.

    A written form is marked where the long vowel sign draws the letter, and the letter is
    drawn in the position it takes at the end of a word — an `isol` or a `fina`. A marked
    written form of a position that joins both ways asks for no change: the letter is drawn
    with it whether the long vowel sign follows or not.
    """

    return list(
        dict.fromkeys(
            (charName, position)
            for charName, position, _ in lvsVariants(locale)
            if position in JOINED_BEFORE
        )
    )


def iii0b(c: MongFeaComposer) -> None:
    """
    GB requires that the masculinity and femininity of a letter be passed forward and backward indefinitely throughout the word.

    A to C implement masculinity indefinitely passing forward, D to F implement femininity indefinitely passing forward, G to K implement masculinity indefinitely passing backward.
    """

    categories = data.locales["MNG"].categories

    with c.Lookup("III.ig.preprocessing.A", feature="rclt"):
        for alias in categories["vowelMasculine"]:
            for position in (init, medi):
                default = c.getDefault(alias, position)
                c.sub(default, by=[default, MARKER_MASCULINE])

    with c.Lookup(
        "III.ig.preprocessing.B",
        feature="rclt",
        flags={"UseMarkFilteringSet": c.glyphClass([MARKER_MASCULINE])},
    ):
        for alias in categories["vowelNeuter"] + categories["consonant"]:
            for position in (medi, fina):
                default = c.getDefault(alias, position)
                c.sub(MARKER_MASCULINE, c.input(default), by=[default, MARKER_MASCULINE])

    with c.Lookup("III.ig.preprocessing.C", feature="rclt"):
        for alias in (
            categories["vowelMasculine"] + categories["vowelNeuter"] + categories["consonant"]
        ):
            if alias not in ["h", "g"]:
                for position in (init, medi, fina):
                    default = c.getDefault(alias, position)
                    c.sub(default, MARKER_MASCULINE, by=default)

    with c.Lookup("III.ig.preprocessing.D", feature="rclt"):
        for alias in categories["vowelFeminine"]:
            for position in (init, medi):
                default = c.getDefault(alias, position)
                c.sub(default, by=[default, MARKER_FEMININE])

    with c.Lookup(
        "III.ig.preprocessing.E",
        feature="rclt",
        flags={"UseMarkFilteringSet": c.glyphClass([MARKER_FEMININE])},
    ):
        for alias in categories["vowelNeuter"] + categories["consonant"]:
            for position in (medi, fina):
                default = c.getDefault(alias, position)
                c.sub(MARKER_FEMININE, c.input(default), by=[default, MARKER_FEMININE])

    with c.Lookup("III.ig.preprocessing.F", feature="rclt"):
        for alias in (
            categories["vowelFeminine"] + categories["vowelNeuter"] + categories["consonant"]
        ):
            if alias not in ["h", "g"]:
                for position in (init, medi, fina):
                    default = c.getDefault(alias, position)
                    c.sub(default, MARKER_FEMININE, by=default)

    # G': Insert marker.masculine.false after every glyph that participates in gender harmony.
    # This replaces the per-glyph .marked variant system with two marker glyphs.
    allAliases = (
        categories["vowelMasculine"]
        + categories["vowelFeminine"]
        + categories["vowelNeuter"]
        + categories["consonant"]
    )
    passingAliases = (
        categories["vowelMasculine"] + categories["vowelNeuter"] + categories["consonant"]
    )

    with c.Lookup("III.ig.preprocessing.G", feature="rclt", flags={"IgnoreMarks": True}):
        for alias in allAliases:
            for position in (init, medi, fina):
                default = c.getDefault(alias, position)
                c.sub(default, by=[default, MARKER_MASCULINE_FALSE])

    with c.Lookup("III.ig.preprocessing.H", feature="rclt", flags={"IgnoreMarks": True}):
        for alias in categories["vowelMasculine"]:
            for position in (medi, fina, isol):
                default = c.getDefault(alias, position)
                c.sub(default, c.input(MARKER_MASCULINE_FALSE), by=MARKER_MASCULINE_TRUE)

    anyGlyphBetweenMarkers = c.namedGlyphClass(
        "MNG-any_between_markers",
        [
            c.getDefault(alias, position)
            for alias in passingAliases
            for position in (init, medi, fina, isol)
        ]
        + [
            MARKER_MASCULINE_FALSE,
            MARKER_MASCULINE_TRUE,
            MARKER_MASCULINE,
            MARKER_FEMININE,
            c.classes["mvs"],
        ],
    )
    with c.Lookup("III.ig.preprocessing.I.A", feature="rclt", flags={"IgnoreMarks": True}):
        for marker in [
            [c.input(MARKER_MASCULINE_FALSE)],
            [c.input(MARKER_MASCULINE_FALSE), c.classes["fvs"]],
        ]:
            c.sub(*marker, c.classes["mvs"], c.getDefault("a", "isol"), c.classes["fvs"], by=None)
            c.sub(*marker, c.classes["mvs"], c.getDefault("a", "isol"), by=MARKER_MASCULINE_TRUE)
    with c.Lookup("III.ig.preprocessing.I.B", feature="rclt", flags={"IgnoreMarks": True}):
        c.current.append(
            ast.ReverseChainSingleSubstStatement(
                old_prefix=[],
                glyphs=[c._normalized(MARKER_MASCULINE_FALSE)],
                old_suffix=[
                    c._normalized(anyGlyphBetweenMarkers),
                    c._normalized(MARKER_MASCULINE_TRUE),
                ],
                replacements=[c._normalized(MARKER_MASCULINE_TRUE)],
            )
        )
        c.current.append(
            ast.ReverseChainSingleSubstStatement(
                old_prefix=[],
                glyphs=[c._normalized(MARKER_MASCULINE_FALSE)],
                old_suffix=[
                    c._normalized(MARKER_MASCULINE),
                    c._normalized(anyGlyphBetweenMarkers),
                    c._normalized(MARKER_MASCULINE_TRUE),
                ],
                replacements=[c._normalized(MARKER_MASCULINE_TRUE)],
            )
        )

    with c.Lookup("III.ig.preprocessing.J", feature="rclt"):
        for alias in allAliases:
            for position in (init, medi, fina):
                default = c.getDefault(alias, position)
                c.sub(default, MARKER_MASCULINE_FALSE, by=default)

    with c.Lookup("III.ig.preprocessing.K", feature="rclt"):
        for position in (init, medi, fina):
            default = c.getDefault("g", position)
            c.sub(default, c.input(MARKER_MASCULINE_TRUE), by=MARKER_MASCULINE)

    with c.Lookup("III.ig.preprocessing.L", feature="rclt"):
        for alias in [a for a in allAliases if a != "g"]:
            for position in (init, medi, fina):
                default = c.getDefault(alias, position)
                c.sub(default, MARKER_MASCULINE_TRUE, by=default)

    with c.Lookup("III.ig.preprocessing.M", feature="rclt"):
        c.sub(MARKER_MASCULINE, MARKER_MASCULINE, by=MARKER_MASCULINE)
        c.sub(MARKER_MASCULINE, MARKER_FEMININE, by=MARKER_FEMININE)


def iii1(c: MongFeaComposer) -> None:
    """
    **Phase III.1: Phonetic - Chachlag**

    The isolated Hudum _a_, _e_ and Hudum Ali Gali _a_ (same as Hudum _a_) choose `Aa` when follow an MVS, while MVS chooses the narrow space glyph.

    According to GB, when Hudum _a_ and _e_ are followed by FVS, the MVS shaping needs to be postponed to particle lookup, so MVS needs to be reset at this time. For example, for an MVS, an _a_ and an FVS2, in this step should be invalid MVS, isolated default _a_ and ignored FVS2. Since the function of NNBSP is transferred to MVS, this step, although required by GB, is essential, so the lookup name does not have a GB suffix.
    """

    if "MNG" in c.locales:
        aLike = c.variants("MNG", ["a", "e"], isol)
        with c.Lookup("III.a_e.chachlag", feature="rclt", flags={"IgnoreMarks": True}):
            c.sub(
                c.input(c.classes["mvs"], c.conditions["_.narrow"]),
                c.input(aLike, c.conditions["MNG:chachlag"]),
                by=None,
            )

        with c.Lookup(
            "III.a_e.chachlag.GB",
            feature="rclt",
            flags={"UseMarkFilteringSet": c.classes["fvs"]},
        ):
            c.sub(
                c.input(c.classes["mvs"], c.conditions["_.reset"]),
                aLike,
                c.classes["fvs"],
                by=None,
            )


def iii2(c: MongFeaComposer) -> None:
    """
    **Phase III.2: Phonetic - Syllabic**
    """

    iii2a(c)
    iii2b(c)
    iii2c(c)
    iii2d(c)
    iii2e(c)
    iii2f(c)
    iii2g(c)


def iii2a(c: MongFeaComposer) -> None:
    """
    (1) When Hudum _o_ or _u_ or _oe_ or _ue_ follows an initial consonant, apply `marked`.

    According to GB requirements: The `marked` will be skipped if the vowel precedes or follows an FVS, although Hudum _g_ or _h_ with FVS2 or FVS4 will apply `marked` for _oe_ or _ue_; when the first syllable contains a consonant cluster, the `marked` will still be applied.

    (2) When initial Hudum _d_ follows a final vowel, apply `marked`. Appear in Twelve Syllabaries.

    According to GB requirements: The `marked` will be skipped if the vowel precedes or follows an FVS.
    """

    categories = data.locales["MNG"].categories

    if {"MNG", "MNGx", "MCH", "MCHx", "SIB"}.intersection(c.locales):
        with c.Lookup(
            "III.o_u_oe_ue.marked",
            feature="rclt",
            flags={"IgnoreMarks": True},
        ):
            if "MNG" in c.locales:
                c.sub(
                    c.classes["MNG-consonant.init"],
                    c.input(c.variants("MNG", ["o", "u", "oe", "ue"]), c.conditions["MNG:marked"]),
                    by=None,
                )
            if "MNGx" in c.locales:
                c.sub(
                    c.classes["MNGx-consonant.init"],
                    c.input(c.variants("MNGx", ["ue"]), c.conditions["MNGx:marked"]),
                    by=None,
                )
                c.sub(
                    c.classes["MNGx-consonant.init"],
                    c.classes["MNGx-hX"],
                    c.input(c.classes["MNGx-ue"], c.conditions["MNGx:marked"]),
                    by=None,
                )
            for locale in ["SIB", "MCH", "MCHx"]:
                if locale in c.locales:
                    initials = c.classes[f"{locale}-consonant.init"]
                    vowels = c.variants(locale, ["o", "u"])
                    marked = c.input(vowels, c.conditions[f"{locale}:marked"])
                    c.sub(initials, marked, by=None)

    if "MNG" in c.locales:
        # The `marked` that an initial consonant asks for is carried to the vowel that ends
        # the syllable, across the consonants of the cluster between them, so that
        # `k2 l ue` draws the marked `ue` as `k2 l ue` does when the vowel follows the
        # initial consonant alone. GB 25914—2023 requires it.
        with c.Lookup("III.o_u_oe_ue.marked.emit", feature="rclt", flags={"IgnoreMarks": True}):
            for alias in categories["consonant"]:
                default = c.getDefault(alias, "init")
                c.sub(default, by=[default, MARKER_INITIAL])

        with c.Lookup(
            "III.o_u_oe_ue.marked.propagate",
            feature="rclt",
            flags={"UseMarkFilteringSet": c.glyphClass([MARKER_INITIAL])},
        ):
            for alias in categories["consonant"]:
                for position in (medi, fina):
                    default = c.getDefault(alias, position)
                    c.sub(MARKER_INITIAL, c.input(default), by=[default, MARKER_INITIAL])

        with c.Lookup(
            "III.o_u_oe_ue.marked.mark_vowel",
            feature="rclt",
            flags={"UseMarkFilteringSet": c.glyphClass([MARKER_INITIAL])},
        ):
            c.sub(
                MARKER_INITIAL,
                c.input(c.variants("MNG", ["o", "u", "oe", "ue"]), c.conditions["MNG:marked"]),
                by=None,
            )

        with c.Lookup("III.o_u_oe_ue.marked.cleanup", feature="rclt"):
            for alias in categories["consonant"]:
                for position in (init, medi, fina):
                    default = c.getDefault(alias, position)
                    c.sub(default, MARKER_INITIAL, by=default)

        with c.Lookup(
            "III.o_u_oe_ue.marked.GB.A",
            feature="rclt",
            flags={"UseMarkFilteringSet": c.classes["fvs"]},
        ):
            variants = c.variants("MNG", ["o", "u", "oe", "ue"], (medi, fina))
            c.sub(c.input(variants, c.conditions["MNG:reset"]), c.classes["fvs"], by=None)
            variants = c.variants("MNG", ["o", "u", "oe", "ue"], fina)
            c.sub(c.classes["fvs"], c.input(variants, c.conditions["MNG:reset"]), by=None)

        with c.Lookup(
            "III.o_u_oe_ue.marked.GB.B",
            feature="rclt",
            flags={"UseMarkFilteringSet": c.classes["fvs"]},
        ):
            c.sub(
                c.variants("MNG", ["g", "h"], init),
                c.glyphClass([c.classes["fvs2"], c.classes["fvs4"]]),
                c.input(c.variants("MNG", ["oe", "ue"], fina), c.conditions["MNG:marked"]),
                by=None,
            )

        with c.Lookup("III.d.marked", feature="rclt", flags={"IgnoreMarks": True}):
            c.sub(
                c.input(c.classes["MNG-d.init"], c.conditions["MNG:marked"]),
                c.classes["MNG-vowel.fina"],
                by=None,
            )

        with c.Lookup(
            "III.d.marked.GB", feature="rclt", flags={"UseMarkFilteringSet": c.classes["fvs"]}
        ):
            c.sub(
                c.input(c.classes["MNG-d.init"], c.conditions["MNG:reset"]),
                c.classes["MNG-vowel.fina"],
                c.classes["fvs"],
                by=None,
            )
            c.sub(
                c.input(c.classes["MNG-d.init"], c.conditions["MNG:reset"]),
                c.classes["fvs"],
                c.classes["MNG-vowel.fina"],
                by=None,
            )


def iii2b(c: MongFeaComposer) -> None:
    """
    (1) When Sibe _z_ precedes _i_, apply `marked`.

    (2) When Manchu _i_ follows _z_, apply `marked`.

    (3) When Manchu _f_ precedes _i_ or _o_ or _u_ or _ue_, apply `marked`.

    (4) When Manchu Ali Gali _i_ follows _cX_ or _z_ or _jhX_, apply `marked`.
    """

    if {"SIB", "MCH", "MCHx"}.intersection(c.locales):
        with c.Lookup("III.z_f_i.marked.SIB_MCH_MCHx", feature="rclt", flags={"IgnoreMarks": True}):
            if "SIB" in c.locales:
                c.sub(
                    c.input(c.classes["SIB-z"], c.conditions["SIB:marked"]),
                    c.classes["SIB-i"],
                    by=None,
                )
            if "MCH" in c.locales:
                c.sub(
                    c.classes["MCH-z"],
                    c.input(c.classes["MCH-i"], c.conditions["MCH:marked"]),
                    by=None,
                )
                c.sub(
                    c.input(c.classes["MCH-f"], c.conditions["MCH:marked"]),
                    c.variants("MCH", ["i", "o", "u", "ue"]),
                    by=None,
                )
            if "MCHx" in c.locales:
                c.sub(
                    c.variants("MCHx", ["cX", "z", "jhX"]),
                    c.input(c.classes["MCHx-i"], c.conditions["MCHx:marked"]),
                    by=None,
                )


def iii2c(c: MongFeaComposer) -> None:
    """
    When Hudum _n_, _j_, _w_  follows an MVS that follows chachlag _a_ or _e_, apply `chachlag_onset`. When Hudum _h_, _g_, Hudum Ali Gali _a_ follows an MVS that follows chachlag _a_, apply `chachlag_onset`.

    According to GB requirements, when Hudum _g_ follows an MVS that follows chachlag _e_, apply `chachlag_devsger`.
    """

    if {"MNG", "MNGx"}.intersection(c.locales):
        with c.Lookup(
            "III.n_j_w_h_g_a.chachlag_onset.MNG_MNGx",
            feature="rclt",
            flags={"IgnoreMarks": True},
        ):
            njwVariants = c.variants("MNG", ["n.fina", "j.isol", "j.fina", "w.fina"])
            hgVariants = c.variants("MNG", ["h", "g"], "fina")
            if "MNG" in c.locales:
                c.sub(
                    c.input(njwVariants, c.conditions["MNG:chachlag_onset"]),
                    c.classes["mvs.valid"],
                    c.glyphClass(["u1820.Aa.isol", "u1821.Aa.isol"]),
                    by=None,
                )
                c.sub(
                    c.input(hgVariants, c.conditions["MNG:chachlag_onset"]),
                    c.classes["mvs.valid"],
                    "u1820.Aa.isol",
                    by=None,
                )
            if "MNGx" in c.locales:
                c.sub(
                    c.input(c.classes["MNGx-a.fina"], c.conditions["MNG:chachlag_onset"]),
                    c.classes["mvs.valid"],
                    "u1820.Aa.isol",
                    by=None,
                )

    if "MNG" in c.locales:
        with c.Lookup("III.g.chachlag_onset.MNG.GB", feature="rclt", flags={"IgnoreMarks": True}):
            c.sub(
                c.input(c.classes["MNG-g.fina"], c.conditions["MNG:chachlag_onset_gb"]),
                c.classes["mvs.valid"],
                "u1821.Aa.isol",
                by=None,
            )


def iii2d(c: MongFeaComposer) -> None:
    """
    (1) When Sibe _e_ or _u_ follows _t_, _d_, _k_, _g_, _h_, apply `feminine`.

    (2) When Manchu _e_, _u_ follows _t_, _d_, _k_, _g_, _h_, apply `feminine`.

    (3) When Manchu Ali Gali _e_, _u_ follows _tX_, _t_, _d_, _dhX_, _g_, _k_, _ghX_, _h_, apply `feminine`. When Manchu Ali Gali _e_ follows _ngX_, _sbm_, apply `feminine`.
    """

    if {"SIB", "MCH", "MCHx"}.intersection(c.locales):
        with c.Lookup("III.e_u.feminine.SIB_MCH_MCHx", feature="rclt", flags={"IgnoreMarks": True}):
            for locale in ["SIB", "MCH", "MCHx"]:
                if locale in c.locales:
                    feminineFollowingT(c, locale)

            # Gx
            for locale in ["MCH", "MCHx"]:
                if locale in c.locales:
                    feminineFollowingK(c, locale)


def feminineFollowingT(c: MongFeaComposer, locale: LocaleID) -> None:
    """Apply `feminine` to the _e_ or _u_ that follows a t-like consonant of *locale*.

    The t-like consonant makes the word feminine, and the vowel that follows it is written
    with the feminine form of its position. A vowel of the same word may follow that vowel
    — `u u`, where the second _u_ ends the word, or `ue u` — and the word stays feminine, so
    the `feminine` lookup is reached through a vowel as well. Without it the word would be
    feminine where a consonant made it so and not where its own vowel carried the gender
    on, and the final _u_ of such a word would keep the form the character is written with
    by default.
    """

    consonants = c.variants(locale, ["t", "d", "k", "g", "h"])
    if locale == "MCHx":
        consonants = c.variants("MCHx", ["tX", "t", "d", "dhX", "g", "k", "ghX", "h"])
    euLetters = c.variants(locale, ["e", "u"])
    feminineMarked = c.input("u1860.Oh.fina", c.conditions[f"{locale}:feminine_marked"])
    feminine = c.input(euLetters, c.conditions[f"{locale}:feminine"])
    c.sub(consonants, feminineMarked, by=None)
    c.sub(consonants, feminine, by=None)
    c.sub(c.classes[f"{locale}-vowel"], feminine, by=None)

    if locale == "MCHx":
        c.sub(c.classes["MCHx-sbm"], feminine, by=None)


def feminineFollowingK(c: MongFeaComposer, locale: LocaleID) -> None:
    """Apply `feminine` to the _e_ or _u_ that follows _k_ of *locale* before an FVS."""

    euLetters = c.variants(locale, ["e", "u"])
    feminine = c.input(euLetters, c.conditions[f"{locale}:feminine"])
    c.sub(c.classes[f"{locale}-k.init"], c.classes["fvs2"], feminine, by=None)
    c.sub(c.classes[f"{locale}-k.medi"], c.classes["fvs4"], feminine, by=None)
    if locale == "MCHx":
        c.sub(c.classes["MCHx-g.init"], c.classes["fvs2"], feminine, by=None)


def iii2e(c: MongFeaComposer) -> None:
    """
    (1) For Hudum, Todo, Sibe, Manchu and Manchu Ali Gali, when _n_ follows a vowel, apply `onset`; when _n_ follows a consonant, apply `devsger`.

    (2) For Hudum, When _t_ or _d_ follows a vowel, apply `onset`; when _t_ or _d_ follows a consonant, apply `devsger`. For Sibe and Manchu, when _t_ or _d_ follows _a_ or _i_ or _o_, apply `masculine_onset`; when _t_ or _d_ follows _e_, _u_, _ue_, apply `feminine`; when _t_ follows a consonant, apply `devsger`; when _t_ precedes a vowel, apply `devsger`. For Manchu Ali Gali, when _tX_ or _dhX_ follows _a_ or _i_ or _o_, apply `masculine_onset`; when _tX_ or _dhX_ follows _e_ or _u_ or _ue_, apply `feminine`.
    """

    if {"MNG", "TOD", "SIB", "MCH", "MCHx"}.intersection(c.locales):
        with c.Lookup(
            "III.n.onset_and_devsger.MNG_TOD_SIB_MCH_MCHx",
            feature="rclt",
            flags={"IgnoreMarks": True},
        ):
            for locale in ["MNG", "TOD", "SIB", "MCH", "MCHx"]:
                if locale in c.locales:
                    onset = c.input(c.classes[f"{locale}-n"], c.conditions[f"{locale}:onset"])
                    devsger = c.input(c.classes[f"{locale}-n"], c.conditions[f"{locale}:devsger"])
                    c.sub(onset, c.classes[f"{locale}-vowel"], by=None)
                    c.sub(devsger, c.classes[f"{locale}-consonant"], by=None)

    if {"MNG", "SIB", "MCH", "MCHx"}.intersection(c.locales):
        with c.Lookup(
            "III.t_d.onset_and_devsger_and_gender.MNG_MCH_MCHx",
            feature="rclt",
            flags={"IgnoreMarks": True},
        ):
            if "MNG" in c.locales:
                tLikeInit = c.input(c.variants("MNG", ["t", "d"], init))
                tLike = c.variants("MNG", ["t", "d"])
                onset = c.input(tLike, c.conditions["MNG:onset"])
                devsger = c.input(tLike, c.conditions["MNG:devsger"])
                c.sub(tLikeInit, c.classes["MNG-vowel.fina"], by=None)
                c.sub(onset, c.classes["MNG-vowel"], by=None)
                c.sub(devsger, c.classes["MNG-consonant"], by=None)
            for locale in ["SIB", "MCH", "MCHx"]:
                if locale in c.locales:
                    tLikeFollowing(c, locale)


def tLikeFollowing(c: MongFeaComposer, locale: LocaleID) -> None:
    """Apply `masculine_onset`, `feminine` or `devsger` to the vowel that follows a
    t-like consonant of *locale*.

    The feminine vowel of Manchu Ali Gali is written as an _e_ that follows a _tX_, and
    the joined _t_ that ends a word is written differently from the one that starts it.
    """

    tLike = c.variants(locale, ["t", "d"])
    if locale == "MCHx":
        tLike = c.variants("MCHx", ["tX", "dhX"])
    aLike = c.variants(locale, ["a", "i", "o"])
    eLike = c.variants(locale, ["e", "u", "ue"])
    masculineOnset = c.input(tLike, c.conditions[f"{locale}:masculine_onset"])
    feminine = c.input(tLike, c.conditions[f"{locale}:feminine"])
    c.sub(masculineOnset, aLike, by=None)
    c.sub(feminine, eLike, by=None)

    if locale == "MCHx":
        return

    devsger = c.input(c.classes[f"{locale}-t"], c.conditions[f"{locale}:devsger"])
    finaDevsger = c.input(c.classes[f"{locale}-t.fina"], c.conditions[f"{locale}:devsger"])
    c.sub(devsger, c.classes[f"{locale}-consonant"], by=None)
    c.sub(c.classes[f"{locale}-vowel"], finaDevsger, by=None)


def iii2f(c: MongFeaComposer) -> None:
    """
    (1) When (_k_,) _g_, _h_ precedes masculine vowel, apply `masculine_onset`. When (_k_,) _g_, _h_ precedes feminine or neuter vowel, apply `feminine`. Apply `masculine_devsger` or `feminine` or `devsger` for Hudum, Todo, Sibe, Manchu in devsger context.

    (2) For Hudum, when _g_, _h_ following _i_ precedes masculine indicator, apply `masculine_devsger`, else apply `feminine`. When initial _g_, _h_ precedes a consonant, apply `feminine`.

    (3) Delete all the masculine indicators and the feminine indicators after _g_ or _h_.
    """

    if {"MNG", "TOD", "SIB", "MCH"}.intersection(c.locales):

        def makeGLike(locale):
            return c.variants(locale, ["h", "g"] if locale in ["MNG", "TOD"] else ["k", "g", "h"])

        with c.Lookup(
            "III.k_g_h.onset_and_devsger_and_gender.MNG_TOD_SIB_MCH",
            feature="rclt",
            flags={"IgnoreMarks": True},
        ):
            if "MNG" in c.locales:
                gLike = c.input(makeGLike("MNG"))
                c.sub(gLike, c.classes["mvs"], c.variants("MNG", ["a", "e"], isol), by=None)
            for locale in ["MNG", "TOD", "SIB", "MCH"]:
                if locale in c.locales:
                    onset = c.input(makeGLike(locale), c.conditions[f"{locale}:masculine_onset"])
                    c.sub(onset, c.classes[f"{locale}-vowelMasculine"], by=None)

            for locale in ["MNG", "TOD", "SIB", "MCH"]:
                if locale in c.locales:
                    feminine = c.input(makeGLike(locale), c.conditions[f"{locale}:feminine"])
                    feminineVowels = c.classes[f"{locale}-vowelFeminine"]
                    neuterVowels = c.classes[f"{locale}-vowelNeuter"]
                    c.sub(feminine, c.glyphClass([feminineVowels, neuterVowels]), by=None)

            if "MNG" in c.locales:
                masculineDevsger = c.input(makeGLike("MNG"), c.conditions["MNG:masculine_devsger"])
                feminine = c.input(makeGLike("MNG"), c.conditions["MNG:feminine"])
                c.sub(c.classes["MNG-vowelMasculine"], masculineDevsger, by=None)
                c.sub(c.classes["MNG-vowelFeminine"], feminine, by=None)
            if "TOD" in c.locales:
                devsger = c.input(c.classes["TOD-g"], c.conditions["TOD:masculine_devsger"])
                c.sub(c.classes["TOD-vowel"], devsger, by=None)
            if "SIB" in c.locales:
                devsger = c.input(c.classes["SIB-k"], c.conditions["SIB:devsger"])
                c.sub(devsger, c.classes["SIB-consonant"], by=None)
                finaDevsger = c.input(c.classes["SIB-k.fina"], c.conditions["SIB:devsger"])
                c.sub(c.classes["SIB-vowel"], finaDevsger, by=None)
            if "MCH" in c.locales:
                mchGenderDevsger(c)

    if "MNG" in c.locales:
        with c.Lookup(
            "III.g_h.onset_and_devsger_and_gender.A.MNG",
            feature="rclt",
            flags={"UseMarkFilteringSet": c.glyphClass([MARKER_MASCULINE])},
        ):
            gLike = c.variants("MNG", ["h", "g"])
            aLike = c.variants("MNG", ["a", "e"], isol)
            c.sub(c.input(gLike), c.classes["MNG-vowel"], by=None)
            c.sub(c.input(gLike), MARKER_MASCULINE, c.classes["MNG-vowel"], by=None)
            c.sub(c.input(gLike), c.classes["mvs"], aLike, by=None)
            c.sub(c.input(gLike), MARKER_MASCULINE, c.classes["mvs"], aLike, by=None)
            masculineDevsger = c.input(gLike, c.conditions["MNG:masculine_devsger"])
            c.sub(c.classes["MNG-i"], masculineDevsger, MARKER_MASCULINE, by=None)
            feminine = c.input(c.classes["MNG-g"], c.conditions["MNG:feminine"])
            c.sub(c.classes["MNG-i"], feminine, by=None)

        with c.Lookup(
            "III.g_h.onset_and_devsger_and_gender.B.MNG",
            feature="rclt",
            flags={"IgnoreMarks": True},
        ):
            feminine = c.input(c.variants("MNG", ["h", "g"], init), c.conditions["MNG:feminine"])
            c.sub(feminine, c.classes["MNG-consonant"], by=None)

        for index in [0, 1]:
            step = ["A", "B"][index]
            genderMarker = [MARKER_MASCULINE, MARKER_FEMININE][index]
            postprocessGender(c, step, genderMarker)


def mchGenderDevsger(c: MongFeaComposer) -> None:
    """Apply the gender and devsger of _k_ in Manchu."""

    masculineDevsger = c.input(c.classes["MCH-k"], c.conditions["MCH:masculine_devsger"])
    feminine = c.input(c.classes["MCH-k"], c.conditions["MCH:feminine"])
    c.sub(c.classes["MCH-t"], c.classes["MCH-e"], masculineDevsger, by=None)
    gLike = c.variants("MCH", ["k", "g", "h"])
    c.sub(gLike, c.classes["MCH-u"], feminine, by=None)
    ghLike = c.variants("MCH", ["kh", "gh", "hh"])
    c.sub(ghLike, c.classes["MCH-a"], feminine, by=None)
    c.sub(c.variants("MCH", ["e", "ue"]), feminine, by=None)
    c.sub(c.variants("MCH", ["a", "i", "o", "u"]), masculineDevsger, by=None)


def postprocessGender(c: MongFeaComposer, step: str, genderMarker: str) -> None:
    """Delete the *genderMarker* that follows the _g_ or _h_ of Hudum."""

    with c.Lookup(
        f"III.ig.post_processing.{step}.MNG",
        feature="rclt",
        flags={"UseMarkFilteringSet": c.glyphClass([genderMarker])},
    ):
        for alias in ["h", "g"]:
            charName = getCharNameByAlias("MNG", alias)
            for position in (init, medi, fina):
                for variant in data.variants[charName].get(position, {}).values():
                    written = GlyphDescriptor.fromData(charName, position, variant)
                    c.sub(str(written), genderMarker, by=str(written))


def iii2g(c: MongFeaComposer) -> None:
    """
    (1) When _t_ precedes _ee_ or consonant, apply `devsger`.

    (2) When _sh_ precedes _i_ and not in Twelve Syllabaries, apply `dotless`.

    (3) When _g_ follows _s_ or _d_, apply `dotless`.
    """

    if "MNG" in c.locales:
        with c.Lookup("III.t_sh_g.MNG.GB", feature="rclt", flags={"IgnoreMarks": True}):
            devsger = c.input(c.classes["MNG-t"], c.conditions["MNG:devsger"])
            c.sub(devsger, c.variants("MNG", ["ee", "consonant"]), by=None)
            dotlessInit = c.input(c.classes["MNG-sh.init"], c.conditions["MNG:dotless"])
            c.sub(dotlessInit, c.classes["MNG-i.medi"], by=None)
            dotlessMedi = c.input(c.classes["MNG-sh.medi"], c.conditions["MNG:dotless"])
            c.sub(dotlessMedi, c.variants("MNG", "i", (medi, fina)), by=None)
            gMedi = c.input(c.classes["MNG-g.medi"], c.conditions["MNG:dotless"])
            gFina = c.input(c.classes["MNG-g.fina"], c.conditions["MNG:dotless"])
            sLike = c.variants("MNG", ["s", "d"])
            c.sub(sLike, gMedi, c.classes["MNG-vowelMasculine"], by=None)
            c.sub(sLike, gFina, c.classes["mvs"], "u1820.Aa.isol", by=None)


def iii3(c: MongFeaComposer) -> None:
    """
    **Phase III.3: Phonetic - Particle**

    (1) Apply `particle` for letters in particles following MVS in Hudum, Todo, Sibe and Manchu.

    (2) Apply `particle` for letters in particles not following MVS in Hudum.

    (3) According to GB, apply `_.wide` for MVS preceding Hudum string in Hudum.
    """

    for locale in ["MNG", "SIB", "MCH"]:
        if locale in c.locales:
            with c.Lookup(
                f"III.particle.{locale}",
                feature="rclt",
                flags={"UseMarkFilteringSet": c.classes["fvs"]},
            ):
                for aliasString, particle in data.particles[locale].items():
                    implementParticle(c, locale, aliasString, particle)

    if "TOD" in c.locales:
        with c.Lookup("III.particle.TOD", feature="rclt", flags={"IgnoreMarks": True}):
            wide = c.input(c.classes["mvs"], c.conditions["_.wide"])
            particle = c.input(c.classes["TOD-n.init"], c.conditions["TOD:particle"])
            c.sub(wide, particle, c.classes["TOD-i.fina"], by=None)

    if "MNG" in c.locales:
        with c.Lookup("III.mvs.postprocessing.GB", feature="rclt"):
            wide = c.input(c.classes["mvs.invalid"], c.conditions["_.wide"])
            following = c.glyphClass(
                [
                    c.classes["MNG-vowel"],
                    c.classes["MNG-consonant"],
                    "nirugu",
                    "nirugu.ignored",
                ]
            )
            c.sub(wide, following, by=None)


def implementParticle(
    c: MongFeaComposer, locale: LocaleID, aliasString: str, particle: ParticleData
) -> None:
    """Apply `particle` to the letters of one particle of *locale*.

    A particle is a string of letters; the letters to which `particle` applies are given
    by the indices of the particle. The lookup ignores the particle when it follows an MVS
    and applies `particle` to the letters of the particle when it does not.
    """

    aliasList = aliasString.split()
    indices = particle.indices
    hasMvs = aliasList[0] == "mvs"
    if hasMvs:
        aliasList = aliasList[1:]
        indices = [index - 1 for index in indices]

    classList = [
        c.classes[f"{locale}-{alias}.{getPosition(index, len(aliasList))}"]
        for index, alias in enumerate(aliasList)
    ]

    subArgs: list = []
    if hasMvs:
        subArgs.append(c.input(c.classes["mvs.invalid"], c.conditions["_.wide"]))
    ignoreSubArgs: list = [c.input(c.classes["mvs"])] if hasMvs else []
    minIndex = 0 if hasMvs else min(indices)
    for index, glyphClass in enumerate(classList):
        subInput = c.input(glyphClass)
        ignoreSubArgs.append(subInput)
        if index in indices:
            subArgs.append(c.input(glyphClass, c.conditions[f"{locale}:particle"]))
        elif minIndex <= index <= max(indices):
            subArgs.append(subInput)
        else:
            subArgs.append(glyphClass)
    c.sub(*ignoreSubArgs, c.classes["fvs"], by=None)
    c.sub(*subArgs, by=None)


def iii4(c: MongFeaComposer) -> None:
    """
    **Phase III.4: Graphemic - Devsger**

    (1) Apply `devsger` for _i_ and _u_ in Hudum, Todo, Sibe and Manchu.

    (2) According to GB, reset _i_ in some contexts.
    """

    categories = data.locales["MNG"].categories

    if {"MNG", "TOD", "SIB", "MCH", "MCHx"}.intersection(c.locales):
        with c.Lookup(
            "III.i_u.devsger.MNG_TOD_SIB_MCH_MCHx", feature="rclt", flags={"IgnoreMarks": True}
        ):
            if "MNG" in c.locales:
                writtens = c.writtens(
                    "MNG", lambda x: x[-1] != "I", (init, medi), categories["vowel"]
                )
                vowelVariants = c.namedGlyphClass("MNG-vowel.not_ending_with_I", writtens.glyphs)
                i = c.input(c.classes["MNG-i"], c.conditions["MNG:vowel_devsger"])
                c.sub(vowelVariants, i, by=None)
            if "TOD" in c.locales:
                i = c.input(c.classes["TOD-i"], c.conditions["TOD:vowel_devsger"])
                u = c.input(c.classes["TOD-u"], c.conditions["TOD:vowel_devsger"])
                c.sub(c.classes["TOD-vowel"], i, by=None)
                c.sub(c.classes["TOD-u"], u, by=None)
            if "SIB" in c.locales:
                i = c.input(c.classes["SIB-i"], c.conditions["SIB:vowel_devsger"])
                u = c.input(c.classes["SIB-u"], c.conditions["SIB:vowel_devsger"])
                c.sub(c.classes["SIB-vowel"], i, by=None)
                c.sub(c.classes["SIB-vowel"], u, by=None)
            if "MCH" in c.locales:
                i = c.input(c.classes["MCH-i"], c.conditions["MCH:vowel_devsger"])
                c.sub(c.classes["MCH-vowel"], i, by=None)
            if "MCHx" in c.locales:
                i = c.input(c.classes["MCHx-i"], c.conditions["MCHx:vowel_devsger"])
                u = c.input(c.classes["MCHx-u"], c.conditions["MCHx:vowel_devsger"])
                c.sub(c.classes["MCHx-vowel"], i, by=None)
                c.sub(c.classes["MCHx-vowel"], u, by=None)

    if "MNG" in c.locales:
        with c.Lookup(
            "III.i.devsger.MNG.GB",
            feature="rclt",
            flags={"UseMarkFilteringSet": c.classes["fvs"]},
        ):
            oeUeMedi = c.variants("MNG", ["oe", "ue"], medi)
            i = c.input(c.variants("MNG", "i", (medi, fina)), c.conditions["MNG:reset"])
            iFina = c.input(c.classes["MNG-i"], c.conditions["MNG:vowel_devsger"])
            c.sub(oeUeMedi, c.glyphClass([c.classes["fvs1"], c.classes["fvs2"]]), i, by=None)
            c.sub(oeUeMedi, c.classes["fvs3"], iFina, by=None)
            ueInit = c.classes["MNG-ue.init"]
            c.sub(ueInit, c.classes["fvs2"], i, by=None)
            c.sub(ueInit, c.classes["fvs1"], iFina, by=None)


def iii5(c: MongFeaComposer) -> None:
    """
    **Phase III.5: Graphemic - Post-bowed**

    (1) Apply `post_bowed` for vowel following bowed consonant for Hudum, Hudum Ali Gali, Todo, Todo Ali Gali, Sibe, Manchu and Manchu Ali Gali.

    (2) According to GB, adjust the vowel (may precede FVS) following bowed consonant for Hudum.
    """

    if "MNG" in c.locales:
        bowedB = c.namedGlyphClass("MNG-bowedB", c.variants("MNG", ["b", "p", "f"]).glyphs)
        bowedK = c.namedGlyphClass("MNG-bowedK", c.variants("MNG", ["k", "k2"]).glyphs)
        bowedG = c.namedGlyphClass("MNG-bowedG", c.writtens("MNG", ["G", "Gx"]).glyphs)

        with c.Lookup("III.vowel.post_bowed.MNG", feature="rclt", flags={"IgnoreMarks": True}):
            bowed = c.glyphClass([bowedB, bowedK, bowedG])
            ueFina = c.glyphClass(["u1825.Ue.fina", "u1826.Ue.fina"])
            c.sub(bowed, c.input(ueFina), by=None)
            oUOeUeFina = c.variants("MNG", ["o", "u", "oe", "ue"], fina)
            postBowed = c.input(oUOeUeFina, c.conditions["MNG:post_bowed"])
            c.sub(bowed, postBowed, by=None)
            aeFina = c.variants("MNG", ["a", "e"], fina)
            aePostBowed = c.input(aeFina, c.conditions["MNG:post_bowed"])
            eFina = c.variants("MNG", "e", fina)
            c.sub(c.glyphClass([bowedB, bowedK]), aePostBowed, by=None)
            c.sub(bowedG, c.input(eFina, c.conditions["MNG:post_bowed"]), by=None)

        with c.Lookup("III.fvs.post_bowed.preprocessing.GB", feature="rclt"):
            bowed = c.glyphClass([bowedB, bowedK, bowedG])
            ignored = c.input(c.classes["fvs.ignored"], c.conditions["_.reset"])
            c.sub(bowed, ignored, by=None)

        with c.Lookup("III.vowel.post_bowed.MNG.GB", feature="rclt", flags={"IgnoreMarks": True}):
            hgVariants = c.variants("MNG", ["h", "g"])
            fvs24 = c.glyphClass([c.classes["fvs2"], c.classes["fvs4"]])
            fvs13 = c.glyphClass([c.classes["fvs1"], c.classes["fvs3"]])
            ePostBowed = c.input(c.classes["MNG-e.fina"], c.conditions["MNG:post_bowed"])
            eReset = c.input(c.classes["MNG-e.fina"], c.conditions["MNG:reset"])
            c.sub(hgVariants, fvs24, ePostBowed, by=None)
            c.sub(hgVariants, fvs13, eReset, by=None)
            oUOeUeFina = c.variants("MNG", ["o", "u", "oe", "ue"], fina)
            oeUeFina = c.variants("MNG", ["oe", "ue"], fina)
            oUFina = c.variants("MNG", ["o", "u"], fina)
            initials = c.variants("MNG", ["b", "p", "f", "k", "k2"], init)
            marked = c.input(oeUeFina, c.conditions["MNG:marked"])
            c.sub(initials, c.classes["fvs"], marked, by=None)
            reset = c.input(oUOeUeFina, c.conditions["MNG:reset"])
            c.sub(hgVariants, fvs13, reset, by=None)
            gLike = c.variants("MNG", ["g", "h"], (init, medi))
            mediGLike = c.variants("MNG", ["g", "h"], medi)
            initGLike = c.variants("MNG", ["g", "h"], init)
            c.sub(gLike, fvs24, c.input(oUFina, c.conditions["MNG:reset"]), by=None)
            c.sub(mediGLike, fvs24, c.input(oeUeFina, c.conditions["MNG:post_bowed"]), by=None)
            c.sub(initGLike, fvs24, marked, by=None)

        with c.Lookup("III.fvs.post_bowed.postprocessing.GB", feature="rclt"):
            bowed = c.glyphClass([bowedB, bowedK, bowedG])
            invalid = c.input(c.classes["fvs.invalid"], c.conditions["_.ignored"])
            c.sub(bowed, invalid, by=None)

    if "MNGx" in c.locales:
        bowedB = c.namedGlyphClass("MNGx-bowedB", c.variants("MNGx", ["pX", "phX", "b"]).glyphs)
        bowedK = c.namedGlyphClass("MNGx-bowedK", c.variants("MNGx", ["kX", "k2", "k"]).glyphs)
        with c.Lookup("III.vowel.post_bowed.MNGx", feature="rclt", flags={"IgnoreMarks": True}):
            bowed = c.glyphClass([bowedB, bowedK])
            vowels = ["a", "o", "ue"]
            postBowed = c.input(c.variants("MNGx", vowels, fina), c.conditions["MNGx:post_bowed"])
            c.sub(bowed, postBowed, by=None)

    if "TOD" in c.locales:
        bowedB = c.namedGlyphClass("TOD-bowedB", c.variants("TOD", ["b", "p"]).glyphs)
        bowedK = c.namedGlyphClass("TOD-bowedK", c.variants("TOD", ["kh", "gh"]).glyphs)
        bowedG = c.namedGlyphClass("TOD-bowedG", c.writtens("TOD", ["K", "G"]).glyphs)
        with c.Lookup("III.vowel.post_bowed.TOD", feature="rclt", flags={"IgnoreMarks": True}):
            bowed = c.glyphClass([bowedB, bowedK, bowedG])
            vowels = ["a", "i", "u", "ue"]
            postBowed = c.input(c.variants("TOD", vowels, fina), c.conditions["TOD:post_bowed"])
            c.sub(bowed, postBowed, by=None)

            c.sub(bowed, c.input(c.classes["TOD-a_lvs.fina"]), by="u1820_u1843.AaLv.fina")

    if "TODx" in c.locales:
        # A bowed letter of Todo Ali Gali is written with a form of its own where the writing
        # systems that share the character agree on another one — the initial _pX_ is `Bh`
        # for Todo Ali Gali and `Bg` for the others — and the shared form is the one the
        # letter carries until the FVS lookups of Phase III.6 draw its own. The bow is drawn
        # the same way in both, so both are taken here, or the vowel after the bow would not
        # be redrawn as it is written after one.
        bowedB = c.namedGlyphClass(
            "TODx-bowedB",
            withSharedVariants(c, "TODx", ["pX", "p", "b"]),
        )
        bowedK = c.namedGlyphClass(
            "TODx-bowedK",
            withSharedVariants(c, "TODx", ["kX", "khX", "gX"]),
        )
        with c.Lookup("III.vowel.post_bowed.TODx", feature="rclt", flags={"IgnoreMarks": True}):
            bowed = c.glyphClass([bowedB, bowedK])
            vowels = ["a", "i", "ue"]
            postBowed = c.input(c.variants("TODx", vowels, fina), c.conditions["TODx:post_bowed"])
            c.sub(bowed, postBowed, by=None)

            c.sub(bowed, c.input(c.classes["TODx-a_lvs.fina"]), by="u1820_u1843.AaLv.fina")
            c.sub(bowed, c.input(c.classes["TODx-i_lvs.fina"]), by="u1845_u1843.IpLv.fina")
            c.sub(bowed, c.input(c.classes["TODx-ue_lvs.fina"]), by="u1849_u1843.OLv.fina")

    for locale in ["SIB", "MCH"]:
        if locale in c.locales:
            bowedB = c.namedGlyphClass(f"{locale}-bowedB", c.variants(locale, ["b", "p"]).glyphs)
            bowedK = c.namedGlyphClass(
                f"{locale}-bowedK", c.variants(locale, ["kh", "gh", "hh"]).glyphs
            )
            bowedG = c.namedGlyphClass(
                f"{locale}-bowedG", c.writtens(locale, ["G", "Gh", "Gc"]).glyphs
            )
            with c.Lookup(
                f"III.vowel.post_bowed.{locale}", feature="rclt", flags={"IgnoreMarks": True}
            ):
                euLetters = c.variants(locale, ["e", "u"])
                postBowed = c.input(euLetters, c.conditions[f"{locale}:post_bowed"])
                postBowedFeminine = c.input(
                    euLetters, c.conditions[f"{locale}:post_bowed_feminine"]
                )
                aoLetters = c.variants(locale, ["a", "o"])
                aoPostBowed = c.input(aoLetters, c.conditions[f"{locale}:post_bowed"])
                c.sub(bowedB, postBowed, by=None)
                c.sub(bowedG, postBowedFeminine, by=None)
                c.sub(c.glyphClass([bowedB, bowedK]), aoPostBowed, by=None)

                # Gx
                if locale == "MCH":
                    c.sub(c.classes["MCH-k.init"], c.classes["fvs2"], postBowedFeminine, by=None)
                    c.sub(c.classes["MCH-k.medi"], c.classes["fvs4"], postBowedFeminine, by=None)

    if "MCHx" in c.locales:
        bowedB = c.namedGlyphClass(
            "MCHx-bowedB",
            c.variants("MCHx", ["pX", "p", "b", "bhX"]).glyphs,
        )
        bowedK = c.namedGlyphClass(
            "MCHx-bowedK",
            c.variants("MCHx", ["gh", "kh"]).glyphs,
        )
        bowedG = c.namedGlyphClass(
            "MCHx-bowedG",
            c.writtens("MCHx", ["G", "Gh", "Gc", "Gx"]).glyphs,
        )
        with c.Lookup("III.vowel.post_bowed.MCHx", feature="rclt", flags={"IgnoreMarks": True}):
            euLetters = c.variants("MCHx", ["e", "u"])
            postBowed = c.input(euLetters, c.conditions["MCHx:post_bowed"])
            postBowedFeminine = c.input(euLetters, c.conditions["MCHx:post_bowed_feminine"])
            e = c.input(c.classes["MCHx-e"], c.conditions["MCHx:post_bowed_feminine"])
            ePostBowed = c.input(c.classes["MCHx-e"], c.conditions["MCHx:post_bowed"])
            aoPostBowed = c.input(c.variants("MCHx", ["a", "o"]), c.conditions["MCHx:post_bowed"])
            c.sub(bowedB, postBowed, by=None)
            c.sub(c.glyphClass([bowedG, c.classes["MCHx-ghX"]]), postBowedFeminine, by=None)
            c.sub(c.classes["MCHx-ngX"], e, by=None)
            c.sub(c.classes["MCHx-sbm"], ePostBowed, by=None)
            c.sub(c.glyphClass([bowedB, bowedK]), aoPostBowed, by=None)

            c.sub(c.classes["MCHx-k.init"], c.classes["fvs2"], postBowedFeminine, by=None)
            c.sub(c.classes["MCHx-k.medi"], c.classes["fvs4"], postBowedFeminine, by=None)
            c.sub(c.classes["MCHx-g.init"], c.classes["fvs2"], postBowedFeminine, by=None)


def iii6(c: MongFeaComposer) -> None:
    """
    **Phase III.6: Uncaptured - FVS-selected**

    (1) Apply `manual` for letters preceding FVS.

    (2) Apply `manual` for punctuation.

    (3) Draw a letter and the final Todo long vowel sign that follows it as one written form.
    """

    for locale in c.locales:
        with c.Lookup(f"_.manual.{locale}") as _lvs:
            manualFvses(c, locale)

        with c.Lookup(f"III.fvs.{locale}", feature="rclt"):
            automatedFvses(c, locale, _lvs)

    ligateLvs(c)

    if "MNGx" in c.locales:
        with c.Lookup("_.manual.punctuation") as _lvs:
            c.sub(c.input("u1880"), "fvs1.ignored", by="u1880.fvs1")
            c.sub(c.input("u1881"), "fvs1.ignored", by="u1881.fvs1")

        with c.Lookup("III.fvs.punctuation", feature="rclt"):
            valid = c.input("fvs1.ignored", c.conditions["_.valid"])
            c.sub(c.input("u1880", _lvs), valid, by=None)
            c.sub(c.input("u1881", _lvs), valid, by=None)


def fvsPrecedingLetters(
    c: MongFeaComposer, locale: LocaleID
) -> Iterator[tuple[ast.GlyphClass | ast.GlyphClassDefinition, int, str]]:
    """Every letter of *locale* that precedes an FVS, with the FVS it precedes.

    A letter whose writing system writes the position with a form of its own, while the
    writing systems that share the character agree on another form, reaches the shared
    form through the cross-writing-system lookups of Phase IIa — those lookups answer for
    every writing system at once, so they cannot answer with the form of one of them. The
    writing system has to accept the shared form beside its own here, and it draws its own
    form from the shared one in the lookups of Phase III.6.
    """

    for alias, charName, position, fvs, variant in getVariants(locale):
        if fvs == 0 or locale not in variant.locales:
            continue
        glyphClass = c.classes[f"{locale}-{alias}.{position}"]
        members = [*glyphClass.glyphSet()]
        if shared := sharedVariant(c, charName, position, members):
            glyphClass = c.glyphClass([shared, *members])
        by = str(GlyphDescriptor.fromData(charName, position, variant))
        yield glyphClass, fvs, by


def manualFvses(c: MongFeaComposer, locale: LocaleID) -> None:
    """Draw the own form of every letter of *locale* that precedes an FVS."""

    for glyphClass, fvs, by in fvsPrecedingLetters(c, locale):
        c.sub(c.input(glyphClass), f"fvs{fvs}.ignored", by=by)


def sharedVariant(
    c: MongFeaComposer,
    charName: CharacterName,
    position: JoiningPosition,
    members: Iterable,
) -> str | None:
    """The glyph the cross-writing-system lookups draw the position with, if not *members*.

    A glyph of the position that no written form of *locale* names is the one the shared
    lookups draw, so a letter that comes through them carries it.
    """

    shared = c.defaultVariant(charName, position)
    if any(i.glyph == shared for i in members):
        return None
    return shared


def withSharedVariants(c: MongFeaComposer, locale: LocaleID, aliases: list[str]) -> list[str]:
    """The written forms of *aliases* of *locale*, each beside the form it shares.

    A writing system that writes a letter with a form of its own carries the shared form of
    the character until the FVS lookups of Phase III.6 draw its own, so a class that a
    lookup before Phase III.6 reads has to hold both. The shared form is the one the font
    draws the character with, which is the same for every writing system that shares it.
    """

    members = list[str]()
    for alias in aliases:
        charName = getCharNameByAlias(locale, alias)
        for position in data.variants[charName]:
            own = c.classes[f"{locale}-{alias}.{position}"].glyphSet()
            members.extend(
                i.glyph for i in own if GlyphDescriptor.parse(i.glyph).pseudoPosition() is None
            )  # type: ignore[attr-defined]
            if shared := sharedVariant(c, charName, position, own):
                members.append(shared)
    return list(dict.fromkeys(members))


def automatedFvses(c: MongFeaComposer, locale: LocaleID, _lvs: ast.LookupBlock) -> None:
    """Consume the FVS of every letter of *locale* that precedes one."""

    for glyphClass, fvs, _ in fvsPrecedingLetters(c, locale):
        valid = c.input(f"fvs{fvs}.ignored", c.conditions["_.valid"])
        c.sub(c.input(glyphClass, _lvs), valid, by=None)


def iii7(c: MongFeaComposer) -> None:
    """
    **Phase III.7: Control character postprocessing**

    An nnbsp that no shaping took is written as the glyph of the nnbsp, which is the glyph
    the source font draws for the character.

    Unicode 16.0 hands the function of the nnbsp to the MVS, so every lookup that shapes an
    MVS shapes an nnbsp as well — `@mvs`, `@mvs.invalid` and `@mvs.valid` all hold it — and
    an nnbsp that a chachlag, a particle or a wide space consumed is already written with
    the glyphs that shaping writes. What reaches this phase unwritten is therefore the nnbsp
    that nothing followed, which is the nnbsp that stands as a space of its own, and it is
    written with the glyph of the character rather than with the `mvs` the MVS is drawn
    with. The substitution is made here, at the end of the shaping, because every lookup
    before it reads the nnbsp by the name it shares with the MVS.
    """

    name = c.glyphNameProcessor("nnbsp")
    if name not in c.glyphs and name not in c.spec.newGlyphs:
        return
    with c.Lookup("III.nnbsp.postprocessing", feature="rclt"):
        c.sub("nnbsp", by=name)

    with c.Lookup("III.controls.postprocessing", feature="rclt"):
        c.sub(
            c.input(
                c.glyphClass(["nirugu.ignored", c.classes["fvs.ignored"]]),
                c.conditions["_.reset"],
            ),
            by=None,
        )

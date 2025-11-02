from fontTools.feaLib import ast

from .. import GlyphDescriptor, data, getPosition, ligateParts
from ..data.misc import fina, init, isol, medi
from ..utils import getAliasesByLocale, getCharNameByAlias
from . import MongFeaComposer

MARKER_MASCULINE, MARKER_FEMININE = "marker.masculine", "marker.feminine"


def compose(c: MongFeaComposer) -> None:
    iii0(c)
    iii1(c)
    iii2(c)
    iii3(c)
    iii4(c)
    iii5(c)
    iii6(c)


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

    Specifically, for Todo (Ali Gali) long vowel sign, when the final long vowel sign is substituted to ignored glyph, the joining position of the previous letter will be changed (from `init` to `isol`, from `medi` to `fina`).
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
            lvsCharName = getCharNameByAlias("TOD", "lvs")
            with c.Lookup(
                f"III.lvs.preprocessing.{locale}", feature="rclt", flags={"IgnoreMarks": True}
            ):
                for alias in data.locales[locale].categories["lvs"]:
                    charName = getCharNameByAlias(locale, alias)
                    for position in (init, medi):
                        charVar = GlyphDescriptor.fromData(charName, position)
                        for lvsPosition in (medi, fina):
                            lvsVar = GlyphDescriptor.fromData(lvsCharName, lvsPosition)
                            c.sub(str(charVar), str(lvsVar), by=str(ligateParts([charVar, lvsVar])))


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

    # reverse add masculine
    unmarkedVariants = c.namedGlyphClass(
        "MNG-unmarked.A",
        [
            c.getDefault(alias, position)
            for alias in categories["vowelMasculine"]
            + categories["vowelNeuter"]
            + categories["consonant"]
            for position in (init, medi, fina)
        ],
    )
    markedVariants = c.namedGlyphClass(
        "MNG-marked.A",
        [
            c.getDefault(alias, position, marked=True)
            for alias in categories["vowelMasculine"]
            + categories["vowelNeuter"]
            + categories["consonant"]
            for position in (init, medi, fina)
        ],
    )

    with c.Lookup("_.marked.MNG") as _marked:
        c.sub(unmarkedVariants, by=markedVariants)
    c.conditions[_marked.name] = _marked

    with c.Lookup("_.unmarked.MNG") as _unmarked:
        c.sub(markedVariants, by=unmarkedVariants)
    c.conditions[_unmarked.name] = _unmarked

    with c.Lookup("III.ig.preprocessing.G", feature="rclt", flags={"IgnoreMarks": True}):
        for alias in categories["vowelNeuter"] + categories["consonant"]:
            for position in (init, medi):
                unmarked = c.getDefault(alias, position)
                c.sub(c.input(unmarked, _marked), c.classes["MNG-vowelMasculine"], by=None)
        for alias in (
            categories["vowelMasculine"] + categories["vowelNeuter"] + categories["consonant"]
        ):
            unmarked = c.getDefault(alias, fina)
            c.sub(c.input(unmarked, _marked), c.classes["mvs"], c.classes["MNG-a.isol"], by=None)

    with c.Lookup(
        "III.ig.preprocessing.H",
        feature="rclt",
        flags={"UseMarkFilteringSet": c.glyphClass([MARKER_FEMININE])},
    ):
        for alias in categories["vowelNeuter"] + categories["consonant"]:
            for position in (init, medi):
                unmarked = c.getDefault(alias, position)
                marked = c.getDefault(alias, position, marked=True)
                c.current.append(
                    ast.ReverseChainSingleSubstStatement(
                        old_prefix=[],
                        glyphs=[c._normalized(unmarked)],
                        old_suffix=[c._normalized(markedVariants)],
                        replacements=[c._normalized(marked)],
                    )
                )

    with c.Lookup("III.ig.preprocessing.I", feature="rclt"):
        for alias in ["h", "g"]:
            for position in (init, medi):
                marked = c.getDefault(alias, position, marked=True)
                c.sub(c.input(marked, _unmarked), MARKER_MASCULINE, by=None)

    with c.Lookup("III.ig.preprocessing.J", feature="rclt"):
        markedVariants = c.namedGlyphClass(
            "MNG-marked.B",
            [
                c.getDefault(alias, position, marked=True)
                for alias in categories["vowelMasculine"]
                + categories["vowelNeuter"]
                + categories["consonant"]
                if alias not in ["h", "g"]
                for position in (init, medi, fina)
            ],
        )
        c.sub(c.input(markedVariants, _unmarked), by=None)

    with c.Lookup("III.ig.preprocessing.K", feature="rclt"):
        for alias in ["h", "g"]:
            for position in (init, medi):
                unmarked = c.getDefault(alias, position)
                marked = c.getDefault(alias, position, marked=True)
                c.sub(marked, by=[unmarked, MARKER_MASCULINE])


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
                    c.input(c.variants("MNGx", ["o", "ue"]), c.conditions["MNGx:marked"]),
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
                    c.sub(
                        c.classes[f"{locale}-consonant.init"],
                        c.input(c.variants(locale, ["o", "u"]), c.conditions[f"{locale}:marked"]),
                        by=None,
                    )

    if "MNG" in c.locales:
        with c.Lookup(
            "III.o_u_oe_ue.marked.GB.A",
            feature="rclt",
            flags={"UseMarkFilteringSet": c.classes["fvs"]},
        ):
            variants = c.variants("MNG", ["o", "u", "oe", "ue"], (medi, fina))
            c.sub(c.input(variants, c.conditions["MNG:reset"]), c.classes["fvs"], by=None)
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

        markedVariants = c.namedGlyphClass(
            "MNG-marked.C",
            [
                c.getDefault(alias, position, marked=True)
                for alias in categories["vowelMasculine"]
                + categories["vowelNeuter"]
                + categories["consonant"]
                for position in (init, medi, fina)
            ],
        )
        with c.Lookup(
            "III.o_u_oe_ue.initial_marked.GB.A", feature="rclt", flags={"IgnoreMarks": True}
        ):
            c.sub(
                c.glyphClass([c.classes["MNG-consonant.init"], markedVariants]),
                c.input(c.classes["MNG-consonant.medi"], c.conditions["_.marked.MNG"]),
                by=None,
            )

        variants = c.variants("MNG", ["o", "u", "oe", "ue"], medi)
        with c.Lookup(
            "III.o_u_oe_ue.initial_marked.GB.B", feature="rclt", flags={"IgnoreMarks": True}
        ):
            c.sub(
                c.glyphClass([c.classes["MNG-consonant.init"], markedVariants]),
                c.input(variants, c.conditions["MNG:marked"]),
                by=None,
            )

        with c.Lookup("III.o_u_oe_ue.initial_marked.GB.C", feature="rclt"):
            c.sub(c.input(markedVariants, c.conditions["_.unmarked.MNG"]), by=None)

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
                    consonants = c.variants(locale, ["t", "d", "k", "g", "h"])
                    if locale == "MCHx":
                        consonants = c.variants(
                            "MCHx", ["tX", "t", "d", "dhX", "g", "k", "ghX", "h"]
                        )
                    euLetters = c.variants(locale, ["e", "u"])
                    c.sub(
                        consonants,
                        c.input("u1860.Oh.fina", c.conditions[f"{locale}:feminine_marked"]),
                        by=None,
                    )
                    c.sub(
                        consonants,
                        c.input(euLetters, c.conditions[f"{locale}:feminine"]),
                        by=None,
                    )

                    if locale == "MCHx":
                        c.sub(
                            c.variants("MCHx", ["ngX", "sbm"]),
                            c.input(euLetters, c.conditions["MCHx:feminine"]),
                            by=None,
                        )


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
                    c.sub(
                        c.input(c.classes[f"{locale}-n"], c.conditions[f"{locale}:onset"]),
                        c.classes[f"{locale}-vowel"],
                        by=None,
                    )
                    c.sub(
                        c.input(c.classes[f"{locale}-n"], c.conditions[f"{locale}:devsger"]),
                        c.classes[f"{locale}-consonant"],
                        by=None,
                    )

    if {"MNG", "SIB", "MCH", "MCHx"}.intersection(c.locales):
        with c.Lookup(
            "III.t_d.onset_and_devsger_and_gender.MNG_MCH_MCHx",
            feature="rclt",
            flags={"IgnoreMarks": True},
        ):
            if "MNG" in c.locales:
                c.sub(
                    c.input(c.variants("MNG", ["t", "d"], init)),
                    c.classes["MNG-vowel.fina"],
                    by=None,
                )
                tLike = c.variants("MNG", ["t", "d"])
                c.sub(c.input(tLike, c.conditions["MNG:onset"]), c.classes["MNG-vowel"], by=None)
                c.sub(
                    c.input(tLike, c.conditions["MNG:devsger"]),
                    c.classes["MNG-consonant"],
                    by=None,
                )
            for locale in ["SIB", "MCH", "MCHx"]:
                if locale in c.locales:
                    tLike = c.variants(locale, ["t", "d"])
                    if locale == "MCHx":
                        tLike = c.variants("MCHx", ["tX", "dhX"])
                    aLike = c.variants(locale, ["a", "i", "o"])
                    eLike = c.variants(locale, ["e", "u", "ue"])
                    c.sub(
                        c.input(tLike, c.conditions[f"{locale}:masculine_onset"]),
                        aLike,
                        by=None,
                    )
                    c.sub(c.input(tLike, c.conditions[f"{locale}:feminine"]), eLike, by=None)
                    if locale != "MCHx":
                        c.sub(
                            c.input(c.classes[f"{locale}-t"], c.conditions[f"{locale}:devsger"]),
                            c.classes[f"{locale}-consonant"],
                            by=None,
                        )
                        c.sub(
                            c.classes[f"{locale}-vowel"],
                            c.input(
                                c.classes[f"{locale}-t.fina"], c.conditions[f"{locale}:devsger"]
                            ),
                            by=None,
                        )


def iii2f(c: MongFeaComposer) -> None:
    """
    (1) When (_k_,) _g_, _h_ precedes masculine vowel, apply `masculine_onset`. When (_k_,) _g_, _h_ precedes feminine or neuter vowel, apply `feminine`. Apply `masculine_devsger` or `feminine` or `devsger` for Hudum, Todo, Sibe, Manchu in devsger context.

    (2) For Hudum, when _g_, _h_ following _i_ precedes masculine indicator, apply `masculine_devsger`, else apply `feminine`. When initial _g_, _h_ precedes a consonant, apply `feminine`.

    (3) Delete all the masculine indicators and the feminine indicators after _g_ or _h_.
    """

    if {"MNG", "TOD", "SIB", "MCH"}.intersection(c.locales):
        gLike = lambda locale: c.variants(
            locale, ["h", "g"] if locale in ["MNG", "TOD"] else ["k", "g", "h"]
        )

        with c.Lookup(
            "III.k_g_h.onset_and_devsger_and_gender.MNG_TOD_SIB_MCH",
            feature="rclt",
            flags={"IgnoreMarks": True},
        ):
            if "MNG" in c.locales:
                c.sub(
                    c.input(gLike("MNG")),
                    c.classes["mvs"],
                    c.variants("MNG", ["a", "e"], isol),
                    by=None,
                )
            for locale in ["MNG", "TOD", "SIB", "MCH"]:
                if locale in c.locales:
                    c.sub(
                        c.input(gLike(locale), c.conditions[f"{locale}:masculine_onset"]),
                        c.classes[f"{locale}-vowelMasculine"],
                        by=None,
                    )

            for locale in ["MNG", "TOD", "SIB", "MCH"]:
                if locale in c.locales:
                    c.sub(
                        c.input(gLike(locale), c.conditions[f"{locale}:feminine"]),
                        c.glyphClass(
                            [
                                c.classes[f"{locale}-vowelFeminine"],
                                c.classes[f"{locale}-vowelNeuter"],
                            ]
                        ),
                        by=None,
                    )

            if "MNG" in c.locales:
                c.sub(
                    c.classes["MNG-vowelMasculine"],
                    c.input(gLike("MNG"), c.conditions["MNG:masculine_devsger"]),
                    by=None,
                )
                c.sub(
                    c.classes["MNG-vowelFeminine"],
                    c.input(gLike("MNG"), c.conditions["MNG:feminine"]),
                    by=None,
                )
            if "TOD" in c.locales:
                c.sub(
                    c.classes["TOD-vowel"],
                    c.input(c.classes["TOD-g"], c.conditions["TOD:masculine_devsger"]),
                    by=None,
                )
            if "SIB" in c.locales:
                c.sub(
                    c.input(c.classes["SIB-k"], c.conditions["SIB:devsger"]),
                    c.classes["SIB-consonant"],
                    by=None,
                )
                c.sub(
                    c.classes["SIB-vowel"],
                    c.input(c.classes["SIB-k.fina"], c.conditions["SIB:devsger"]),
                    by=None,
                )
            if "MCH" in c.locales:
                c.sub(
                    c.classes["MCH-t"],
                    c.classes["MCH-e"],
                    c.input(c.classes["MCH-k"], c.conditions["MCH:masculine_devsger"]),
                    by=None,
                )
                gLike = c.variants("MCH", ["k", "g", "h"])
                c.sub(
                    gLike,
                    c.classes["MCH-u"],
                    c.input(c.classes["MCH-k"], c.conditions["MCH:feminine"]),
                    by=None,
                )
                ghLike = c.variants("MCH", ["kh", "gh", "hh"])
                c.sub(
                    ghLike,
                    c.classes["MCH-a"],
                    c.input(c.classes["MCH-k"], c.conditions["MCH:feminine"]),
                    by=None,
                )
                c.sub(
                    c.variants("MCH", ["e", "ue"]),
                    c.input(c.classes["MCH-k"], c.conditions["MCH:feminine"]),
                    by=None,
                )
                c.sub(
                    c.variants("MCH", ["a", "i", "o", "u"]),
                    c.input(c.classes["MCH-k"], c.conditions["MCH:masculine_devsger"]),
                    by=None,
                )

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
            c.sub(
                c.classes["MNG-i"],
                c.input(gLike, c.conditions["MNG:masculine_devsger"]),
                MARKER_MASCULINE,
                by=None,
            )
            c.sub(
                c.classes["MNG-i"],
                c.input(c.classes["MNG-g"], c.conditions["MNG:feminine"]),
                by=None,
            )

        with c.Lookup(
            "III.g_h.onset_and_devsger_and_gender.B.MNG",
            feature="rclt",
            flags={"IgnoreMarks": True},
        ):
            c.sub(
                c.input(c.variants("MNG", ["h", "g"], init), c.conditions["MNG:feminine"]),
                c.classes["MNG-consonant"],
                by=None,
            )

        for index in [0, 1]:
            step = ["A", "B"][index]
            genderMarker = [MARKER_MASCULINE, MARKER_FEMININE][index]

            with c.Lookup(
                f"III.ig.post_processing.{step}.MNG",
                feature="rclt",
                flags={"UseMarkFilteringSet": c.glyphClass([genderMarker])},
            ):
                for alias in ["h", "g"]:
                    charName = getCharNameByAlias("MNG", alias)
                    for position in (init, medi, fina):
                        variants = data.variants[charName].get(position, {})
                        for i in variants.values():
                            variant = str(GlyphDescriptor.fromData(charName, position, i))
                            c.sub(variant, genderMarker, by=variant)


def iii2g(c: MongFeaComposer) -> None:
    """
    (1) When _t_ precedes _ee_ or consonant, apply `devsger`.

    (2) When _sh_ precedes _i_ and not in Twelve Syllabaries, apply `dotless`.

    (3) When _g_ follows _s_ or _d_, apply `dotless`.
    """

    if "MNG" in c.locales:
        with c.Lookup("III.t_sh_g.MNG.GB", feature="rclt", flags={"IgnoreMarks": True}):
            c.sub(
                c.input(c.classes["MNG-t"], c.conditions["MNG:devsger"]),
                c.variants("MNG", ["ee", "consonant"]),
                by=None,
            )
            c.sub(
                c.input(c.classes["MNG-sh.init"], c.conditions["MNG:dotless"]),
                c.classes["MNG-i.medi"],
                by=None,
            )
            c.sub(
                c.input(c.classes["MNG-sh.medi"], c.conditions["MNG:dotless"]),
                c.variants("MNG", "i", (medi, fina)),
                by=None,
            )
            c.sub(
                c.variants("MNG", ["s", "d"]),
                c.input(c.classes["MNG-g.medi"], c.conditions["MNG:dotless"]),
                c.classes["MNG-vowelMasculine"],
                by=None,
            )
            c.sub(
                c.variants("MNG", ["s", "d"]),
                c.input(c.classes["MNG-g.fina"], c.conditions["MNG:dotless"]),
                c.classes["mvs"],
                "u1820.Aa.isol",
                by=None,
            )


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
                for aliasString, indices in data.particles[locale].items():
                    aliasList = aliasString.split()
                    hasMvs = aliasList[0] == "mvs"
                    if hasMvs:
                        aliasList = aliasList[1:]
                        indices = [index - 1 for index in indices]
                    classList = []

                    classList = [
                        c.classes[f"{locale}-{alias}.{getPosition(index, len(aliasList))}"]
                        for index, alias in enumerate(aliasList)
                    ]

                    subArgs: list = (
                        [c.input(c.classes["mvs"], c.conditions["_.wide"])] if hasMvs else []
                    )
                    ignoreSubArgs: list = [c.input(c.classes["mvs"])] if hasMvs else []
                    minIndex = 0 if hasMvs else min(indices)
                    for i, glyphClass in enumerate(classList):
                        if i in indices:
                            subArgs.append(c.input(glyphClass, c.conditions[f"{locale}:particle"]))
                            ignoreSubArgs.append(c.input(glyphClass))
                        elif minIndex <= i <= max(indices):
                            subArgs.append(c.input(glyphClass))
                            ignoreSubArgs.append(c.input(glyphClass))
                        else:
                            subArgs.append(glyphClass)
                            ignoreSubArgs.append(glyphClass)
                    c.sub(*ignoreSubArgs, c.classes["fvs"], by=None)
                    c.sub(*subArgs, by=None)

    if "TOD" in c.locales:
        with c.Lookup("TOD:particle") as _particle:
            c.sub(c.classes["TOD-n.init"], by="u1828.N.init.mvs")

        with c.Lookup("III.particle.TOD", feature="rclt", flags={"IgnoreMarks": True}):
            c.sub(
                c.input(c.classes["mvs"], c.conditions["_.wide"]),
                c.input(c.classes["TOD-n.init"], _particle),
                c.classes["TOD-i.fina"],
                by=None,
            )

    if "MNG" in c.locales:
        with c.Lookup("III.mvs.postprocessing.GB", feature="rclt"):
            c.sub(
                c.input(c.classes["mvs.invalid"], c.conditions["_.wide"]),
                c.glyphClass(
                    [
                        c.classes["MNG-vowel"],
                        c.classes["MNG-consonant"],
                        "nirugu",
                        "nirugu.ignored",
                    ]
                ),
                by=None,
            )


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
                vowelVariants = c.namedGlyphClass(
                    "MNG-vowel.not_ending_with_I",
                    c.writtens(
                        "MNG", lambda x: x[-1] != "I", (init, medi), categories["vowel"]
                    ).glyphs,
                )
                c.sub(
                    vowelVariants,
                    c.input(c.classes["MNG-i"], c.conditions["MNG:vowel_devsger"]),
                    by=None,
                )
            if "TOD" in c.locales:
                c.sub(
                    c.classes["TOD-vowel"],
                    c.input(c.classes["TOD-i"], c.conditions["TOD:vowel_devsger"]),
                    by=None,
                )
                c.sub(
                    c.classes["TOD-u"],
                    c.input(c.classes["TOD-u"], c.conditions["TOD:vowel_devsger"]),
                    by=None,
                )
            if "SIB" in c.locales:
                c.sub(
                    c.classes["SIB-vowel"],
                    c.input(c.classes["SIB-i"], c.conditions["SIB:vowel_devsger"]),
                    by=None,
                )
                c.sub(
                    c.classes["SIB-vowel"],
                    c.input(c.classes["SIB-u"], c.conditions["SIB:vowel_devsger"]),
                    by=None,
                )
            if "MCH" in c.locales:
                c.sub(
                    c.classes["MCH-vowel"],
                    c.input(c.classes["MCH-i"], c.conditions["MCH:vowel_devsger"]),
                    by=None,
                )
            if "MCHx" in c.locales:
                c.sub(
                    c.classes["MCHx-vowel"],
                    c.input(c.classes["MCHx-u"], c.conditions["MCHx:vowel_devsger"]),
                    by=None,
                )

    if "MNG" in c.locales:
        with c.Lookup(
            "III.i.devsger.MNG.GB",
            feature="rclt",
            flags={"UseMarkFilteringSet": c.classes["fvs"]},
        ):
            c.sub(
                c.variants("MNG", ["oe", "ue"], medi),
                c.glyphClass([c.classes["fvs1"], c.classes["fvs2"]]),
                c.input(c.variants("MNG", "i", (medi, fina)), c.conditions["MNG:reset"]),
                by=None,
            )
            c.sub(
                c.variants("MNG", ["oe", "ue"], medi),
                c.classes["fvs3"],
                c.input(c.classes["MNG-i"], c.conditions["MNG:vowel_devsger"]),
                by=None,
            )
            c.sub(
                c.classes["MNG-ue.init"],
                c.classes["fvs2"],
                c.input(c.variants("MNG", "i", (medi, fina)), c.conditions["MNG:reset"]),
                by=None,
            )
            c.sub(
                c.classes["MNG-ue.init"],
                c.classes["fvs1"],
                c.input(c.classes["MNG-i"], c.conditions["MNG:vowel_devsger"]),
                by=None,
            )


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
            c.sub(bowed, c.input(c.glyphClass(["u1825.Ue.fina", "u1826.Ue.fina"])), by=None)
            c.sub(
                bowed,
                c.input(
                    c.variants("MNG", ["o", "u", "oe", "ue"], fina),
                    c.conditions["MNG:post_bowed"],
                ),
                by=None,
            )
            c.sub(
                c.glyphClass([bowedB, bowedK]),
                c.input(c.variants("MNG", ["a", "e"], fina), c.conditions["MNG:post_bowed"]),
                by=None,
            )
            c.sub(
                bowedG,
                c.input(c.variants("MNG", "e", fina), c.conditions["MNG:post_bowed"]),
                by=None,
            )

        with c.Lookup("III.fvs.post_bowed.preprocessing.GB", feature="rclt"):
            c.sub(
                c.glyphClass([bowedB, bowedK, bowedG]),
                c.input(c.classes["fvs.ignored"], c.conditions["_.reset"]),
                by=None,
            )

        with c.Lookup("III.vowel.post_bowed.MNG.GB", feature="rclt", flags={"IgnoreMarks": True}):
            hgVariants = c.variants("MNG", ["h", "g"])
            c.sub(
                hgVariants,
                c.glyphClass([c.classes["fvs2"], c.classes["fvs4"]]),
                c.input(c.classes["MNG-e.fina"], c.conditions["MNG:post_bowed"]),
                by=None,
            )
            c.sub(
                hgVariants,
                c.glyphClass([c.classes["fvs1"], c.classes["fvs3"]]),
                c.input(c.classes["MNG-e.fina"], c.conditions["MNG:reset"]),
                by=None,
            )
            c.sub(
                c.variants("MNG", ["b", "p", "f", "k", "k2"], init),
                c.classes["fvs"],
                c.input(c.variants("MNG", ["oe", "ue"], fina), c.conditions["MNG:marked"]),
                by=None,
            )
            c.sub(
                hgVariants,
                c.glyphClass([c.classes["fvs1"], c.classes["fvs3"]]),
                c.input(c.variants("MNG", ["o", "u", "oe", "ue"], fina), c.conditions["MNG:reset"]),
                by=None,
            )
            c.sub(
                c.variants("MNG", ["g", "h"], (init, medi)),
                c.glyphClass([c.classes["fvs2"], c.classes["fvs4"]]),
                c.input(c.variants("MNG", ["o", "u"], fina), c.conditions["MNG:reset"]),
                by=None,
            )
            c.sub(
                c.variants("MNG", ["g", "h"], medi),
                c.glyphClass([c.classes["fvs2"], c.classes["fvs4"]]),
                c.input(c.variants("MNG", ["oe", "ue"], fina), c.conditions["MNG:post_bowed"]),
                by=None,
            )
            c.sub(
                c.variants("MNG", ["g", "h"], init),
                c.glyphClass([c.classes["fvs2"], c.classes["fvs4"]]),
                c.input(c.variants("MNG", ["oe", "ue"], fina), c.conditions["MNG:marked"]),
                by=None,
            )

        with c.Lookup("III.fvs.post_bowed.postprocessing.GB", feature="rclt"):
            c.sub(
                c.glyphClass([bowedB, bowedK, bowedG]),
                c.input(c.classes["fvs.invalid"], c.conditions["_.ignored"]),
                by=None,
            )

    if "MNGx" in c.locales:
        bowedB = c.namedGlyphClass("MNGx-bowedB", c.variants("MNGx", ["pX", "phX", "b"]).glyphs)
        bowedK = c.namedGlyphClass("MNGx-bowedK", c.variants("MNGx", ["kX", "k2", "k"]).glyphs)
        with c.Lookup("III.vowel.post_bowed.MNGx", feature="rclt", flags={"IgnoreMarks": True}):
            bowed = c.glyphClass([bowedB, bowedK])
            vowels = ["a", "o", "ue"]
            c.sub(
                bowed,
                c.input(c.variants("MNGx", vowels, fina), c.conditions["MNGx:post_bowed"]),
                by=None,
            )
            c.sub(c.classes["MNGx-waX"], c.input(c.classes["MNGx-a"]), by="u1820.Aa.isol.post_wa")

    if "TOD" in c.locales:
        bowedB = c.namedGlyphClass("TOD-bowedB", c.variants("TOD", ["b", "p"]).glyphs)
        bowedK = c.namedGlyphClass("TOD-bowedK", c.variants("TOD", ["kh", "gh"]).glyphs)
        bowedG = c.namedGlyphClass("TOD-bowedG", c.writtens("TOD", ["K", "G"]).glyphs)
        with c.Lookup("III.vowel.post_bowed.TOD", feature="rclt", flags={"IgnoreMarks": True}):
            bowed = c.glyphClass([bowedB, bowedK, bowedG])
            vowels = ["a", "i", "u", "ue"]
            c.sub(
                bowed,
                c.input(c.variants("TOD", vowels, fina), c.conditions["TOD:post_bowed"]),
                by=None,
            )

            c.sub(bowed, c.input(c.classes["TOD:a_lvs.fina"]), by="u1820_u1843.AaLv.fina")

    if "TODx" in c.locales:
        bowedB = c.namedGlyphClass(
            "TODx-bowedB",
            c.variants("TODx", ["pX", "p", "b"]).glyphs,
        )
        bowedK = c.namedGlyphClass(
            "TODx-bowedK",
            c.variants("TODx", ["kX", "khX", "gX"]).glyphs,
        )
        with c.Lookup("III.vowel.post_bowed.TODx", feature="rclt", flags={"IgnoreMarks": True}):
            bowed = c.glyphClass([bowedB, bowedK])
            vowels = ["a", "i", "ue"]
            c.sub(
                bowed,
                c.input(c.variants("TODx", vowels, fina), c.conditions["TODx:post_bowed"]),
                by=None,
            )

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
                f"{locale}-bowedG", c.writtens(locale, ["G", "Gx", "Gh", "Gc"]).glyphs
            )
            with c.Lookup(
                f"III.vowel.post_bowed.{locale}", feature="rclt", flags={"IgnoreMarks": True}
            ):
                c.sub(
                    c.glyphClass([bowedB, bowedG]),
                    c.input(c.variants(locale, ["e", "u"]), c.conditions[f"{locale}:post_bowed"]),
                    by=None,
                )
                c.sub(
                    c.glyphClass([bowedB, bowedK]),
                    c.input(c.variants(locale, ["a", "o"]), c.conditions[f"{locale}:post_bowed"]),
                    by=None,
                )

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
            c.writtens("MCHx", ["G", "Gh", "Gc"]).glyphs,
        )
        with c.Lookup("III.vowel.post_bowed.MCHx", feature="rclt", flags={"IgnoreMarks": True}):
            c.sub(
                c.glyphClass([bowedB, bowedG, c.classes["MCHx-ghX"]]),
                c.input(c.variants("MCHx", ["e", "u"]), c.conditions["MCHx:post_bowed"]),
                by=None,
            )
            c.sub(
                c.glyphClass([c.classes["MCHx-ngX"], c.classes["MCHx-sbm"]]),
                c.input(c.classes["MCHx-e"], c.conditions["MCHx:post_bowed"]),
                by=None,
            )
            c.sub(
                c.glyphClass([bowedB, bowedK]),
                c.input(c.variants("MCHx", ["a", "o"]), c.conditions["MCHx:post_bowed"]),
                by=None,
            )


def iii6(c: MongFeaComposer) -> None:
    """
    **Phase III.6: Uncaptured - FVS-selected**

    (1) Apply `manual` for letters preceding FVS.

    (2) Apply `manual` for letters preceding FVS that precedes LVS for Todo and Todo Ali Gali.

    (3) Apply `manual` for punctuation.
    """

    for locale in c.locales:
        with c.Lookup(f"_.manual.{locale}") as _lvs:
            for alias in getAliasesByLocale(locale):
                charName = getCharNameByAlias(locale, alias)
                letter = locale + "-" + alias
                for position, variants in data.variants[charName].items():
                    glyphClass = c.classes[letter + "." + position]
                    for fvs, variant in variants.items():
                        if fvs != 0 and locale in variant.locales:
                            variant = str(GlyphDescriptor.fromData(charName, position, variant))
                            c.sub(c.input(glyphClass), f"fvs{fvs}.ignored", by=variant)

        with c.Lookup(f"III.fvs.{locale}", feature="rclt"):
            for alias in getAliasesByLocale(locale):
                charName = getCharNameByAlias(locale, alias)
                letter = locale + "-" + alias
                for position, variants in data.variants[charName].items():
                    glyphClass = c.classes[letter + "." + position]
                    for fvs in variants:
                        if fvs != 0:
                            c.sub(
                                c.input(glyphClass, _lvs),
                                c.input(f"fvs{fvs}.ignored", c.conditions["_.valid"]),
                                by=None,
                            )

    if "TOD" in c.locales:
        with c.Lookup("_.manual.lvs.TOD") as _lvs:
            c.sub(c.input(c.classes["TOD-a_lvs.isol"]), "fvs1.ignored", by="u1820_u1843.ALv.isol")
            c.sub(c.input(c.classes["TOD-a_lvs.isol"]), "fvs3.ignored", by="u1820_u1843.AALv.isol")
            c.sub(c.input(c.classes["TOD-a_lvs.init"]), "fvs2.ignored", by="u1820_u1843.AALv.init")
            c.sub(c.input(c.classes["TOD-a_lvs.fina"]), "fvs1.ignored", by="u1820_u1843.AaLv.fina")
            c.sub(c.input(c.classes["TOD-a_lvs.fina"]), "fvs2.ignored", by="u1820_u1843.AaLv.fina")
        with c.Lookup("III.fvs.lvs.TOD"):
            c.sub(
                c.input(c.classes["TOD-a_lvs.isol"], _lvs),
                c.input("fvs1.ignored", c.conditions["_.valid"]),
                by=None,
            )
            c.sub(
                c.input(c.classes["TOD-a_lvs.isol"], _lvs),
                c.input("fvs3.ignored", c.conditions["_.valid"]),
                by=None,
            )
            c.sub(
                c.input(c.classes["TOD-a_lvs.init"], _lvs),
                c.input("fvs2.ignored", c.conditions["_.valid"]),
                by=None,
            )
            c.sub(
                c.input(c.classes["TOD-a_lvs.fina"], _lvs),
                c.input("fvs1.ignored", c.conditions["_.valid"]),
                by=None,
            )
            c.sub(
                c.input(c.classes["TOD-a_lvs.fina"], _lvs),
                c.input("fvs2.ignored", c.conditions["_.valid"]),
                by=None,
            )

    if "TODx" in c.locales:
        with c.Lookup("_.manual.lvs.TODx") as _lvs:
            c.sub(
                c.input(c.classes["TODx-i_lvs.fina"]),
                "fvs1.ignored",
                by="u1845_u1843.IpLv.fina",
            )
            c.sub(
                c.input(c.classes["TODx-i_lvs.fina"]),
                "fvs2.ignored",
                by="u1845_u1843.I3Lv.fina",
            )
            c.sub(
                c.input(c.classes["TODx-ue_lvs.fina"]),
                "fvs1.ignored",
                by="u1849_u1843.OLv.fina",
            )
            c.sub(
                c.input(c.classes["TODx-ue_lvs.fina"]),
                "fvs2.ignored",
                by="u1849_u1843.ULv.fina",
            )
        with c.Lookup("III.fvs.lvs.TODx"):
            c.sub(
                c.input(c.classes["TODx-i_lvs.fina"], _lvs),
                c.input("fvs1.ignored", c.conditions["_.valid"]),
                by=None,
            )
            c.sub(
                c.input(c.classes["TODx-i_lvs.fina"], _lvs),
                c.input("fvs2.ignored", c.conditions["_.valid"]),
                by=None,
            )
            c.sub(
                c.input(c.classes["TODx-ue_lvs.fina"], _lvs),
                c.input("fvs1.ignored", c.conditions["_.valid"]),
                by=None,
            )
            c.sub(
                c.input(c.classes["TODx-ue_lvs.fina"], _lvs),
                c.input("fvs2.ignored", c.conditions["_.valid"]),
                by=None,
            )

    if "MNGx" in c.locales:
        with c.Lookup("_.manual.punctuation") as _lvs:
            c.sub(c.input("u1880"), "fvs1.ignored", by="u1880.fvs1")
            c.sub(c.input("u1881"), "fvs1.ignored", by="u1881.fvs1")

        with c.Lookup("III.fvs.punctuation", feature="rclt"):
            c.sub(
                c.input("u1880", _lvs),
                c.input("fvs1.ignored", c.conditions["_.valid"]),
                by=None,
            )
            c.sub(
                c.input("u1881", _lvs),
                c.input("fvs1.ignored", c.conditions["_.valid"]),
                by=None,
            )

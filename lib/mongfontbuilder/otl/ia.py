from . import MongFeaComposer


def compose(c: MongFeaComposer) -> None:
    """
    **Phase Ia.1: Basic character-to-glyph mapping**

    This phase is empty. It held the substitution of NNBSP for MVS that Unicode Version
    16.0 asks for, since the function of the nnbsp is the one the MVS has and the two are
    shaped alike. That substitution turned *every* nnbsp into an MVS, so the glyph the
    source font draws for the character could never be written — wrong for an nnbsp that
    stands alone, which is a space and not the separator between two words.

    The two are shaped alike without it: `@mvs`, `@mvs.invalid` and `@mvs.valid` each hold
    the nnbsp beside the glyphs of the MVS, so every lookup of the phases below shapes an
    nnbsp as it shapes an MVS. What nothing then shaped is written as the glyph of the
    character by Phase III.7, which is the phase that can tell the two apart.
    """

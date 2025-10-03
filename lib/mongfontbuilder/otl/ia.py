from . import MongFeaComposer


def compose(c: MongFeaComposer) -> None:
    """
    **Phase Ia.1: Basic character-to-glyph mapping**

    Since Unicode Version 16.0, NNBSP has been taken over by MVS, which participate in chachlag and particle shaping.
    """

    with c.Lookup("Ia.nnbsp.preprocessing", feature="ccmp"):
        c.sub("nnbsp", by="mvs")

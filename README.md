# Mongolian Font Builder

The Mongolian Font Builder project consists of:

- **Documentation and data files** that clarify the encoding and shaping rules required for a font to be compatible with the Unicode Standard and China’s national standard GB/T 25914-2023.
  - Stabilized versions of the documentation will be published as revisions of [UTN \#57, Encoding and Shaping of the Mongolian Script](https://www.unicode.org/notes/tn57/) (the **Mongolian UTN**).
- **Tooling**, as a Python package `mongfontbuilder`, that helps font designers and developers produce a standard-compatible Mongolian script font, as clarified by the documentation.
  - It also acts as the reference implementation of the Mongolian UTN.
- **Templates** for generating fonts in Glyphs app from the tooling’s output.
- **Tests** for validating fonts produced by the tooling across multiple Mongolian writing systems (Hudum, Sibe, Manchu).

## Documentation and data files

The documentation is maintained in [web/docs/](https://github.com/Kushim-Jiang/mongfontbuilder/blob/main/web/docs) and deployed to [mongfontbuilder.pages.dev](https://mongfontbuilder.pages.dev/). For contribution guidelines, refer to [CONTRIBUTING.md](https://github.com/Kushim-Jiang/mongfontbuilder/blob/main/CONTRIBUTING.md).

The source-of-truth data files are maintained as TypeScript files in [data/](https://github.com/Kushim-Jiang/mongfontbuilder/blob/main/data). They’re exported to JSON in [lib/mongfontbuilder/data/](https://github.com/Kushim-Jiang/mongfontbuilder/tree/main/lib/mongfontbuilder/data) for consumption of the Python API.

## Tooling

The Python package `mongfontbuilder` is maintained in [lib/](https://github.com/Kushim-Jiang/mongfontbuilder/blob/main/lib) and published to [PyPI](https://pypi.org/project/mongfontbuilder/). To install the package in terminal:

```sh
pip install mongfontbuilder
```

This package includes various utilities, including:

- Python API for the data files.
- Dynamic generation of OpenType Layout rules.
- Construction of a complete font from a minimal glyph set.

A CLI is also available — it reads a source UFO font and writes a complete font with the generated OTL rules:

```sh
uv run python -m mongfontbuilder input.ufo output.otf --locales MNG
```

Both `.ufo` and `.otf` output formats are supported. See `--help` for available locales.

## Templates

Maintained in [templates/](https://github.com/Kushim-Jiang/mongfontbuilder/blob/main/templates).

The tooling can generate [Glyphs](https://glyphsapp.com/) templates (`.glyphs` files) from the UFO test fonts and the OTL composer output. These templates let type designers open and work with the generated glyph layout directly in Glyphs app.

The template update script is at [`templates/update.py`](https://github.com/Kushim-Jiang/mongfontbuilder/blob/main/templates/update.py). Currently available templates:

- `hudum.glyphs` — Hudum (MNG) template.
- `manchu.glyphs` — Manchu (MCH) template.

Template tests are macOS-only (require Glyphs app) and located in [`tests/test_templates.py`](https://github.com/Kushim-Jiang/mongfontbuilder/blob/main/tests/test_templates.py).

## Tests

Maintained in [tests/](https://github.com/Kushim-Jiang/mongfontbuilder/blob/main/tests).

Tests are organized per writing system with separate test fonts:

- **Hudum** (`MNG`): validated against the EAC and core test suites (`eac-hud`, `core-hud`).
- **Manchu** (`MCH`): validated against the core test suite (`core-man`).
- **Sibe** (`SIB`): validated against the core test suite (`core-sib`).

The test harness builds each font on the fly using `mongfontbuilder`’s Python API directly, then shapes the test input strings with [HarfBuzz](https://harfbuzz.github.io/) and compares the resulting glyph sequence against expected output.

### Cases the EAC expects differently

The EAC suite is settled by the Hudum standard alone. Where the UTN model disagrees with it, the case is marked as an expected failure — it is kept in the suite, and the reason is kept in [`tests/fixtures.py`](https://github.com/Kushim-Jiang/mongfontbuilder/blob/main/tests/fixtures.py) — so that the run stays green and the disagreement stays visible.

A font that writes with every writing system at once (`test_unified.py`) is the one that has to be marked for the cases below: the meeting held that the effect of an FVS does not depend on the locale, so the FVS stays valid and selects its variant wherever the character is shared. A font that writes with one writing system answers them as the EAC expects.

- `MND11-2`, `MNM10-2`, `MNM11-2`, `MNS11-26`, `MNZ11-3`, `MNZ21-5`, `XIM11-11`, `XIM11-675`, `XIM11-678`, `XIM11-681`, `XIM11-684`, `XIM11-687`, `XIM11-690`, `XIM11-694`

`XIM11-46` (`e n fvs3 mvs e`) is answered differently by every font as well, but for a reason of its own: the FVS3 follows the _n_, and the UTN model draws the form it selects rather than the one the EAC expects.

The cases below are marked for every font, because the UTN model answers them differently from the EAC in a way that does not depend on which writing systems a font carries.

- `XIM11-39`, `XIM11-40`, `XIM11-41` — the UTN model keeps the old functionality of NNBSP, so the features of NNBSP stay on.
- `XIM11-1012` — a letter before an MVS is in the final position, so the FVS after it selects the final variant.

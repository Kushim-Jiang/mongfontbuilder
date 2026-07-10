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

Currently the following EAC Hudum test cases are expected to fail:

- `eac-hud > XIM11-39`, `eac-hud > XIM11-40`, `eac-hud > XIM11-41`
  - The EAC spec assumes that all features of NNBSP should be disabled. The UTN model considers this test case incorrect. The UTN model considers that the old functionality of NNBSP should be retained.
- `eac-hud > XIM11-46`
  - The EAC spec expects an invalid FVS after a letter to prevent the MVS shaping step. The UTN model disagrees.
- `eac-hud > XIM11-1012`
  - When an FVS after a letter prevents the MVS shaping step, the MVS is treated as an NBSP. In this case, the FVS remains valid. The UTN model considers this test case incorrect.
- `eac-hud > MSM11-2`, `eac-hud > XIM11-16`
  - The currently exported font does not yet account for shaping rules based on locale, resulting in these two tests failing. Future efforts will focus on resolving this issue to pass both tests.

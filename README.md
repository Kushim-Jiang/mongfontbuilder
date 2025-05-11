# Mongolian Font Builder

The Mongolian Font Builder project consists of:

- **Documentation and data files** that clarify the encoding and shaping rules required for a font to be compatible with the Unicode Standard and China’s national standard GB/T 25914-2023.
  - Stabilized versions of the documentation will be published as revisions of [UTN \#57, Encoding and Shaping of the Mongolian Script](https://www.unicode.org/notes/tn57/) (the **Mongolian UTN**).
- **Tooling**, as a Python package `mongfontbuilder`, that helps font designers and developers produce a standard-compatible Mongolian script font, as clarified by the documentation.
  - It also acts the reference implementation of the Mongolian UTN.
- **Tests** for validating fonts produced by the tooling.

## Documentation and data files

The documentation is maintained in [web/docs/](https://github.com/Kushim-Jiang/mongfontbuilder/blob/main/web/docs) and deployed to [mongolian-utn.pages.dev](https://mongolian-utn.pages.dev). For contribution guidelines, refer to [CONTRIBUTING.md](https://github.com/Kushim-Jiang/mongfontbuilder/blob/main/CONTRIBUTING.md).

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

## Tests

Maintained in [tests/](https://github.com/Kushim-Jiang/mongfontbuilder/blob/main/tests).

Currently the following EAC test cases are expected to fail:

- `eac-hud > XIM11-46`
  - The EAC spec expects an invalid FVS after a letter to prevent the MVS shaping step. The UTN model disagrees.
- `eac-hud > XIM11-47`
- `eac-hud > XIM11-48`
- `eac-hud > XIM11-49`
  - The current test font does not include the glyphs `one`, `two`, `three`, and `alatin`.
- `eac-hud > XIM11-1012`
  - When an FVS after a letter prevents the MVS shaping step, the MVS is treated as an NBSP. In this case, the FVS remains valid. The UTN model considers this test case incorrect.

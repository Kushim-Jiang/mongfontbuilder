# Mongolian Font Builder

## Overview

Mongolian Font Builder is a comprehensive toolchain for constructing, shaping, and testing Mongolian script fonts. It provides a Python package, detailed documentation, and structured data to support font development and testing.

## Tooling

The core Python package, `mongfontbuilder`, is located in the [lib](https://github.com/Kushim-Jiang/mongfontbuilder/blob/main/lib) directory. It includes utilities for font construction, shaping rule implementation, and data processing.

The [tests](https://github.com/Kushim-Jiang/mongfontbuilder/blob/main/tests) directory contains examples and test cases. While it is not part of the package, it can be referred to when writing code.

> It is known that the following EAC test cases may fail:
>
> - `eac-hud > XIM11-46`
>   - EAC believes that an invalid FVS after a letter prevents this MVS shaping step, but UTN disagrees.
> - `eac-hud > XIM11-47`
> - `eac-hud > XIM11-48`
> - `eac-hud > XIM11-49`
>   - This font does not include the characters `one`, `two`, `three`, and `alatin` by default.
> - `eac-hud > XIM11-1012`
>   - When an FVS after a letter prevents the MVS shaping step, the MVS is treated as an NBSP. In this case, the FVS remains valid. UTN considers this test case incorrect.

To install the package (can be done using PowerShell or any terminal):

```powershell
pip install mongfontbuilder
```

## Documentation

The project documentation is maintained in the [docs](https://github.com/Kushim-Jiang/mongfontbuilder/blob/main/docs) directory. While it is not part of the Python package, it is built using [Astro](https://astro.build/) and [Svelte](https://svelte.dev/). It serves as a draft for the Mongolian UTN ([UTN \#57: Encoding and Shaping of the Mongolian Script](https://www.unicode.org/notes/tn57/)). The latest editor’s draft is available at [mongolian-utn.pages.dev/](https://mongolian-utn.pages.dev/).

For contribution guidelines, refer to [CONTRIBUTING.md](CONTRIBUTING.md).

## Data

The source data for the UTN is maintained in the [data](https://github.com/Kushim-Jiang/mongfontbuilder/blob/main/data) directory. This data is exported to [lib/mongfontbuilder/data](https://github.com/Kushim-Jiang/mongfontbuilder/tree/main/lib/mongfontbuilder/data) directory for use in the Python package.

## License

This project is licensed under the MIT License.

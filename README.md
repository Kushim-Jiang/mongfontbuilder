# Mongolian Font Builder

## Overview

Mongolian Font Builder is a comprehensive toolchain for constructing, shaping, and testing Mongolian script fonts. It provides a Python package, detailed documentation, and structured data to support font development and testing.

## Tooling

The core Python package, `mongfontbuilder`, is located in the [lib/](lib/) directory. It includes utilities for font construction, shaping rule implementation, and data processing.

The [tests/](tests/) directory contains examples and test cases. While it is not part of the package, it can be referred to when writing code.

To install the package (can be done using PowerShell or any terminal):

```powershell
pip install mongfontbuilder
```

## Documentation

The project documentation is maintained in the [docs/](docs/) directory. While it is not part of the Python package, it is built using [Astro](https://astro.build/) and [Svelte](https://svelte.dev/). It serves as a draft for the Mongolian UTN ([UTN \#57: Encoding and Shaping of the Mongolian Script](https://www.unicode.org/notes/tn57/)). The latest editor’s draft is available at [mongolian-utn.pages.dev/](https://mongolian-utn.pages.dev/).

For contribution guidelines, refer to [CONTRIBUTING.md](CONTRIBUTING.md).

## Data

The source data for the UTN is maintained in the [data/](data/) directory. This data is exported to [lib/mongfontbuilder/data.json](/lib/mongfontbuilder/data.json) for use in the Python package.

## License

This project is licensed under the MIT License.

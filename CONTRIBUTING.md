# Contributing Guide

## Contributing to the Python Package

1. Set up the development environment using [Poetry](https://python-poetry.org/):

   ```sh
   poetry install
   poetry env use python
   poetry env activate
   ```

2. Write tests to verify your changes.

Unfinished tasks or ideas can be added as [issues](https://github.com/Kushim-Jiang/mongfontbuilder/issues).

## Contributing to the Documentation

[![Built with Starlight](https://astro.badg.es/v2/built-with-starlight/tiny.svg)](https://starlight.astro.build)

1. Install dependencies:

   ```sh
   npm install
   ```

2. Start a local development server:

   ```sh
   npm run dev
   ```

Starlight looks for `.md` or `.mdx` files in the [docs/](docs/) directory. Each file is exposed as a route based on its file name. The `.mdx` files can include Svelte code, and standalone functions can be maintained as reusable components.

Images can be added to [web/src/](web/src/) and embedded in Markdown using relative links. And static assets, such as favicons, can be placed in [web/public/](web/public/).

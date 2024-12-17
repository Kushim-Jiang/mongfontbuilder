# Mongolian UTN

See also:

- [Kushim-Jiang/Mongolian](https://github.com/Kushim-Jiang/Mongolian)
- [Kushim-Jiang/mongolian-private](https://github.com/Kushim-Jiang/mongolian-private)

## Data

The source of truth of the UTN’s data is maintained in the [data](data/) directory, which is then exported to [lib/mongfontbuilder/data.json](/lib/mongfontbuilder/data.json) for consuming from Python.

## Web version

[![Built with Starlight](https://astro.badg.es/v2/built-with-starlight/tiny.svg)](https://starlight.astro.build)

Once you’ve installed dependencies with `npm install`, start a local development server:

```sh
npm run dev
```

Starlight looks for .md or .mdx files in [web/src/content/docs/](web/src/content/docs/). Each file is exposed as a route based on its file name.

Images can be added to [web/src/assets/](web/src/assets/) and embedded in Markdown with a relative link.

Static assets, like favicons, can be placed in [web/src/public/](web/src/public/).

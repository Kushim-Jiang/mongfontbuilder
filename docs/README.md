# Mongolian UTN

[![Built with Starlight](https://astro.badg.es/v2/built-with-starlight/tiny.svg)](https://starlight.astro.build)

Once you’ve installed dependencies with `npm install`, start a development server:

```sh
npm run dev
```

Starlight looks for .md or .mdx files in the “src/content/docs/” directory. Each file is exposed as a route based on its file name.

Images can be added to “src/assets/” and embedded in Markdown with a relative link.

Static assets, like favicons, can be placed in the “public/” directory.

## Data

The source of truth of the UTN’s data is [data.ts](data.ts), which is then exported to [/mongfontbuilder/data.json](/mongfontbuilder/data.json) for Python’s consumption.

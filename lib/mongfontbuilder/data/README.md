# Data

- characters.yaml: Unicode charater to joining position to FVS to variant (in written units).
    - `.fabricated` values are views of the existence of `.fabricated` attribute inside “locales” data files.
- representative-glyphs.yaml: Recommended glyph forms for cmap.
    - To be merged into characters.yaml as the `.nominal` attribute.
- glyphs/: Glyphs used in shaping logic.
- locales/: Locale-specific categorization and metadata of phonetic letters.

> `.nominal` and `.fabricated` attributes, when their value is `null`, are meant to be interpreted like HTML [boolean attributes](https://developer.mozilla.org/en-US/docs/Glossary/Boolean/HTML).

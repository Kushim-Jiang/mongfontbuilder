from importlib.resources import files

import mongfontbuilder
import yaml
from tptq.feacomposer.utils import GlyphNameProcessingParser

names = set[str]()

path = files(mongfontbuilder) / "otl" / "main.fea"
with path.open(encoding="utf-8") as f:
    parser = GlyphNameProcessingParser(f, lambda x: names.add(x) or x)
parser.parse()

path = files(mongfontbuilder) / "data" / "glyphs"

all_glyphs = {}
for file in path.iterdir():
    with file.open(encoding="utf-8") as f:
        glyphs = yaml.safe_load(f)
        all_glyphs.update(glyphs)

for name in sorted(names):
    if name not in all_glyphs:
        print(f"Missing glyph: {name}")

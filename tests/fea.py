from importlib.resources import files

import mongfontbuilder
from tptq.feacomposer.utils import GlyphNameProcessingParser

names = set[str]()

path = files(mongfontbuilder) / "otl" / "main.fea"
with path.open(encoding="utf-8") as f:
    parser = GlyphNameProcessingParser(f, lambda x: names.add(x) or x)
parser.parse()

print(sorted(names))

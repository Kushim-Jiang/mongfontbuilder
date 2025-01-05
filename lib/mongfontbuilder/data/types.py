from dataclasses import dataclass, field

from cattrs import register_structure_hook

from .constants import JoiningPosition, joiningPositions

WrittenUnitID = str


@dataclass
class WrittenUnitVariant:
    archaic: bool = False


LocaleID = str
Condition = str


@dataclass
class Locale:
    conditions: list[Condition]
    categories: dict[str, list[str]]


CharacterName = str
Alias = str | dict[LocaleID, str]
register_structure_hook(Alias, lambda x, _: x)

FVS = int
VariantReference = tuple[JoiningPosition, FVS, LocaleID | None]
Written = list[WrittenUnitID] | VariantReference
structureWritten = lambda x, _: tuple(x) if x[0] in joiningPositions else x
register_structure_hook(Written, structureWritten)
register_structure_hook(Written | None, lambda x, _: structureWritten(x, None) if x else None)


@dataclass
class VariantLocaleData:
    written: Written | None = None
    conditions: list[Condition] = field(default_factory=list)
    gb: str = ""
    eac: str = ""


@dataclass
class Variant:
    written: Written
    locales: dict[LocaleID, VariantLocaleData]

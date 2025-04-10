from dataclasses import dataclass, field
from typing import Literal, NamedTuple

from cattrs import register_structure_hook

from .misc import JoiningPosition, joiningPositions

WrittenUnitID = str
LocaleID = Literal["MNG", "MNGx", "TOD", "TODx", "SIB", "MCH", "MCHx"]
Condition = str
CharacterName = str
FVS = int

LocaleNamespace = Literal["MNG", "TOD", "SIB", "MCH"]
AliasData = str | dict[LocaleNamespace, str]
register_structure_hook(AliasData, lambda x, _: x)


@dataclass
class LocaleData:
    conditions: list[Condition]
    categories: dict[str, list[str]]


class VariantReference(NamedTuple):
    position: JoiningPosition
    fvs: FVS
    locale: LocaleID | None = None


Written = list[WrittenUnitID] | VariantReference
_structureWritten = lambda x, _: VariantReference(*x) if x[0] in joiningPositions else x
register_structure_hook(Written, _structureWritten)
register_structure_hook(Written | None, lambda x, _: _structureWritten(x, None) if x else None)


@dataclass
class VariantLocaleData:
    written: Written | None = None
    conditions: list[Condition] = field(default_factory=list)
    archaic: bool = False
    gb: str = ""
    eac: str = ""
    lvs: bool = False


@dataclass
class VariantData:
    written: Written
    default: bool = False
    locales: dict[LocaleID, VariantLocaleData] = field(default_factory=dict)

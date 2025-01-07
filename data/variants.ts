import type { LocaleID, Condition } from "./locales";
import type { WrittenUnitID } from "./writtenUnits";
import type { CharacterName, JoiningPosition } from "./misc";

export type FVS = 0 | 1 | 2 | 3 | 4;

type Variant = {
  written: Written;
  locales: Partial<Record<LocaleID, VariantLocaleData>>;
};
type VariantLocaleData = {
  written?: Written;
  conditions?: Condition[];
  gb?: string;
  eac?: string;
};
type Written = WrittenUnitID[] | VariantReference;
type VariantReference = [
  position: JoiningPosition,
  fvs: FVS,
  locale?: LocaleID,
];

export const variants: Record<
  CharacterName,
  Record<JoiningPosition, Partial<Record<FVS, Variant>>>
> = {
  "MONGOLIAN SIBE SYLLABLE BOUNDARY MARKER": {
    isol: {
      "0": {
        written: ["medi", 0],
        locales: {
          SIB: {
            conditions: ["default"],
          },
          MCH: {
            conditions: ["default"],
          },
          MCHx: {
            written: ["init", 0, "MCHx"],
            conditions: ["default"],
          },
        },
      },
    },
    init: {
      "0": {
        written: ["medi", 0],
        locales: {
          SIB: {
            conditions: ["default"],
          },
          MCH: {
            conditions: ["default"],
          },
          MCHx: {
            written: ["A2"],
            conditions: ["default"],
          },
        },
      },
    },
    medi: {
      "0": {
        written: ["A"],
        locales: {
          SIB: {
            conditions: ["default"],
          },
          MCH: {
            conditions: ["default"],
            gb: "1807 sibe syllable boundary",
          },
          MCHx: {
            conditions: ["default"],
          },
        },
      },
    },
    fina: {
      "0": {
        written: ["medi", 0],
        locales: {
          SIB: {
            conditions: ["default"],
          },
          MCH: {
            conditions: ["default"],
          },
          MCHx: {
            conditions: ["default"],
          },
        },
      },
    },
  },
  "MONGOLIAN LETTER A": {
    isol: {
      "1": {
        written: ["A"],
        locales: {
          MNG: {
            gb: "00B3 a second isolated form",
            eac: "MAD2",
          },
          MNGx: {},
          TOD: {
            conditions: ["chachlag", "particle"],
            gb: "1821 a second isolated form",
            eac: "TAD2",
          },
          TODx: {},
        },
      },
      "2": {
        written: ["Aa"],
        locales: {
          MNG: {
            conditions: ["chachlag", "particle"],
            gb: "00B4 a third isolated form",
            eac: "MAD3",
          },
          MNGx: {
            conditions: ["chachlag"],
          },
        },
      },
      "3": {
        written: ["A", "A"],
        locales: {
          MNG: {
            conditions: ["default"],
            gb: "00B2 a first isolated form",
            eac: "MAD1",
          },
          MNGx: {
            conditions: ["default"],
          },
          TOD: {
            conditions: ["default"],
            gb: "1820 a first isolated form",
            eac: "TAD1",
          },
          TODx: {
            conditions: ["default"],
          },
          SIB: {
            conditions: ["default"],
            gb: "1820 sibe a isolated form",
            eac: "SAD1",
          },
          MCH: {
            conditions: ["default"],
            gb: "1820 manchu a isolated form",
            eac: "MAD1",
          },
          MCHx: {
            conditions: ["default"],
          },
        },
      },
    },
    init: {
      "1": {
        written: ["A"],
        locales: {
          MNG: {
            conditions: ["particle"],
            gb: "0007 a first initial form",
            eac: "MAS2",
          },
          MNGx: {},
        },
      },
      "2": {
        written: ["A", "A"],
        locales: {
          MNG: {
            conditions: ["default"],
            gb: "0004 a first initial form",
            eac: "MAS1",
          },
          MNGx: {
            conditions: ["default"],
          },
          TOD: {
            conditions: ["default"],
            gb: "0004 a initial form",
            eac: "TAS1",
          },
          TODx: {
            conditions: ["default"],
          },
          SIB: {
            conditions: ["default"],
            gb: "1820 sibe a initial form",
            eac: "SAS1",
          },
          MCH: {
            conditions: ["default"],
            gb: "0004 manchu a initial form",
            eac: "MAS1",
          },
          MCHx: {
            conditions: ["default"],
          },
        },
      },
    },
    medi: {
      "0": {
        written: ["A"],
        locales: {
          MNG: {
            conditions: ["default"],
            gb: "0005 a first medial form",
            eac: "MAZ1",
          },
          MNGx: {
            conditions: ["default"],
          },
          TOD: {
            conditions: ["default"],
            gb: "0005 a first medial form",
            eac: "TAZ1",
          },
          TODx: {
            conditions: ["default"],
          },
          SIB: {
            conditions: ["default"],
            gb: "1820 sibe a medial form",
            eac: "SAZ1",
          },
          MCH: {
            conditions: ["default"],
            gb: "0005 manchu a medial form",
            eac: "MAZ1",
          },
          MCHx: {
            conditions: ["default"],
          },
        },
      },
      "1": {
        written: ["A", "A"],
        locales: {
          MNG: {
            gb: "0006 a second medial form",
            eac: "MAZ2",
          },
          TOD: {
            gb: "0006 a second medial form",
            eac: "TAZ2",
          },
          TODx: {},
        },
      },
    },
    fina: {
      "1": {
        written: ["Aa"],
        locales: {
          MNG: {
            conditions: ["post_bowed"],
            gb: "0009 a second final form",
            eac: "MAM2",
          },
          MNGx: {
            conditions: ["post_bowed"],
          },
          TOD: {
            conditions: ["post_bowed"],
            gb: "0009 a second final form",
            eac: "TAM2",
          },
          TODx: {
            conditions: ["post_bowed"],
          },
          SIB: {
            conditions: ["post_bowed"],
            eac: "SAM2",
          },
          MCH: {
            conditions: ["post_bowed"],
            eac: "MAM2",
          },
          MCHx: {
            conditions: ["post_bowed"],
          },
        },
      },
      "2": {
        written: ["A"],
        locales: {
          MNG: {
            gb: "0008 a first final form",
            eac: "MAM1",
          },
          MNGx: {
            conditions: ["default"],
          },
          TOD: {
            conditions: ["default"],
            gb: "0008 a first final form",
            eac: "TAM1",
          },
          TODx: {
            conditions: ["default"],
          },
          SIB: {
            conditions: ["default"],
            gb: "1820 sibe a final form",
            eac: "SAM1",
          },
          MCH: {
            conditions: ["default"],
            gb: "0008 manchu a final form",
            eac: "MAM1",
          },
          MCHx: {
            conditions: ["default"],
          },
        },
      },
    },
  },
  "MONGOLIAN LETTER E": {
    isol: {
      "1": {
        written: ["Aa"],
        locales: {
          MNG: {
            conditions: ["chachlag", "particle"],
            gb: "00B4 e second isolated form",
            eac: "MED2",
          },
        },
      },
      "2": {
        written: ["A"],
        locales: {
          MNG: {
            conditions: ["default"],
            gb: "00B3 e first isolated form",
            eac: "MED1",
          },
        },
      },
    },
    init: {
      "0": {
        written: ["A"],
        locales: {
          MNG: {
            conditions: ["default"],
            gb: "0007 e first initial form",
            eac: "MES1",
          },
        },
      },
      "1": {
        written: ["A", "A"],
        locales: {
          MNG: {
            gb: "0004 e second initial form",
            eac: "MES2",
          },
        },
      },
    },
    medi: {
      "0": {
        written: ["A"],
        locales: {
          MNG: {
            conditions: ["default"],
            gb: "0005 e medial form",
            eac: "MEZ1",
          },
        },
      },
    },
    fina: {
      "1": {
        written: ["Aa"],
        locales: {
          MNG: {
            conditions: ["post_bowed"],
            gb: "0009 e second final form",
            eac: "MEM2",
          },
        },
      },
      "2": {
        written: ["A"],
        locales: {
          MNG: {
            conditions: ["default"],
            gb: "0008 e first final form",
            eac: "MEM1",
          },
        },
      },
    },
  },
  "MONGOLIAN LETTER I": {
    isol: {
      "1": {
        written: ["I"],
        locales: {
          MNG: {
            conditions: ["particle"],
            gb: "000B i second isolated form",
            eac: "MID2",
          },
        },
      },
      "2": {
        written: ["Ix"],
        locales: {
          MNG: {
            gb: "00B6 i third isolated form",
            eac: "MID3",
          },
        },
      },
      "3": {
        written: ["A", "I"],
        locales: {
          MNG: {
            conditions: ["default"],
            gb: "00B5 i first isolated form",
            eac: "MID1",
          },
        },
      },
    },
    init: {
      "1": {
        written: ["I"],
        locales: {
          MNG: {
            conditions: ["particle"],
            gb: "00B7 i second initial form",
            eac: "MIS2",
          },
        },
      },
      "2": {
        written: ["A", "I"],
        locales: {
          MNG: {
            conditions: ["default"],
            gb: "000A i first initial form",
            eac: "MIS1",
          },
        },
      },
    },
    medi: {
      "1": {
        written: ["A", "I"],
        locales: {
          MNG: {
            gb: "00B8 i second medial form",
            eac: "MIZ2",
          },
        },
      },
      "2": {
        written: ["I", "I"],
        locales: {
          MNG: {
            conditions: ["devsger"],
            gb: "00B9 i third medial form",
            eac: "MIZ3",
          },
        },
      },
      "3": {
        written: ["I"],
        locales: {
          MNG: {
            conditions: ["default"],
            gb: "00B7 i first medial form",
            eac: "MIZ1",
          },
        },
      },
    },
    fina: {
      "0": {
        written: ["I"],
        locales: {
          MNG: {
            conditions: ["default"],
            gb: "000B i final form",
            eac: "MIM0",
          },
        },
      },
    },
  },
  "MONGOLIAN LETTER O": {
    isol: {
      "0": {
        written: ["A", "O"],
        locales: {
          MNG: {
            conditions: ["default"],
            gb: "00BA o isolated form",
            eac: "MWD1",
          },
          MNGx: {
            conditions: ["default"],
          },
          SIB: {
            conditions: ["default"],
            gb: "1823 sibe o isolated form",
            eac: "SOD1",
          },
          MCH: {
            conditions: ["default"],
            gb: "1823 manchu o isolated form",
            eac: "MOD1",
          },
          MCHx: {
            conditions: ["default"],
          },
        },
      },
    },
    init: {
      "0": {
        written: ["A", "O"],
        locales: {
          MNG: {
            conditions: ["default"],
            gb: "00BA o initial form",
            eac: "MWS1",
          },
          MNGx: {
            conditions: ["default"],
          },
          SIB: {
            conditions: ["default"],
            gb: "1823 sibe o initial form",
            eac: "SOS1",
          },
          MCH: {
            conditions: ["default"],
            gb: "1824 manchu o initial form",
            eac: "MOS1",
          },
          MCHx: {
            conditions: ["default"],
          },
        },
      },
    },
    medi: {
      "0": {
        written: ["O"],
        locales: {
          MNG: {
            conditions: ["default"],
            gb: "000C o first medial form",
            eac: "MWZ1",
          },
          MNGx: {
            conditions: ["default"],
          },
          SIB: {
            conditions: ["default"],
            gb: "1823 sibe o medial form",
            eac: "SOZ1",
          },
          MCH: {
            conditions: ["default"],
            gb: "000C manchu o medial form",
            eac: "MOZ1",
          },
          MCHx: {
            conditions: ["default"],
          },
        },
      },
      "1": {
        written: ["A", "O"],
        locales: {
          MNG: {
            gb: "000D o second medial form",
            eac: "MWZ2",
          },
        },
      },
    },
    fina: {
      "1": {
        written: ["O"],
        locales: {
          MNG: {
            conditions: ["marked", "post_bowed"],
            gb: "000F o second final form",
            eac: "MWM2",
          },
          MNGx: {
            conditions: ["post_bowed"],
          },
          SIB: {
            conditions: ["marked", "post_bowed"],
            gb: "1823 sibe o second final form",
            eac: "SOM2",
          },
          MCH: {
            conditions: ["marked", "post_bowed"],
            gb: "000F manchu o second final form",
            eac: "MOM2",
          },
          MCHx: {
            conditions: ["marked", "post_bowed"],
          },
        },
      },
      "2": {
        written: ["U"],
        locales: {
          MNG: {
            conditions: ["default"],
            gb: "000E o first final form",
            eac: "MWM1",
          },
          MNGx: {
            conditions: ["default"],
          },
          SIB: {
            conditions: ["default"],
            gb: "1823 sibe o first final form",
            eac: "SOM1",
          },
          MCH: {
            conditions: ["default"],
            gb: "000E manchu o first final form",
            eac: "MOM1",
          },
          MCHx: {
            conditions: ["default"],
          },
        },
      },
    },
  },
  "MONGOLIAN LETTER U": {
    isol: {
      "1": {
        written: ["U"],
        locales: {
          MNG: {
            conditions: ["particle"],
            gb: "000E u second isolated form",
            eac: "MVD2",
          },
        },
      },
      "2": {
        written: ["Ux"],
        locales: {
          MNG: {
            gb: "00BB u third isolated form",
            eac: "MVD3",
          },
        },
      },
      "3": {
        written: ["A", "O"],
        locales: {
          MNG: {
            conditions: ["default"],
            gb: "00BA u first isolated form",
            eac: "MVD1",
          },
        },
      },
    },
    init: {
      "1": {
        written: ["O"],
        locales: {
          MNG: {
            conditions: ["particle"],
            gb: "000F u second initial form",
            eac: "MVS2",
          },
        },
      },
      "2": {
        written: ["A", "O"],
        locales: {
          MNG: {
            conditions: ["default"],
            gb: "00BA u first initial form",
            eac: "MVS1",
          },
        },
      },
    },
    medi: {
      "0": {
        written: ["O"],
        locales: {
          MNG: {
            conditions: ["default"],
            gb: "000F u first medial form",
            eac: "MVZ1",
          },
        },
      },
      "1": {
        written: ["A", "O"],
        locales: {
          MNG: {
            gb: "000D u second medial form",
            eac: "MVZ2",
          },
        },
      },
    },
    fina: {
      "1": {
        written: ["O"],
        locales: {
          MNG: {
            conditions: ["marked", "post_bowed"],
            gb: "000F u second final form",
            eac: "MVM2",
          },
        },
      },
      "2": {
        written: ["U"],
        locales: {
          MNG: {
            conditions: ["default", "particle"],
            gb: "000E u first final form",
            eac: "MVM1",
          },
        },
      },
    },
  },
  "MONGOLIAN LETTER OE": {
    isol: {
      "0": {
        written: ["A", "Ue"],
        locales: {
          MNG: {
            conditions: ["default"],
            gb: "00BC oe first isolated form",
            eac: "MOD1",
          },
        },
      },
      "1": {
        written: ["A", "U"],
        locales: {
          MNG: {
            gb: "00BD oe second isolated form",
            eac: "MOD2",
          },
        },
      },
    },
    init: {
      "0": {
        written: ["A", "O", "I"],
        locales: {
          MNG: {
            conditions: ["default"],
            gb: "00BE oe initial form",
            eac: "MOS1",
          },
        },
      },
    },
    medi: {
      "1": {
        written: ["O", "I"],
        locales: {
          MNG: {
            conditions: ["marked"],
            gb: "00BF oe second medial form",
            eac: "MOZ2",
          },
        },
      },
      "2": {
        written: ["A", "O", "I"],
        locales: {
          MNG: {
            gb: "0010 oe third medial form",
            eac: "MOZ3",
          },
        },
      },
      "3": {
        written: ["O"],
        locales: {
          MNG: {
            conditions: ["default"],
            gb: "000F oe first medial form",
            eac: "MOZ1",
          },
        },
      },
    },
    fina: {
      "1": {
        written: ["Ue"],
        locales: {
          MNG: {
            conditions: ["marked"],
            gb: "0011 oe second final form",
            eac: "MOM2",
          },
        },
      },
      "2": {
        written: ["O"],
        locales: {
          MNG: {
            conditions: ["post_bowed"],
            gb: "000F oe third final form",
            eac: "MOM3",
          },
        },
      },
      "3": {
        written: ["U"],
        locales: {
          MNG: {
            conditions: ["default"],
            gb: "000E oe first final form",
            eac: "MOM1",
          },
        },
      },
    },
  },
  "MONGOLIAN LETTER UE": {
    isol: {
      "0": {
        written: ["A", "Ue"],
        locales: {
          MNG: {
            conditions: ["default"],
            gb: "00BC ue first isolated form",
            eac: "MUD1",
          },
          MNGx: {
            conditions: ["default"],
          },
        },
      },
      "1": {
        written: ["A", "U"],
        locales: {
          MNG: {
            gb: "00BD ue second isolated form",
            eac: "MUD2",
          },
          MNGx: {},
        },
      },
      "2": {
        written: ["U"],
        locales: {
          MNG: {
            conditions: ["particle"],
            gb: "000E ue third isolated form",
            eac: "MUD3",
          },
        },
      },
      "3": {
        written: ["Ux"],
        locales: {
          MNG: {
            gb: "00BB ue fourth isolated form",
            eac: "MUD4",
          },
        },
      },
    },
    init: {
      "1": {
        written: ["O"],
        locales: {
          MNG: {
            conditions: ["particle"],
            gb: "000F ue second initial form",
            eac: "MUS2",
          },
        },
      },
      "2": {
        written: ["A", "O", "I"],
        locales: {
          MNG: {
            conditions: ["default"],
            gb: "00BE ue first initial form",
            eac: "MUS1",
          },
          MNGx: {
            conditions: ["default"],
          },
        },
      },
    },
    medi: {
      "1": {
        written: ["O", "I"],
        locales: {
          MNG: {
            conditions: ["marked"],
            gb: "00BF ue second medial form",
            eac: "MUZ2",
          },
          MNGx: {
            conditions: ["marked"],
          },
        },
      },
      "2": {
        written: ["A", "O", "I"],
        locales: {
          MNG: {
            gb: "0010 ue third medial form",
            eac: "MUZ3",
          },
        },
      },
      "3": {
        written: ["O"],
        locales: {
          MNG: {
            conditions: ["default", "particle"],
            gb: "000F ue first medial form",
            eac: "MUZ1",
          },
          MNGx: {
            conditions: ["default"],
          },
        },
      },
    },
    fina: {
      "1": {
        written: ["Ue"],
        locales: {
          MNG: {
            conditions: ["marked"],
            gb: "0011 ue second final form",
            eac: "MUM2",
          },
        },
      },
      "2": {
        written: ["O"],
        locales: {
          MNG: {
            conditions: ["post_bowed"],
            gb: "000F ue third final form",
            eac: "MUM3",
          },
          MNGx: {
            conditions: ["post_bowed"],
          },
        },
      },
      "3": {
        written: ["U"],
        locales: {
          MNG: {
            conditions: ["default", "particle"],
            gb: "000E ue first final form",
            eac: "MUM1",
          },
          MNGx: {
            conditions: ["default"],
          },
        },
      },
    },
  },
  "MONGOLIAN LETTER EE": {
    isol: {
      "0": {
        written: ["A", "W"],
        locales: {
          MNG: {
            conditions: ["default"],
            gb: "00C0 ee isolated form",
            eac: "XED1",
          },
          MNGx: {
            conditions: ["default"],
          },
        },
      },
    },
    init: {
      "0": {
        written: ["A", "W"],
        locales: {
          MNG: {
            conditions: ["default"],
            gb: "0012 ee initial form",
            eac: "XES1",
          },
          MNGx: {
            conditions: ["default"],
          },
        },
      },
    },
    medi: {
      "0": {
        written: ["W"],
        locales: {
          MNG: {
            conditions: ["default"],
            gb: "00C1 ee medial form",
            eac: "XEZ1",
          },
          MNGx: {
            conditions: ["default"],
          },
        },
      },
    },
    fina: {
      "0": {
        written: ["W"],
        locales: {
          MNG: {
            conditions: ["default"],
            gb: "0013 ee final form",
            eac: "XEM1",
          },
          MNGx: {
            conditions: ["default"],
          },
        },
      },
    },
  },
  "MONGOLIAN LETTER NA": {
    isol: {
      "0": {
        written: ["init", 0],
        locales: {
          MNG: {
            conditions: ["default"],
            gb: "00C2 na first isolated form",
            eac: "MND1",
          },
          MNGx: {
            conditions: ["default"],
          },
          TOD: {
            conditions: ["default"],
            gb: "1828 na isolated form",
            eac: "TNAD1",
          },
          TODx: {
            conditions: ["default"],
          },
          SIB: {
            conditions: ["default"],
            eac: "SNAD1",
          },
          MCH: {
            conditions: ["default"],
            eac: "MNAD1",
          },
          MCHx: {
            conditions: ["default"],
          },
        },
      },
      "1": {
        written: ["init", 1],
        locales: {
          MNG: {
            gb: "0007 na second isolated form",
            eac: "MND2",
          },
        },
      },
    },
    init: {
      "0": {
        written: ["N"],
        locales: {
          MNG: {
            conditions: ["default"],
            gb: "00C2 na first initial form",
            eac: "MNS1",
          },
          MNGx: {
            conditions: ["default"],
          },
          TOD: {
            conditions: ["default"],
            gb: "1828 na initial form",
            eac: "TNAS1",
          },
          TODx: {
            conditions: ["default"],
          },
          SIB: {
            conditions: ["default"],
            gb: "1828 sibe na initial form",
            eac: "SNAS1",
          },
          MCH: {
            conditions: ["default"],
            gb: "1828 manchu na initial form",
            eac: "MNAS1",
          },
          MCHx: {
            conditions: ["onset"],
          },
        },
      },
      "1": {
        written: ["A"],
        locales: {
          MNG: {
            gb: "0007 na second initial form",
            eac: "MNS2",
          },
          MCHx: {
            conditions: ["default", "devsger"],
          },
        },
      },
    },
    medi: {
      "1": {
        written: ["N"],
        locales: {
          MNG: {
            conditions: ["onset"],
            gb: "0014 na second medial form",
            eac: "MNZ2",
          },
          MNGx: {},
          TOD: {
            conditions: ["onset"],
            gb: "0014 na second medial form",
            eac: "TNAZ2",
          },
          TODx: {
            conditions: ["onset"],
          },
          SIB: {
            conditions: ["onset"],
            gb: "1828 sibe na second medial form",
            eac: "SNAZ2",
          },
          MCH: {
            conditions: ["onset"],
            gb: "0014 manchu na second medial form",
            eac: "MNAZ2",
          },
          MCHx: {
            conditions: ["onset"],
          },
        },
      },
      "2": {
        written: ["A"],
        locales: {
          MNG: {
            conditions: ["default", "devsger"],
            gb: "0005 na first medial form",
            eac: "MNZ1",
          },
          MNGx: {
            conditions: ["default"],
          },
          TOD: {
            conditions: ["default", "devsger"],
            gb: "0005 na first medial form",
            eac: "TNAZ1",
          },
          TODx: {
            conditions: ["default", "devsger"],
          },
          SIB: {
            conditions: ["default", "devsger"],
            gb: "1828 sibe na first medial form",
            eac: "SNAZ1",
          },
          MCH: {
            conditions: ["default", "devsger"],
            gb: "0005 manchu na first medial form",
            eac: "MNAZ1",
          },
          MCHx: {
            conditions: ["default", "devsger"],
          },
        },
      },
    },
    fina: {
      "1": {
        written: ["N"],
        locales: {
          MNG: {
            conditions: ["chachlag_onset"],
            gb: "0015 na second final form",
            eac: "MNM2",
          },
          SIB: {
            gb: "1828 sibe na second final form",
            eac: "SNAM2",
          },
          MCH: {
            gb: "0015 manchu na second final form",
            eac: "MNAM2",
          },
          MCHx: {},
        },
      },
      "2": {
        written: ["A"],
        locales: {
          MNG: {
            conditions: ["default", "devsger"],
            gb: "0008 na first final form",
            eac: "MNM1",
          },
          MNGx: {
            conditions: ["default"],
          },
          TOD: {
            conditions: ["default"],
            gb: "0008 na final form",
            eac: "TNAM1",
          },
          TODx: {
            conditions: ["default"],
          },
          SIB: {
            conditions: ["default"],
            gb: "1828 sibe na first final form",
            eac: "SNAM1",
          },
          MCH: {
            conditions: ["default"],
            gb: "0008 manchu na first final form",
            eac: "MNAM1",
          },
          MCHx: {
            conditions: ["default"],
          },
        },
      },
    },
  },
  "MONGOLIAN LETTER ANG": {
    isol: {
      "0": {
        written: ["medi", 0],
        locales: {
          MNG: {
            conditions: ["default"],
            gb: "00C3 ang isolated form",
            eac: "XND1",
          },
          MNGx: {
            conditions: ["default"],
          },
          MCH: {
            conditions: ["default"],
            eac: "MANGD1",
          },
          MCHx: {
            conditions: ["default"],
          },
        },
      },
    },
    init: {
      "0": {
        written: ["medi", 0],
        locales: {
          MNG: {
            conditions: ["default"],
            gb: "00C3 ang initial form",
            eac: "XNS1",
          },
          MNGx: {
            conditions: ["default"],
          },
          MCH: {
            conditions: ["default"],
            eac: "MANGS1",
          },
          MCHx: {
            conditions: ["default"],
          },
        },
      },
    },
    medi: {
      "0": {
        written: ["A", "G"],
        locales: {
          MNG: {
            conditions: ["default"],
            gb: "00C3 ang medial form",
            eac: "XNZ1",
          },
          MNGx: {
            conditions: ["default"],
          },
          MCH: {
            conditions: ["default"],
            gb: "1829 manchu ang first medial form",
            eac: "MANGZ1",
          },
          MCHx: {
            conditions: ["default"],
          },
        },
      },
    },
    fina: {
      "0": {
        written: ["A", "G"],
        locales: {
          MNG: {
            conditions: ["default"],
            gb: "00C3 ang final form",
            eac: "XNM1",
          },
          MNGx: {
            conditions: ["default"],
          },
          MCH: {
            conditions: ["default"],
            gb: "0017 manchu ang final form",
            eac: "MANGM1",
          },
          MCHx: {
            conditions: ["default"],
          },
        },
      },
    },
  },
  "MONGOLIAN LETTER BA": {
    isol: {
      "0": {
        written: ["init", 0],
        locales: {
          MNG: {
            conditions: ["default"],
            gb: "00C4 ba isolated form",
            eac: "MBD1",
          },
          MNGx: {
            conditions: ["default"],
          },
          SIB: {
            conditions: ["default"],
            eac: "SBAD1",
          },
          MCH: {
            conditions: ["default"],
            eac: "MBAD1",
          },
          MCHx: {
            conditions: ["default"],
          },
        },
      },
    },
    init: {
      "0": {
        written: ["B"],
        locales: {
          MNG: {
            conditions: ["default"],
            gb: "00C4 ba initial form",
            eac: "MBS1",
          },
          MNGx: {
            conditions: ["default"],
          },
          SIB: {
            conditions: ["default"],
            gb: "182A sibe ba initial form",
            eac: "SBAS1",
          },
          MCH: {
            conditions: ["default"],
            gb: "182A manchu ba initial form",
            eac: "MBAS1",
          },
          MCHx: {
            conditions: ["default"],
          },
        },
      },
    },
    medi: {
      "0": {
        written: ["B"],
        locales: {
          MNG: {
            conditions: ["default"],
            gb: "00C4 ba medial form",
            eac: "MBZ1",
          },
          MNGx: {
            conditions: ["default"],
          },
          SIB: {
            conditions: ["default"],
            gb: "182A sibe ba medial form",
            eac: "SBAZ1",
          },
          MCH: {
            conditions: ["default"],
            gb: "182A manchu ba medial form",
            eac: "MBAZ1",
          },
          MCHx: {
            conditions: ["default"],
          },
        },
      },
    },
    fina: {
      "0": {
        written: ["B"],
        locales: {
          MNG: {
            conditions: ["default"],
            gb: "0018 ba first final form",
            eac: "MBM1",
          },
          MNGx: {
            conditions: ["default"],
          },
          SIB: {
            conditions: ["default"],
            gb: "182A sibe ba final form",
            eac: "SBAM1",
          },
          MCH: {
            conditions: ["default"],
            gb: "0018 manchu ba final form",
            eac: "MBAM1",
          },
          MCHx: {
            conditions: ["default"],
          },
        },
      },
      "1": {
        written: ["B2"],
        locales: {
          MNG: {
            gb: "00C5 ba second final form",
            eac: "MBM2",
          },
          MNGx: {},
        },
      },
    },
  },
  "MONGOLIAN LETTER PA": {
    isol: {
      "0": {
        written: ["init", 0],
        locales: {
          MNG: {
            conditions: ["default"],
            gb: "00C6 pa isolated form",
            eac: "MPD1",
          },
        },
      },
    },
    init: {
      "0": {
        written: ["P"],
        locales: {
          MNG: {
            conditions: ["default"],
            gb: "00C6 pa initial form",
            eac: "MPS1",
          },
        },
      },
    },
    medi: {
      "0": {
        written: ["P"],
        locales: {
          MNG: {
            conditions: ["default"],
            gb: "00C6 pa medial form",
            eac: "MPZ1",
          },
        },
      },
    },
    fina: {
      "0": {
        written: ["P"],
        locales: {
          MNG: {
            conditions: ["default"],
            gb: "0019 pa final form",
            eac: "MPM1",
          },
        },
      },
    },
  },
  "MONGOLIAN LETTER QA": {
    isol: {
      "0": {
        written: ["init", 3],
        locales: {
          MNG: {
            conditions: ["default"],
            gb: "00C7 qa first isolated form",
            eac: "MHD1",
          },
        },
      },
      "1": {
        written: ["init", 1],
        locales: {
          MNG: {
            gb: "00C8 qa second isolated form",
            eac: "MHD2",
          },
        },
      },
      "2": {
        written: ["init", 2],
        locales: {
          MNG: {
            gb: "001E qa third isolated form",
            eac: "MHD3",
          },
        },
      },
      "4": {
        written: ["init", 4],
        locales: {
          MNG: {
            gb: "001B qa fourth isolated form",
            eac: "MHD4",
          },
        },
      },
    },
    init: {
      "1": {
        written: ["Hx"],
        locales: {
          MNG: {
            gb: "00C8 qa second initial form",
            eac: "MHS2",
          },
        },
      },
      "2": {
        written: ["G"],
        locales: {
          MNG: {
            conditions: ["feminine"],
            gb: "001E qa third initial form",
            eac: "MHS3",
          },
        },
      },
      "3": {
        written: ["H"],
        locales: {
          MNG: {
            conditions: ["default", "masculine_onset"],
            gb: "00C7 qa first initial form",
            eac: "MHS1",
          },
        },
      },
      "4": {
        written: ["Gx"],
        locales: {
          MNG: {
            gb: "001B qa fourth initial form",
            eac: "MHS4",
          },
        },
      },
    },
    medi: {
      "1": {
        written: ["Hx"],
        locales: {
          MNG: {
            gb: "001C qa second medial form",
            eac: "MHZ2",
          },
        },
      },
      "2": {
        written: ["G"],
        locales: {
          MNG: {
            gb: "001E qa third medial form",
            eac: "MHZ3",
          },
        },
      },
      "3": {
        written: ["H"],
        locales: {
          MNG: {
            conditions: ["default", "chachlag_onset", "masculine_devsger"],
            gb: "0006 qa first medial form",
            eac: "MHZ1",
          },
        },
      },
      "4": {
        written: ["Gx"],
        locales: {
          MNG: {
            gb: "001B qa fourth medial form",
            eac: "MHZ4",
          },
        },
      },
    },
    fina: {
      "0": {
        written: ["H"],
        locales: {
          MNG: {
            gb: "001A qa first final form",
            eac: "MHM1",
          },
        },
      },
      "1": {
        written: ["Hx"],
        locales: {
          MNG: {
            gb: "001D qa second final form",
            eac: "MHM2",
          },
        },
      },
    },
  },
  "MONGOLIAN LETTER GA": {
    isol: {
      "0": {
        written: ["init", 3],
        locales: {
          MNG: {
            conditions: ["default"],
            gb: "00C8 ga first isolated form",
            eac: "MGD1",
          },
        },
      },
      "1": {
        written: ["init", 1],
        locales: {
          MNG: {
            gb: "00C7 ga second isolated form",
            eac: "MGD2",
          },
        },
      },
      "2": {
        written: ["init", 2],
        locales: {
          MNG: {
            gb: "001E ga third isolated form",
            eac: "MGD3",
          },
        },
      },
      "4": {
        written: ["init", 4],
        locales: {
          MNG: {
            gb: "001B ga fourth isolated form",
            eac: "MGD4",
          },
        },
      },
    },
    init: {
      "1": {
        written: ["H"],
        locales: {
          MNG: {
            gb: "00C7 ga second initial form",
            eac: "MGS2",
          },
        },
      },
      "2": {
        written: ["G"],
        locales: {
          MNG: {
            conditions: ["feminine"],
            gb: "001E ga third initial form",
            eac: "MGS3",
          },
        },
      },
      "3": {
        written: ["Hx"],
        locales: {
          MNG: {
            conditions: ["default", "masculine_onset"],
            gb: "00C8 ga first initial form",
            eac: "MGS1",
          },
        },
      },
      "4": {
        written: ["Gx"],
        locales: {
          MNG: {
            gb: "001B ga fourth initial form",
            eac: "MGS4",
          },
        },
      },
    },
    medi: {
      "1": {
        written: ["Hx"],
        locales: {
          MNG: {
            conditions: ["masculine_onset"],
            gb: "001C ga second medial form",
            eac: "MGZ2",
          },
        },
      },
      "2": {
        written: ["G"],
        locales: {
          MNG: {
            conditions: ["default", "feminine"],
            gb: "001E ga third medial form",
            eac: "MGZ3",
          },
        },
      },
      "3": {
        written: ["H"],
        locales: {
          MNG: {
            conditions: ["masculine_devsger", "dotless"],
            gb: "0006 ga first medial form",
            eac: "MGZ1",
          },
        },
      },
      "4": {
        written: ["Gx"],
        locales: {
          MNG: {
            gb: "001B ga fourth medial form",
            eac: "MGZ4",
          },
        },
      },
    },
    fina: {
      "1": {
        written: ["H"],
        locales: {
          MNG: {
            conditions: ["chachlag_devsger", "masculine_devsger", "dotless"],
            gb: "001A ga first final form",
            eac: "MGM1",
          },
        },
      },
      "2": {
        written: ["G"],
        locales: {
          MNG: {
            conditions: ["default", "feminine"],
            gb: "001F ga second final form",
            eac: "MGM2",
          },
        },
      },
      "3": {
        written: ["Hx"],
        locales: {
          MNG: {
            conditions: ["chachlag_onset"],
            gb: "001D ga third final form",
            eac: "MGM3",
          },
        },
      },
    },
  },
  "MONGOLIAN LETTER MA": {
    isol: {
      "0": {
        written: ["init", 0],
        locales: {
          MNG: {
            conditions: ["default"],
            gb: "00C9 ma isolated form",
            eac: "MMD1",
          },
          SIB: {
            conditions: ["default"],
            eac: "SMAD1",
          },
          MCH: {
            conditions: ["default"],
            eac: "MMAD1",
          },
          MCHx: {
            conditions: ["default"],
          },
        },
      },
    },
    init: {
      "0": {
        written: ["M"],
        locales: {
          MNG: {
            conditions: ["default"],
            gb: "00C9 ma initial form",
            eac: "MMS1",
          },
          SIB: {
            conditions: ["default"],
            gb: "182E sibe ma initial form",
            eac: "SMAS1",
          },
          MCH: {
            conditions: ["default"],
            gb: "182E manchu ma initial form",
            eac: "MMAS1",
          },
          MCHx: {
            conditions: ["default"],
          },
        },
      },
    },
    medi: {
      "0": {
        written: ["M"],
        locales: {
          MNG: {
            conditions: ["default"],
            gb: "0020 ma medial form",
            eac: "MMZ1",
          },
          SIB: {
            conditions: ["default"],
            gb: "182E sibe ma medial form",
            eac: "SMAZ1",
          },
          MCH: {
            conditions: ["default"],
            gb: "0020 manchu ma medial form",
            eac: "MMAZ1",
          },
          MCHx: {
            conditions: ["default"],
          },
        },
      },
    },
    fina: {
      "0": {
        written: ["M"],
        locales: {
          MNG: {
            conditions: ["default"],
            gb: "0021 ma final form",
            eac: "MMM1",
          },
          SIB: {
            conditions: ["default"],
            gb: "182E sibe ma final form",
            eac: "SMAM1",
          },
          MCH: {
            conditions: ["default"],
            gb: "0021 manchu ma final form",
            eac: "MMAM1",
          },
          MCHx: {
            conditions: ["default"],
          },
        },
      },
    },
  },
  "MONGOLIAN LETTER LA": {
    isol: {
      "0": {
        written: ["init", 0],
        locales: {
          MNG: {
            conditions: ["default"],
            gb: "00CA la isolated form",
            eac: "MLD1",
          },
          MNGx: {
            conditions: ["default"],
          },
          TOD: {
            conditions: ["default"],
            gb: "182F la isolated form",
            eac: "TLAD1",
          },
          TODx: {
            conditions: ["default"],
          },
          SIB: {
            conditions: ["default"],
            eac: "SLAD1",
          },
          MCH: {
            conditions: ["default"],
            eac: "MLAD1",
          },
          MCHx: {
            conditions: ["default"],
          },
        },
      },
    },
    init: {
      "0": {
        written: ["L"],
        locales: {
          MNG: {
            conditions: ["default"],
            gb: "00CA la initial form",
            eac: "MLS1",
          },
          MNGx: {
            conditions: ["default"],
          },
          TOD: {
            conditions: ["default"],
            gb: "182F la initial form",
            eac: "TLAS1",
          },
          TODx: {
            conditions: ["default"],
          },
          SIB: {
            conditions: ["default"],
            gb: "182F sibe la initial form",
            eac: "SLAS1",
          },
          MCH: {
            conditions: ["default"],
            gb: "182F manchu la initial form",
            eac: "MLAS1",
          },
          MCHx: {
            conditions: ["default"],
          },
        },
      },
    },
    medi: {
      "0": {
        written: ["L"],
        locales: {
          MNG: {
            conditions: ["default"],
            gb: "0022 la medial form",
            eac: "MLZ1",
          },
          MNGx: {
            conditions: ["default"],
          },
          TOD: {
            conditions: ["default"],
            gb: "0022 la medial form",
            eac: "TLAZ1",
          },
          TODx: {
            conditions: ["default"],
          },
          SIB: {
            conditions: ["default"],
            gb: "182F sibe la medial form",
            eac: "SLAZ1",
          },
          MCH: {
            conditions: ["default"],
            gb: "0022 manchu la medial form",
            eac: "MLAZ1",
          },
          MCHx: {
            conditions: ["default"],
          },
        },
      },
    },
    fina: {
      "0": {
        written: ["L"],
        locales: {
          MNG: {
            conditions: ["default"],
            gb: "0023 la final form",
            eac: "MLM1",
          },
          MNGx: {
            conditions: ["default"],
          },
          TOD: {
            conditions: ["default"],
            gb: "0023 la final form",
            eac: "TLAM1",
          },
          TODx: {
            conditions: ["default"],
          },
          SIB: {
            conditions: ["default"],
            gb: "182F sibe la final form",
            eac: "SLAM1",
          },
          MCH: {
            conditions: ["default"],
            gb: "0023 manchu la final form",
            eac: "MLAM1",
          },
          MCHx: {
            conditions: ["default"],
          },
        },
      },
    },
  },
  "MONGOLIAN LETTER SA": {
    isol: {
      "0": {
        written: ["init", 0],
        locales: {
          MNG: {
            conditions: ["default"],
            gb: "00CB sa isolated form",
            eac: "MSD1",
          },
          MNGx: {
            conditions: ["default"],
          },
          TOD: {
            conditions: ["default"],
            gb: "1830 sa isolated form",
            eac: "TSAD1",
          },
          TODx: {
            conditions: ["default"],
          },
          SIB: {
            conditions: ["default"],
            eac: "SSAD1",
          },
          MCH: {
            conditions: ["default"],
            eac: "MSAD1",
          },
          MCHx: {
            conditions: ["default"],
          },
        },
      },
    },
    init: {
      "0": {
        written: ["S"],
        locales: {
          MNG: {
            conditions: ["default"],
            gb: "00CB sa initial form",
            eac: "MSS1",
          },
          MNGx: {
            conditions: ["default"],
          },
          TOD: {
            conditions: ["default"],
            gb: "1830 sa initial form",
            eac: "TSAS1",
          },
          TODx: {
            conditions: ["default"],
          },
          SIB: {
            conditions: ["default"],
            gb: "1830 sibe sa initial form",
            eac: "SSAS1",
          },
          MCH: {
            conditions: ["default"],
            gb: "1830 manchu sa initial form",
            eac: "MSAS1",
          },
          MCHx: {
            conditions: ["default"],
          },
        },
      },
    },
    medi: {
      "0": {
        written: ["S"],
        locales: {
          MNG: {
            conditions: ["default"],
            gb: "0024 sa first medial form",
            eac: "MSZ1",
          },
          MNGx: {
            conditions: ["default"],
          },
          TOD: {
            conditions: ["default"],
            gb: "0024 sa medial form",
            eac: "TSAZ1",
          },
          TODx: {
            conditions: ["default"],
          },
          SIB: {
            conditions: ["default"],
            gb: "1830 sibe sa medial form",
            eac: "SSAZ1",
          },
          MCH: {
            conditions: ["default"],
            gb: "0024 manchu sa medial form",
            eac: "MSAZ1",
          },
          MCHx: {
            conditions: ["default"],
          },
        },
      },
    },
    fina: {
      "0": {
        written: ["S"],
        locales: {
          MNG: {
            conditions: ["default"],
            gb: "0025 sa first final form",
            eac: "MSM1",
          },
          MNGx: {
            conditions: ["default"],
          },
          TOD: {
            conditions: ["default"],
            gb: "0025 sa final form",
            eac: "TSAM1",
          },
          TODx: {
            conditions: ["default"],
          },
          SIB: {
            conditions: ["default"],
            gb: "1830 sibe sa final form",
            eac: "SSAM1",
          },
          MCH: {
            conditions: ["default"],
            gb: "0025 manchu sa first final form",
            eac: "MSAM1",
          },
          MCHx: {
            conditions: ["default"],
          },
        },
      },
      "1": {
        written: ["Sz"],
        locales: {
          MNG: {
            gb: "0026 sa second final form",
            eac: "MSM2",
          },
        },
      },
    },
  },
  "MONGOLIAN LETTER SHA": {
    isol: {
      "0": {
        written: ["init", 2],
        locales: {
          MNG: {
            conditions: ["default"],
            gb: "00CC sha first isolated form",
            eac: "MXD1",
          },
          MNGx: {
            conditions: ["default"],
          },
          TOD: {
            conditions: ["default"],
            gb: "1831 sha isolated form",
            eac: "TSHAD1",
          },
          TODx: {
            conditions: ["default"],
          },
        },
      },
      "1": {
        written: ["init", 1],
        locales: {
          MNG: {
            gb: "00CB sha second isolated form",
            eac: "MXD2",
          },
        },
      },
    },
    init: {
      "1": {
        written: ["S"],
        locales: {
          MNG: {
            conditions: ["dotless"],
            gb: "00CB sha second initial form",
            eac: "MXS2",
          },
        },
      },
      "2": {
        written: ["Sh"],
        locales: {
          MNG: {
            conditions: ["default"],
            gb: "00CC sha first initial form",
            eac: "MXS1",
          },
          MNGx: {
            conditions: ["default"],
          },
          TOD: {
            conditions: ["default"],
            gb: "1831 sha initial form",
            eac: "TSHAS1",
          },
          TODx: {
            conditions: ["default"],
          },
        },
      },
    },
    medi: {
      "1": {
        written: ["S"],
        locales: {
          MNG: {
            conditions: ["dotless"],
            gb: "0024 sha second medial form",
            eac: "MXZ2",
          },
        },
      },
      "2": {
        written: ["Sh"],
        locales: {
          MNG: {
            conditions: ["default"],
            gb: "0028 sha first medial form",
            eac: "MXZ1",
          },
          MNGx: {
            conditions: ["default"],
          },
          TOD: {
            conditions: ["default"],
            gb: "0028 sha medial form",
            eac: "TSHAZ1",
          },
          TODx: {
            conditions: ["default"],
          },
        },
      },
    },
    fina: {
      "0": {
        written: ["Sh"],
        locales: {
          MNG: {
            conditions: ["default"],
            gb: "0029 sha final form",
            eac: "MXM1",
          },
          MNGx: {
            conditions: ["default"],
          },
          TOD: {
            conditions: ["default"],
            gb: "0029 sha final form",
            eac: "TSHAM1",
          },
          TODx: {
            conditions: ["default"],
          },
        },
      },
    },
  },
  "MONGOLIAN LETTER TA": {
    isol: {
      "0": {
        written: ["init", 0],
        locales: {
          MNG: {
            conditions: ["default"],
            gb: "00CD ta isolated form",
            eac: "MTD1",
          },
        },
      },
    },
    init: {
      "0": {
        written: ["T"],
        locales: {
          MNG: {
            conditions: ["default"],
            gb: "00CD ta initial form",
            eac: "MTS1",
          },
        },
      },
    },
    medi: {
      "1": {
        written: ["T"],
        locales: {
          MNG: {
            conditions: ["devsger"],
            gb: "00CD ta second medial form",
            eac: "MTZ2",
          },
        },
      },
      "2": {
        written: ["D"],
        locales: {
          MNG: {
            conditions: ["default"],
            gb: "00CE ta first medial form",
            eac: "MTZ1",
          },
        },
      },
    },
    fina: {
      "0": {
        written: ["T"],
        locales: {
          MNG: {
            conditions: ["default"],
            gb: "002B ta final form",
            eac: "MTM1",
          },
        },
      },
    },
  },
  "MONGOLIAN LETTER DA": {
    isol: {
      "0": {
        written: ["init", 1],
        locales: {
          MNG: {
            conditions: ["default"],
            gb: "00CE da first isolated form",
            eac: "MDD1",
          },
        },
      },
      "1": {
        written: ["init", 2],
        locales: {
          MNG: {
            gb: "00CD da second isolated form",
            eac: "MDD2",
          },
        },
      },
    },
    init: {
      "1": {
        written: ["D"],
        locales: {
          MNG: {
            conditions: ["marked", "particle"],
            gb: "00CE da second initial form",
            eac: "MDS2",
          },
        },
      },
      "2": {
        written: ["T"],
        locales: {
          MNG: {
            conditions: ["default", "onset"],
            gb: "00CD da first initial form",
            eac: "MDS1",
          },
        },
      },
    },
    medi: {
      "1": {
        written: ["D"],
        locales: {
          MNG: {
            conditions: ["onset"],
            gb: "00CE da second medial form",
            eac: "MDZ2",
          },
        },
      },
      "2": {
        written: ["Dd"],
        locales: {
          MNG: {
            conditions: ["default", "devsger"],
            gb: "002C da first medial form",
            eac: "MDZ1",
          },
        },
      },
    },
    fina: {
      "0": {
        written: ["Dd"],
        locales: {
          MNG: {
            conditions: ["devsger"],
            gb: "002D da first final form",
            eac: "MDM1",
          },
        },
      },
      "1": {
        written: ["D"],
        locales: {
          MNG: {
            gb: "002E da second final form",
            eac: "MDM2",
          },
        },
      },
    },
  },
  "MONGOLIAN LETTER CHA": {
    isol: {
      "0": {
        written: ["init", 0],
        locales: {
          MNG: {
            conditions: ["default"],
            gb: "002F cha isolated form",
            eac: "MQD1",
          },
          MNGx: {
            conditions: ["default"],
          },
          TOD: {
            conditions: ["default"],
            gb: "1834 dza isolated form",
            eac: "TZAD1",
          },
          TODx: {
            conditions: ["default"],
          },
          SIB: {
            conditions: ["default"],
            eac: "SCHAD1",
          },
          MCH: {
            conditions: ["default"],
            eac: "MCHAD1",
          },
          MCHx: {
            conditions: ["default"],
          },
        },
      },
    },
    init: {
      "0": {
        written: ["Ch"],
        locales: {
          MNG: {
            conditions: ["default"],
            gb: "002F cha initial form",
            eac: "MQS1",
          },
          MNGx: {
            conditions: ["default"],
          },
          TOD: {
            conditions: ["default"],
            gb: "1834 dza initial form",
            eac: "TZAS1",
          },
          TODx: {
            conditions: ["default"],
          },
          SIB: {
            conditions: ["default"],
            gb: "1834 sibe cha initial form",
            eac: "SCHAS1",
          },
          MCH: {
            conditions: ["default"],
            gb: "1834 manchu cha initial form",
            eac: "MCHAS1",
          },
          MCHx: {
            conditions: ["default"],
          },
        },
      },
    },
    medi: {
      "0": {
        written: ["Ch"],
        locales: {
          MNG: {
            conditions: ["default"],
            gb: "002F cha medial form",
            eac: "MQZ1",
          },
          MNGx: {
            conditions: ["default"],
          },
          TOD: {
            conditions: ["default"],
            gb: "002F dza medial form",
            eac: "TZAZ1",
          },
          TODx: {
            conditions: ["default"],
          },
          SIB: {
            conditions: ["default"],
            gb: "1834 sibe cha medial form",
            eac: "SCHAZ1",
          },
          MCH: {
            conditions: ["default"],
            gb: "002F manchu cha medial form",
            eac: "MCHAZ1",
          },
          MCHx: {
            conditions: ["default"],
          },
        },
      },
    },
    fina: {
      "0": {
        written: ["Ch"],
        locales: {
          MNG: {
            conditions: ["default"],
            gb: "0030 cha final form",
            eac: "MQM1",
          },
          MNGx: {
            conditions: ["default"],
          },
          TOD: {
            conditions: ["default"],
            gb: "0030 dza final form",
            eac: "TZAM1",
          },
          TODx: {
            written: ["medi", 0],
            conditions: ["default"],
          },
          SIB: {
            written: ["medi", 0],
            conditions: ["default"],
            eac: "SCHAM1",
          },
          MCH: {
            written: ["medi", 0],
            conditions: ["default"],
            eac: "MCHAM1",
          },
          MCHx: {
            conditions: ["default"],
          },
        },
      },
    },
  },
  "MONGOLIAN LETTER JA": {
    isol: {
      "0": {
        written: ["init", 0],
        locales: {
          MNG: {
            conditions: ["default"],
            gb: "00B7 ja first isolated form",
            eac: "MJD1",
          },
          MCH: {
            conditions: ["default"],
            eac: "MJAD1",
          },
          MCHx: {
            conditions: ["default"],
          },
        },
      },
      "1": {
        written: ["I"],
        locales: {
          MNG: {
            conditions: ["chachlag_onset"],
            gb: "000B ja second isolated form",
            eac: "MJD2",
          },
        },
      },
    },
    init: {
      "0": {
        written: ["I"],
        locales: {
          MNG: {
            conditions: ["default"],
            gb: "00B7 ja first initial form",
            eac: "MJS1",
          },
          MCH: {
            conditions: ["default"],
            gb: "1835 manchu ja initial form",
            eac: "MJAS1",
          },
          MCHx: {
            conditions: ["default"],
          },
        },
      },
    },
    medi: {
      "0": {
        written: ["J"],
        locales: {
          MNG: {
            conditions: ["default"],
            gb: "0031 ja first medial form",
            eac: "MJZ1",
          },
          MCH: {
            conditions: ["default"],
            gb: "0031 manchu ja medial form",
            eac: "MJAZ1",
          },
          MCHx: {
            conditions: ["default"],
          },
        },
      },
    },
    fina: {
      "0": {
        written: ["J"],
        locales: {
          MNG: {
            conditions: ["default"],
            gb: "0032 ja first final form",
            eac: "MJM1",
          },
          MCH: {
            written: ["medi", 0],
            conditions: ["default"],
            eac: "MJAM1",
          },
          MCHx: {
            conditions: ["default"],
          },
        },
      },
      "1": {
        written: ["I"],
        locales: {
          MNG: {
            conditions: ["chachlag_onset"],
            gb: "000B ja second final form",
            eac: "MJM2",
          },
        },
      },
    },
  },
  "MONGOLIAN LETTER YA": {
    isol: {
      "0": {
        written: ["init", 2],
        locales: {
          MNG: {
            conditions: ["default"],
            gb: "00CF ya first isolated form",
            eac: "MYD1",
          },
          SIB: {
            conditions: ["default"],
            eac: "SYAD1",
          },
          MCH: {
            conditions: ["default"],
            eac: "MYAD1",
          },
          MCHx: {
            conditions: ["default"],
          },
        },
      },
      "1": {
        written: ["init", 1],
        locales: {
          MNG: {
            gb: "00B7 ya second isolated form",
            eac: "MYD2",
          },
        },
      },
    },
    init: {
      "1": {
        written: ["I"],
        locales: {
          MNG: {
            conditions: ["particle"],
            gb: "00B7 ya second initial form",
            eac: "MYS2",
          },
        },
      },
      "2": {
        written: ["Y"],
        locales: {
          MNG: {
            conditions: ["default"],
            gb: "00CF ya first initial form",
            eac: "MYS1",
          },
          SIB: {
            conditions: ["default"],
            eac: "SYAS1",
          },
          MCH: {
            conditions: ["default"],
            gb: "1836 manchu ya initial form",
            eac: "MYAS1",
          },
          MCHx: {
            conditions: ["default"],
          },
        },
      },
    },
    medi: {
      "1": {
        written: ["I"],
        locales: {
          MNG: {
            conditions: ["particle"],
            gb: "00B7 ya second medial form",
            eac: "MYZ2",
          },
        },
      },
      "2": {
        written: ["I", "I"],
        locales: {
          MNG: {
            gb: "00B9 ya third medial form",
            eac: "MYZ3",
          },
        },
      },
      "3": {
        written: ["Y"],
        locales: {
          MNG: {
            conditions: ["default"],
            gb: "00CF ya first medial form",
            eac: "MYZ1",
          },
          SIB: {
            conditions: ["default"],
            eac: "SYAZ1",
          },
          MCH: {
            conditions: ["default"],
            gb: "1836 manchu ya medial form",
            eac: "MYAZ1",
          },
          MCHx: {
            conditions: ["default"],
          },
        },
      },
    },
    fina: {
      "0": {
        written: ["I"],
        locales: {
          MNG: {
            conditions: ["default"],
            gb: "000B ya final form",
            eac: "MYM1",
          },
          SIB: {
            written: ["medi", 3],
            conditions: ["default"],
            eac: "SYAM1",
          },
          MCH: {
            written: ["medi", 3],
            conditions: ["default"],
            eac: "MYAM1",
          },
          MCHx: {
            written: ["medi", 3],
            conditions: ["default"],
          },
        },
      },
    },
  },
  "MONGOLIAN LETTER RA": {
    isol: {
      "0": {
        written: ["init", 0],
        locales: {
          MNG: {
            conditions: ["default"],
            gb: "00D0 ra isolated form",
            eac: "MRD1",
          },
          MNGx: {
            conditions: ["default"],
          },
          TOD: {
            conditions: ["default"],
            gb: "1837 ra isolated form",
            eac: "TRAD1",
          },
          TODx: {
            conditions: ["default"],
          },
          SIB: {
            conditions: ["default"],
            eac: "SRAD1",
          },
        },
      },
    },
    init: {
      "0": {
        written: ["R"],
        locales: {
          MNG: {
            conditions: ["default"],
            gb: "00D0 ra initial form",
            eac: "MRS1",
          },
          MNGx: {
            conditions: ["default"],
          },
          TOD: {
            conditions: ["default"],
            gb: "1837 ra initial form",
            eac: "TRAS1",
          },
          TODx: {
            conditions: ["default"],
          },
          SIB: {
            conditions: ["default"],
            eac: "SRAS1",
          },
        },
      },
    },
    medi: {
      "0": {
        written: ["R"],
        locales: {
          MNG: {
            conditions: ["default"],
            gb: "00D0 ra medial form",
            eac: "MRZ1",
          },
          MNGx: {
            conditions: ["default"],
          },
          TOD: {
            conditions: ["default"],
            gb: "1837 ra medial form",
            eac: "TRAZ1",
          },
          TODx: {
            conditions: ["default"],
          },
          SIB: {
            conditions: ["default"],
            eac: "SRAZ1",
          },
        },
      },
    },
    fina: {
      "0": {
        written: ["R"],
        locales: {
          MNG: {
            conditions: ["default"],
            gb: "0033 ra final form",
            eac: "MRM1",
          },
          MNGx: {
            conditions: ["default"],
          },
          TOD: {
            conditions: ["default"],
            gb: "0033 ra final form",
            eac: "TRAM1",
          },
          TODx: {
            conditions: ["default"],
          },
          SIB: {
            conditions: ["default"],
            eac: "SRAM1",
          },
        },
      },
    },
  },
  "MONGOLIAN LETTER WA": {
    isol: {
      "0": {
        written: ["init", 0],
        locales: {
          MNG: {
            conditions: ["default"],
            gb: "00C1 wa isolated form",
            eac: "XWD1",
          },
          MNGx: {
            conditions: ["default"],
          },
          TOD: {
            conditions: ["default"],
            gb: "1838 fa isolated form",
            eac: "TFAD1",
          },
          SIB: {
            conditions: ["default"],
            eac: "SFAD1",
          },
          MCH: {
            conditions: ["default"],
            eac: "MWAD1",
          },
          MCHx: {
            conditions: ["default"],
          },
        },
      },
    },
    init: {
      "0": {
        written: ["W"],
        locales: {
          MNG: {
            conditions: ["default"],
            gb: "00C1 wa initial form",
            eac: "XWS1",
          },
          MNGx: {
            conditions: ["default"],
          },
          TOD: {
            conditions: ["default"],
            gb: "1838 fa initial form",
            eac: "TFAS1",
          },
          SIB: {
            conditions: ["default"],
            eac: "SFAS1",
          },
          MCH: {
            conditions: ["default"],
            gb: "1838 manchu wa initial form",
            eac: "MWAS1",
          },
          MCHx: {
            conditions: ["default"],
          },
        },
      },
    },
    medi: {
      "0": {
        written: ["W"],
        locales: {
          MNG: {
            conditions: ["default"],
            gb: "00C1 wa first medial form",
            eac: "XWZ1",
          },
          MNGx: {
            conditions: ["default"],
          },
          TOD: {
            conditions: ["default"],
            gb: "1838 fa medial form",
            eac: "TFAZ1",
          },
          SIB: {
            conditions: ["default"],
            eac: "SFAZ1",
          },
          MCH: {
            conditions: ["default"],
            gb: "1838 manchu wa medial form",
            eac: "MWAZ1",
          },
          MCHx: {
            conditions: ["default"],
          },
        },
      },
      "1": {
        written: ["O"],
        locales: {
          MNG: {
            gb: "000F wa second medial form",
            eac: "XWZ2",
          },
        },
      },
    },
    fina: {
      "0": {
        written: ["W"],
        locales: {
          MNG: {
            conditions: ["default"],
            gb: "0013 wa first final form",
            eac: "XWM1",
          },
          MNGx: {
            conditions: ["default"],
          },
          TOD: {
            conditions: ["default"],
            gb: "0013 fa final form",
            eac: "TFAM1",
          },
          SIB: {
            conditions: ["default"],
            eac: "SFAM1",
          },
          MCH: {
            conditions: ["default"],
            eac: "MWAM1",
          },
          MCHx: {
            conditions: ["default"],
          },
        },
      },
      "1": {
        written: ["U"],
        locales: {
          MNG: {
            conditions: ["chachlag_onset"],
            gb: "000E wa second final form",
            eac: "XWM2",
          },
        },
      },
    },
  },
  "MONGOLIAN LETTER FA": {
    isol: {
      "0": {
        written: ["init", 0],
        locales: {
          MNG: {
            conditions: ["default"],
            gb: "00D1 fa isolated form",
            eac: "XFD1",
          },
        },
      },
    },
    init: {
      "0": {
        written: ["F"],
        locales: {
          MNG: {
            conditions: ["default"],
            gb: "00D1 fa initial form",
            eac: "XFS1",
          },
        },
      },
    },
    medi: {
      "0": {
        written: ["F"],
        locales: {
          MNG: {
            conditions: ["default"],
            gb: "00D1 fa medial form",
            eac: "XFZ1",
          },
        },
      },
    },
    fina: {
      "0": {
        written: ["F"],
        locales: {
          MNG: {
            conditions: ["default"],
            gb: "0034 fa final form",
            eac: "XFM1",
          },
        },
      },
    },
  },
  "MONGOLIAN LETTER KA": {
    isol: {
      "0": {
        written: ["init", 0],
        locales: {
          MNG: {
            conditions: ["default"],
            gb: "00D2 ka isolated form",
            eac: "MKD1",
          },
          MNGx: {
            conditions: ["default"],
          },
          TODx: {
            conditions: ["default"],
          },
          SIB: {
            conditions: ["default"],
            eac: "SKAAD1",
          },
          MCH: {
            conditions: ["default"],
            eac: "MKAAD1",
          },
          MCHx: {
            conditions: ["default"],
          },
        },
      },
    },
    init: {
      "0": {
        written: ["K2"],
        locales: {
          MNG: {
            conditions: ["default"],
            gb: "00D2 ka initial form",
            eac: "MKS1",
          },
          MNGx: {
            conditions: ["default"],
          },
          TODx: {
            conditions: ["default"],
          },
          SIB: {
            conditions: ["default"],
            eac: "SKAAS1",
          },
          MCH: {
            conditions: ["default"],
            gb: "183A manchu ka initial form",
            eac: "MKAAS1",
          },
          MCHx: {
            conditions: ["default"],
          },
        },
      },
    },
    medi: {
      "0": {
        written: ["K2"],
        locales: {
          MNG: {
            conditions: ["default"],
            gb: "00D2 ka medial form",
            eac: "MKZ1",
          },
          MNGx: {
            conditions: ["default"],
          },
          TODx: {
            conditions: ["default"],
          },
          SIB: {
            conditions: ["default"],
            eac: "SKAAZ1",
          },
          MCH: {
            conditions: ["default"],
            gb: "183A manchu ka medial form",
            eac: "MKAAZ1",
          },
          MCHx: {
            conditions: ["default"],
          },
        },
      },
    },
    fina: {
      "0": {
        written: ["K2"],
        locales: {
          MNG: {
            conditions: ["default"],
            gb: "0035 ka final form",
            eac: "MKM1",
          },
          MNGx: {
            conditions: ["default"],
          },
          TODx: {
            written: ["medi", 0],
            conditions: ["default"],
          },
          SIB: {
            written: ["medi", 0],
            conditions: ["default"],
            eac: "SKAAM1",
          },
          MCH: {
            written: ["medi", 0],
            conditions: ["default"],
            eac: "MKAAM1",
          },
          MCHx: {
            written: ["medi", 0],
            conditions: ["default"],
          },
        },
      },
    },
  },
  "MONGOLIAN LETTER KHA": {
    isol: {
      "0": {
        written: ["init", 0],
        locales: {
          MNG: {
            conditions: ["default"],
            gb: "00D3 kha isolated form",
            eac: "XKD1",
          },
          MNGx: {
            conditions: ["default"],
          },
          TODx: {
            conditions: ["default"],
          },
        },
      },
    },
    init: {
      "0": {
        written: ["K"],
        locales: {
          MNG: {
            conditions: ["default"],
            gb: "00D3 kha initial form",
            eac: "XKS1",
          },
          MNGx: {
            conditions: ["default"],
          },
          TODx: {
            conditions: ["default"],
          },
        },
      },
    },
    medi: {
      "0": {
        written: ["K"],
        locales: {
          MNG: {
            conditions: ["default"],
            gb: "00D3 kha medial form",
            eac: "XKZ1",
          },
          MNGx: {
            conditions: ["default"],
          },
          TODx: {
            conditions: ["default"],
          },
        },
      },
    },
    fina: {
      "0": {
        written: ["K"],
        locales: {
          MNG: {
            conditions: ["default"],
            gb: "0036 kha final form",
            eac: "XKM1",
          },
          MNGx: {
            conditions: ["default"],
          },
          TODx: {
            written: ["medi", 0],
            conditions: ["default"],
          },
        },
      },
    },
  },
  "MONGOLIAN LETTER TSA": {
    isol: {
      "0": {
        written: ["init", 0],
        locales: {
          MNG: {
            conditions: ["default"],
            gb: "0037 tsa isolated form",
            eac: "XCD1",
          },
          MNGx: {
            conditions: ["default"],
          },
          TODx: {
            conditions: ["default"],
          },
        },
      },
    },
    init: {
      "0": {
        written: ["C"],
        locales: {
          MNG: {
            conditions: ["default"],
            gb: "0037 tsa initial form",
            eac: "XCS1",
          },
          MNGx: {
            conditions: ["default"],
          },
          TODx: {
            conditions: ["default"],
          },
        },
      },
    },
    medi: {
      "0": {
        written: ["C"],
        locales: {
          MNG: {
            conditions: ["default"],
            gb: "0037 tsa medial form",
            eac: "XCZ1",
          },
          MNGx: {
            conditions: ["default"],
          },
          TODx: {
            conditions: ["default"],
          },
        },
      },
    },
    fina: {
      "0": {
        written: ["C"],
        locales: {
          MNG: {
            conditions: ["default"],
            gb: "0038 tsa final form",
            eac: "XCM1",
          },
          MNGx: {
            conditions: ["default"],
          },
          TODx: {
            written: ["medi", 0],
            conditions: ["default"],
          },
        },
      },
    },
  },
  "MONGOLIAN LETTER ZA": {
    isol: {
      "0": {
        written: ["init", 0],
        locales: {
          MNG: {
            conditions: ["default"],
            gb: "0039 za isolated form",
            eac: "MZD1",
          },
          MNGx: {
            conditions: ["default"],
          },
        },
      },
    },
    init: {
      "0": {
        written: ["Z"],
        locales: {
          MNG: {
            conditions: ["default"],
            gb: "0039 za initial form",
            eac: "MZS1",
          },
          MNGx: {
            conditions: ["default"],
          },
        },
      },
    },
    medi: {
      "0": {
        written: ["Z"],
        locales: {
          MNG: {
            conditions: ["default"],
            gb: "0039 za medial form",
            eac: "MZZ1",
          },
          MNGx: {
            conditions: ["default"],
          },
        },
      },
    },
    fina: {
      "0": {
        written: ["Z"],
        locales: {
          MNG: {
            conditions: ["default"],
            gb: "003A za final form",
            eac: "MZM1",
          },
          MNGx: {
            conditions: ["default"],
          },
        },
      },
    },
  },
  "MONGOLIAN LETTER HAA": {
    isol: {
      "0": {
        written: ["init", 0],
        locales: {
          MNG: {
            conditions: ["default"],
            gb: "00D4 haa isolated form",
            eac: "XHD1",
          },
          MNGx: {
            conditions: ["default"],
          },
          TODx: {
            conditions: ["default"],
          },
        },
      },
    },
    init: {
      "0": {
        written: ["A", "Hr"],
        locales: {
          MNG: {
            conditions: ["default"],
            gb: "00D4 haa initial form",
            eac: "XHS1",
          },
          MNGx: {
            conditions: ["default"],
          },
          TODx: {
            conditions: ["default"],
          },
        },
      },
    },
    medi: {
      "0": {
        written: ["Hr"],
        locales: {
          MNG: {
            conditions: ["default"],
            gb: "00D5 haa medial form",
            eac: "XHZ1",
          },
          MNGx: {
            conditions: ["default"],
          },
          TODx: {
            conditions: ["default"],
          },
        },
      },
    },
    fina: {
      "0": {
        written: ["Hr"],
        locales: {
          MNG: {
            conditions: ["default"],
            gb: "003B haa final form",
            eac: "XHM1",
          },
          MNGx: {
            conditions: ["default"],
          },
          TODx: {
            conditions: ["default"],
          },
        },
      },
    },
  },
  "MONGOLIAN LETTER ZRA": {
    isol: {
      "0": {
        written: ["init", 0],
        locales: {
          MNG: {
            conditions: ["default"],
            gb: "00D6 zra isolated form",
            eac: "XRD1",
          },
        },
      },
    },
    init: {
      "0": {
        written: ["Rh"],
        locales: {
          MNG: {
            conditions: ["default"],
            gb: "00D6 zra initial form",
            eac: "XRS1",
          },
        },
      },
    },
    medi: {
      "0": {
        written: ["Rh"],
        locales: {
          MNG: {
            conditions: ["default"],
            gb: "00D6 zra medial form",
            eac: "XRZ1",
          },
        },
      },
    },
    fina: {
      "0": {
        written: ["Rh"],
        locales: {
          MNG: {
            conditions: ["default"],
            gb: "003C zra final form",
            eac: "XRM1",
          },
        },
      },
    },
  },
  "MONGOLIAN LETTER LHA": {
    isol: {
      "0": {
        written: ["init", 0],
        locales: {
          MNG: {
            conditions: ["default"],
            gb: "00D7 lha isolated form",
            eac: "XLD1",
          },
          MNGx: {
            conditions: ["default"],
          },
          TOD: {
            conditions: ["default"],
            gb: "1840 lha isolated form",
            eac: "TLHAD1",
          },
          TODx: {
            conditions: ["default"],
          },
        },
      },
    },
    init: {
      "0": {
        written: ["L", "Hr"],
        locales: {
          MNG: {
            conditions: ["default"],
            gb: "00D7 lha initial form",
            eac: "XLS1",
          },
          MNGx: {
            conditions: ["default"],
          },
          TOD: {
            conditions: ["default"],
            gb: "1840 lha initial form",
            eac: "TLHAS1",
          },
          TODx: {
            conditions: ["default"],
          },
        },
      },
    },
    medi: {
      "0": {
        written: ["L", "Hr"],
        locales: {
          MNG: {
            conditions: ["default"],
            gb: "003D lha medial form",
            eac: "XLZ1",
          },
          MNGx: {
            conditions: ["default"],
          },
          TOD: {
            conditions: ["default"],
            gb: "003D lha medial form",
            eac: "TLHAZ1",
          },
          TODx: {
            conditions: ["default"],
          },
        },
      },
    },
    fina: {
      "0": {
        written: ["medi", 0],
        locales: {
          MNG: {
            conditions: ["default"],
            gb: "003D lha final form",
            eac: "XLM1",
          },
          MNGx: {
            conditions: ["default"],
          },
          TOD: {
            conditions: ["default"],
            gb: "003D lha final form",
            eac: "TLHAM1",
          },
          TODx: {
            conditions: ["default"],
          },
        },
      },
    },
  },
  "MONGOLIAN LETTER ZHI": {
    isol: {
      "0": {
        written: ["init", 0],
        locales: {
          MNG: {
            conditions: ["default"],
            gb: "00D5 zhi isolated form",
            eac: "XZD1",
          },
        },
      },
    },
    init: {
      "0": {
        written: ["Zr"],
        locales: {
          MNG: {
            conditions: ["default"],
            gb: "00D5 zhi initial form",
            eac: "XZS1",
          },
        },
      },
    },
    medi: {
      "0": {
        written: ["init", 0],
        locales: {
          MNG: {
            conditions: ["default"],
            gb: "00D5 zhi medial form",
            eac: "XZZ1",
          },
        },
      },
    },
    fina: {
      "0": {
        written: ["init", 0],
        locales: {
          MNG: {
            conditions: ["default"],
            gb: "00D5 zhi final form",
            eac: "XZM1",
          },
        },
      },
    },
  },
  "MONGOLIAN LETTER CHI": {
    isol: {
      "0": {
        written: ["init", 0],
        locales: {
          MNG: {
            conditions: ["default"],
            gb: "00D8 chi isolated form",
            eac: "XQD1",
          },
        },
      },
    },
    init: {
      "0": {
        written: ["Cr"],
        locales: {
          MNG: {
            conditions: ["default"],
            gb: "00D8 chi initial form",
            eac: "XQS1",
          },
        },
      },
    },
    medi: {
      "0": {
        written: ["init", 0],
        locales: {
          MNG: {
            conditions: ["default"],
            gb: "00D8 chi medial form",
            eac: "XQZ1",
          },
        },
      },
    },
    fina: {
      "0": {
        written: ["init", 0],
        locales: {
          MNG: {
            conditions: ["default"],
            gb: "00D8 chi final form",
            eac: "XQM1",
          },
        },
      },
    },
  },
  "MONGOLIAN LETTER TODO LONG VOWEL SIGN": {
    isol: {
      "0": {
        written: ["Lv"],
        locales: {
          TOD: {
            conditions: ["default"],
            gb: "1843 todo long vowel sign isolated form",
            eac: "TLVSD1",
          },
          TODx: {
            conditions: ["default"],
          },
        },
      },
    },
    init: {
      "0": {
        written: ["Lv"],
        locales: {
          TOD: {
            conditions: ["default"],
            gb: "1843 todo long vowel sign initial form",
            eac: "TLVSS1",
          },
          TODx: {
            conditions: ["default"],
          },
        },
      },
    },
    medi: {
      "0": {
        written: ["Lv"],
        locales: {
          TOD: {
            conditions: ["default"],
            gb: "1843 todo long vowel sign medial form",
            eac: "TLVSZ1",
          },
          TODx: {
            conditions: ["default"],
          },
        },
      },
    },
    fina: {
      "0": {
        written: ["Lv"],
        locales: {
          TOD: {
            conditions: ["default"],
            gb: "1843 todo long vowel sign final form",
            eac: "TLVSM1",
          },
          TODx: {
            conditions: ["default"],
          },
        },
      },
    },
  },
  "MONGOLIAN LETTER TODO E": {
    isol: {
      "0": {
        written: ["A", "E"],
        locales: {
          TOD: {
            conditions: ["default"],
            gb: "1844 todo e isolated form",
            eac: "TED1",
          },
          TODx: {
            conditions: ["default"],
          },
        },
      },
    },
    init: {
      "0": {
        written: ["A", "E"],
        locales: {
          TOD: {
            conditions: ["default"],
            gb: "1844 todo e initial form",
            eac: "TES1",
          },
          TODx: {
            conditions: ["default"],
          },
        },
      },
    },
    medi: {
      "0": {
        written: ["E"],
        locales: {
          TOD: {
            conditions: ["default"],
            gb: "003F todo e first medial form",
            eac: "TEZ1",
          },
          TODx: {
            conditions: ["default"],
          },
        },
      },
      "1": {
        written: ["A", "E"],
        locales: {
          TOD: {
            gb: "0040 todo e second medial form",
            eac: "TEZ2",
          },
          TODx: {},
        },
      },
    },
    fina: {
      "0": {
        written: ["E"],
        locales: {
          TOD: {
            conditions: ["default"],
            gb: "003F todo e first final form",
            eac: "TEM1",
          },
          TODx: {
            conditions: ["default"],
          },
        },
      },
    },
  },
  "MONGOLIAN LETTER TODO I": {
    isol: {
      "0": {
        written: ["A", "I3"],
        locales: {
          TOD: {
            conditions: ["default"],
            gb: "1845 todo i first medial form",
            eac: "TID1",
          },
          TODx: {
            conditions: ["default"],
          },
        },
      },
    },
    init: {
      "0": {
        written: ["A", "Ip"],
        locales: {
          TOD: {
            conditions: ["default"],
            gb: "0041 todo i first initial form",
            eac: "TIS1",
          },
          TODx: {
            conditions: ["default"],
          },
        },
      },
      "1": {
        written: ["A", "I"],
        locales: {
          TOD: {
            gb: "000A todo i second initial form",
          },
          TODx: {},
        },
      },
    },
    medi: {
      "1": {
        written: ["A", "Ip"],
        locales: {
          TOD: {
            conditions: ["devsger"],
            gb: "0043 todo i first medial form",
            eac: "TIZ2",
          },
          TODx: {},
        },
      },
      "2": {
        written: ["Ip"],
        locales: {
          TOD: {
            conditions: ["default"],
            gb: "0042 todo i second medial form",
            eac: "TIZ1",
          },
          TODx: {
            conditions: ["default"],
          },
        },
      },
      "3": {
        written: ["I"],
        locales: {
          TOD: {
            gb: "1855 todo i third medial form",
          },
          TODx: {},
        },
      },
    },
    fina: {
      "1": {
        written: ["Ip"],
        locales: {
          TOD: {
            conditions: ["post_bowed"],
          },
          TODx: {
            conditions: ["post_bowed"],
          },
        },
      },
      "2": {
        written: ["I3"],
        locales: {
          TOD: {
            conditions: ["default"],
            gb: "0044 todo i first final form",
            eac: "TIM1",
          },
          TODx: {
            conditions: ["default"],
          },
        },
      },
    },
  },
  "MONGOLIAN LETTER TODO O": {
    isol: {
      "0": {
        written: ["A", "Ob"],
        locales: {
          TOD: {
            conditions: ["default"],
            gb: "1846 todo o isolated form",
            eac: "TOD1",
          },
          TODx: {
            conditions: ["default"],
          },
        },
      },
    },
    init: {
      "0": {
        written: ["A", "Ob"],
        locales: {
          TOD: {
            conditions: ["default"],
            gb: "0045 todo o initial form",
            eac: "TOS1",
          },
          TODx: {
            conditions: ["default"],
          },
        },
      },
    },
    medi: {
      "0": {
        written: ["Ob"],
        locales: {
          TOD: {
            conditions: ["default"],
            gb: "0046 todo o first medial form",
            eac: "TOZ1",
          },
          TODx: {
            conditions: ["default"],
          },
        },
      },
      "1": {
        written: ["A", "Ob"],
        locales: {
          TOD: {
            gb: "0047 todo o second medial form",
            eac: "TOZ2",
          },
          TODx: {},
        },
      },
    },
    fina: {
      "0": {
        written: ["Ob"],
        locales: {
          TOD: {
            conditions: ["default"],
            gb: "0048 todo o final form",
            eac: "TOM1",
          },
          TODx: {
            conditions: ["default"],
          },
        },
      },
    },
  },
  "MONGOLIAN LETTER TODO U": {
    isol: {
      "0": {
        written: ["A", "Up"],
        locales: {
          TOD: {
            conditions: ["default"],
            gb: "1847 todo u first isolated form",
            eac: "TUD1",
          },
        },
      },
      "1": {
        written: ["A", "Op"],
        locales: {
          TOD: {
            gb: "0049 todo u second isolated form",
            eac: "TUD2",
          },
        },
      },
    },
    init: {
      "0": {
        written: ["A", "Op"],
        locales: {
          TOD: {
            conditions: ["default"],
            gb: "004A todo u initial form",
            eac: "TUS1",
          },
        },
      },
    },
    medi: {
      "1": {
        written: ["A", "Op"],
        locales: {
          TOD: {
            gb: "004C todo u third medial form",
            eac: "TUZ2",
          },
        },
      },
      "2": {
        written: ["O"],
        locales: {
          TOD: {
            conditions: ["devsger"],
            gb: "000C todo u second medial form",
            eac: "TUZ3",
          },
        },
      },
      "3": {
        written: ["Op"],
        locales: {
          TOD: {
            conditions: ["default"],
            gb: "004B todo u first medial form",
            eac: "TUZ1",
          },
        },
      },
    },
    fina: {
      "1": {
        written: ["U"],
        locales: {
          TOD: {
            conditions: ["devsger"],
            gb: "000E todo u second final form",
            eac: "TUM2",
          },
        },
      },
      "2": {
        written: ["Op"],
        locales: {
          TOD: {
            conditions: ["post_bowed"],
            eac: "TUM3",
          },
        },
      },
      "3": {
        written: ["Up"],
        locales: {
          TOD: {
            conditions: ["default"],
            gb: "004D todo u first final form",
            eac: "TUM1",
          },
        },
      },
    },
  },
  "MONGOLIAN LETTER TODO OE": {
    isol: {
      "0": {
        written: ["A", "Ot"],
        locales: {
          TOD: {
            conditions: ["default"],
            gb: "1848 todo oe isolated form",
            eac: "TOED1",
          },
        },
      },
    },
    init: {
      "0": {
        written: ["A", "Ot"],
        locales: {
          TOD: {
            conditions: ["default"],
            gb: "004E todo oe initial form",
            eac: "TOES1",
          },
        },
      },
    },
    medi: {
      "0": {
        written: ["Ot"],
        locales: {
          TOD: {
            conditions: ["default"],
            gb: "004F todo oe first medial form",
            eac: "TOEZ1",
          },
        },
      },
      "1": {
        written: ["O"],
        locales: {
          TOD: {
            gb: "0046 todo oe second medial form",
          },
        },
      },
      "2": {
        written: ["A", "Ot"],
        locales: {
          TOD: {
            gb: "0050 todo oe third medial form",
            eac: "TOEZ2",
          },
        },
      },
    },
    fina: {
      "0": {
        written: ["Ot"],
        locales: {
          TOD: {
            conditions: ["default"],
            gb: "0051 todo oe first final form",
            eac: "TOEM1",
          },
        },
      },
      "1": {
        written: ["O"],
        locales: {
          TOD: {
            gb: "0048 todo oe second final form",
          },
        },
      },
    },
  },
  "MONGOLIAN LETTER TODO UE": {
    isol: {
      "0": {
        written: ["A", "U"],
        locales: {
          TOD: {
            conditions: ["default"],
            gb: "1849 todo ue first isolated form",
            eac: "TUED1",
          },
          TODx: {
            conditions: ["default"],
          },
        },
      },
      "1": {
        written: ["A", "O"],
        locales: {
          TOD: {
            gb: "1823 todo ue second isolated form",
            eac: "TUED2",
          },
          TODx: {},
        },
      },
    },
    init: {
      "0": {
        written: ["A", "O"],
        locales: {
          TOD: {
            conditions: ["default"],
            gb: "1824 todo ue initial form",
            eac: "TUES1",
          },
          TODx: {
            conditions: ["default"],
          },
        },
      },
    },
    medi: {
      "0": {
        written: ["O"],
        locales: {
          TOD: {
            conditions: ["default"],
            gb: "000C todo ue first medial form",
            eac: "TUEZ1",
          },
          TODx: {
            conditions: ["default"],
          },
        },
      },
      "1": {
        written: ["A", "O"],
        locales: {
          TOD: {
            gb: "000D todo ue second medial form",
            eac: "TUEZ2",
          },
          TODx: {},
        },
      },
    },
    fina: {
      "1": {
        written: ["O"],
        locales: {
          TOD: {
            conditions: ["post_bowed"],
            eac: "TUEM2",
          },
          TODx: {
            conditions: ["post_bowed"],
          },
        },
      },
      "2": {
        written: ["U"],
        locales: {
          TOD: {
            conditions: ["default"],
            gb: "000E todo ue final form",
            eac: "TUEM1",
          },
          TODx: {
            conditions: ["default"],
          },
        },
      },
    },
  },
  "MONGOLIAN LETTER TODO ANG": {
    isol: {
      "0": {
        written: ["medi", 0],
        locales: {
          TOD: {
            conditions: ["default"],
            gb: "1829 ang isolated form",
            eac: "TANGD1",
          },
          TODx: {
            conditions: ["default"],
          },
        },
      },
    },
    init: {
      "0": {
        written: ["medi", 0],
        locales: {
          TOD: {
            conditions: ["default"],
            gb: "1829 ang initial form",
            eac: "TANGS1",
          },
          TODx: {
            conditions: ["default"],
          },
        },
      },
    },
    medi: {
      "0": {
        written: ["A", "G"],
        locales: {
          TOD: {
            conditions: ["default"],
            gb: "1829 ang medial form",
            eac: "TANGZ1",
          },
          TODx: {
            conditions: ["default"],
          },
        },
      },
    },
    fina: {
      "0": {
        written: ["A", "G2"],
        locales: {
          TOD: {
            conditions: ["default"],
            gb: "1829 todo ang final form",
            eac: "TANGM1",
          },
          TODx: {
            conditions: ["default"],
          },
        },
      },
    },
  },
  "MONGOLIAN LETTER TODO BA": {
    isol: {
      "0": {
        written: ["init", 0],
        locales: {
          TOD: {
            conditions: ["default"],
            gb: "182A ba isolated form",
            eac: "TBAD1",
          },
          TODx: {
            conditions: ["default"],
          },
        },
      },
    },
    init: {
      "0": {
        written: ["B"],
        locales: {
          TOD: {
            conditions: ["default"],
            gb: "182A ba initial form",
            eac: "TBAS1",
          },
          TODx: {
            conditions: ["default"],
          },
        },
      },
    },
    medi: {
      "0": {
        written: ["B"],
        locales: {
          TOD: {
            conditions: ["default"],
            gb: "182A ba medial form",
            eac: "TBAZ1",
          },
          TODx: {
            conditions: ["default"],
          },
        },
      },
    },
    fina: {
      "0": {
        written: ["B2"],
        locales: {
          TOD: {
            conditions: ["default"],
            gb: "182A todo ba final form",
            eac: "TBAM1",
          },
          TODx: {
            conditions: ["default"],
          },
        },
      },
    },
  },
  "MONGOLIAN LETTER TODO PA": {
    isol: {
      "0": {
        written: ["init", 0],
        locales: {
          TOD: {
            conditions: ["default"],
            gb: "184C todo pa isolated form",
            eac: "TPAD1",
          },
          TODx: {
            written: ["init", 0, "TODx"],
            conditions: ["default"],
          },
        },
      },
    },
    init: {
      "0": {
        written: ["Pp"],
        locales: {
          TOD: {
            conditions: ["default"],
            gb: "184C todo pa initial form",
            eac: "TPAS1",
          },
          TODx: {
            written: ["Ph"],
            conditions: ["default"],
          },
        },
      },
    },
    medi: {
      "0": {
        written: ["Pp"],
        locales: {
          TOD: {
            conditions: ["default"],
            gb: "184C todo pa medial form",
            eac: "TPAZ1",
          },
          TODx: {
            written: ["Ph"],
            conditions: ["default"],
          },
        },
      },
    },
    fina: {
      "0": {
        written: ["Pp"],
        locales: {
          TOD: {
            conditions: ["default"],
            gb: "0052 todo pa final form",
            eac: "TPAM1",
          },
          TODx: {
            written: ["medi", 0, "TODx"],
            conditions: ["default"],
          },
        },
      },
    },
  },
  "MONGOLIAN LETTER TODO QA": {
    isol: {
      "0": {
        written: ["init", 2],
        locales: {
          TOD: {
            conditions: ["default"],
            gb: "184D todo qa isolated form",
            eac: "TQAD1",
          },
        },
      },
      "1": {
        written: ["init", 1],
        locales: {
          TOD: {
            eac: "TQAD2",
          },
        },
      },
    },
    init: {
      "1": {
        written: ["K"],
        locales: {
          TOD: {
            conditions: ["feminine"],
            gb: "183B todo qa feminine initial form",
            eac: "TQAS2",
          },
        },
      },
      "2": {
        written: ["Hx2"],
        locales: {
          TOD: {
            conditions: ["default", "masculine_onset"],
            gb: "184D todo qa initial form",
            eac: "TQAS1",
          },
        },
      },
    },
    medi: {
      "1": {
        written: ["K"],
        locales: {
          TOD: {
            conditions: ["feminine"],
            gb: "183B todo qa feminine medial form",
            eac: "TQAZ2",
          },
        },
      },
      "2": {
        written: ["Hx"],
        locales: {
          TOD: {
            conditions: ["default", "masculine_onset"],
            gb: "001C todo qa medial form with dots",
            eac: "TQAZ1",
          },
        },
      },
    },
    fina: {
      "0": {
        written: ["K"],
        locales: {
          TOD: {
            conditions: ["default"],
            gb: "1836 todo qa final form",
            eac: "TQAM1",
          },
        },
      },
    },
  },
  "MONGOLIAN LETTER TODO GA": {
    isol: {
      "0": {
        written: ["init", 2],
        locales: {
          TOD: {
            conditions: ["default"],
            gb: "184E todo ga masculine isolated form",
            eac: "TGAD1",
          },
          TODx: {
            conditions: ["default"],
          },
        },
      },
      "1": {
        written: ["init", 1],
        locales: {
          TOD: {
            gb: "1889 todo ga feminine isolated form",
            eac: "TGAD2",
          },
          TODx: {},
        },
      },
    },
    init: {
      "1": {
        written: ["G"],
        locales: {
          TOD: {
            conditions: ["feminine"],
            eac: "TGAS2",
          },
          TODx: {
            conditions: ["feminine"],
          },
        },
      },
      "2": {
        written: ["Hb"],
        locales: {
          TOD: {
            conditions: ["default", "masculine_onset"],
            gb: "184E todo ga initial form",
            eac: "TGAS1",
          },
          TODx: {
            conditions: ["default", "masculine_onset"],
          },
        },
      },
    },
    medi: {
      "1": {
        written: ["Hp"],
        locales: {
          TOD: {
            conditions: ["devsger"],
            gb: "0054 todo ga second medial form",
            eac: "TGAZ2",
          },
          TODx: {
            conditions: ["devsger"],
          },
        },
      },
      "2": {
        written: ["G"],
        locales: {
          TOD: {
            conditions: ["feminine"],
            eac: "TGAZ3",
          },
          TODx: {
            conditions: ["feminine"],
          },
        },
      },
      "3": {
        written: ["Hb"],
        locales: {
          TOD: {
            conditions: ["default", "masculine_onset"],
            gb: "0053 todo ga first medial form",
            eac: "TGAZ1",
          },
          TODx: {
            conditions: ["default", "masculine_onset"],
          },
        },
      },
    },
    fina: {
      "0": {
        written: ["Hp"],
        locales: {
          TOD: {
            conditions: ["default"],
            gb: "0055 todo ga first final form",
            eac: "TGAM1",
          },
          TODx: {
            conditions: ["default"],
          },
        },
      },
    },
  },
  "MONGOLIAN LETTER TODO MA": {
    isol: {
      "0": {
        written: ["init", 0],
        locales: {
          MNGx: {
            conditions: ["default"],
          },
          TOD: {
            conditions: ["default"],
            gb: "182E todo ma isolated form",
            eac: "TMAD1",
          },
          TODx: {
            conditions: ["default"],
          },
        },
      },
    },
    init: {
      "0": {
        written: ["M"],
        locales: {
          MNGx: {
            conditions: ["default"],
          },
          TOD: {
            conditions: ["default"],
            gb: "182E todo ma initial form",
            eac: "TMAS1",
          },
          TODx: {
            conditions: ["default"],
          },
        },
      },
    },
    medi: {
      "0": {
        written: ["M"],
        locales: {
          MNGx: {
            conditions: ["default"],
          },
          TOD: {
            conditions: ["default"],
            gb: "0020 todo ma medial form",
            eac: "TMAZ1",
          },
          TODx: {
            conditions: ["default"],
          },
        },
      },
    },
    fina: {
      "0": {
        written: ["M2"],
        locales: {
          MNGx: {
            conditions: ["default"],
          },
          TOD: {
            conditions: ["default"],
            gb: "184F todo ma final form",
            eac: "TMAM1",
          },
          TODx: {
            conditions: ["default"],
          },
        },
      },
    },
  },
  "MONGOLIAN LETTER TODO TA": {
    isol: {
      "0": {
        written: ["init", 0],
        locales: {
          MNGx: {
            conditions: ["default"],
          },
          TOD: {
            conditions: ["default"],
            gb: "1850 todo ta isolated form",
            eac: "TTAD1",
          },
          TODx: {
            conditions: ["default"],
          },
        },
      },
    },
    init: {
      "0": {
        written: ["Tp"],
        locales: {
          MNGx: {
            conditions: ["default"],
          },
          TOD: {
            conditions: ["default"],
            gb: "1850 todo ta initial form",
            eac: "TTAS1",
          },
          TODx: {
            conditions: ["default"],
          },
        },
      },
    },
    medi: {
      "0": {
        written: ["Tp"],
        locales: {
          MNGx: {
            conditions: ["default"],
          },
          TOD: {
            conditions: ["default"],
            gb: "1850 todo ta medial form",
            eac: "TTAZ1",
          },
          TODx: {
            conditions: ["default"],
          },
        },
      },
    },
    fina: {
      "0": {
        written: ["Tp"],
        locales: {
          MNGx: {
            conditions: ["default"],
          },
          TOD: {
            conditions: ["default"],
            gb: "0056 todo ta final form",
            eac: "TTAM1",
          },
          TODx: {
            written: ["medi", 0],
            conditions: ["default"],
          },
        },
      },
    },
  },
  "MONGOLIAN LETTER TODO DA": {
    isol: {
      "0": {
        written: ["init", 0],
        locales: {
          TOD: {
            conditions: ["default"],
            gb: "1851 todo da isolated form",
            eac: "TDAD1",
          },
          TODx: {
            conditions: ["default"],
          },
        },
      },
    },
    init: {
      "0": {
        written: ["Dp"],
        locales: {
          TOD: {
            conditions: ["default"],
            gb: "1851 todo da initial form",
            eac: "TDAS1",
          },
          TODx: {
            conditions: ["default"],
          },
        },
      },
    },
    medi: {
      "0": {
        written: ["Dp"],
        locales: {
          TOD: {
            conditions: ["default"],
            gb: "1851 todo da medial form",
            eac: "TDAZ1",
          },
          TODx: {
            conditions: ["default"],
          },
        },
      },
    },
    fina: {
      "0": {
        written: ["Dp"],
        locales: {
          TOD: {
            conditions: ["default"],
            gb: "0311 todo da final form",
            eac: "TDAM1",
          },
          TODx: {
            written: ["medi", 0],
            conditions: ["default"],
          },
        },
      },
    },
  },
  "MONGOLIAN LETTER TODO CHA": {
    isol: {
      "0": {
        written: ["init", 0],
        locales: {
          TOD: {
            conditions: ["default"],
            gb: "1852 todo cha isolated form",
            eac: "TCHAD1",
          },
        },
      },
    },
    init: {
      "0": {
        written: ["Jb"],
        locales: {
          TOD: {
            conditions: ["default"],
            gb: "1852 todo cha initial form",
            eac: "TCHAS1",
          },
        },
      },
    },
    medi: {
      "0": {
        written: ["Jb"],
        locales: {
          TOD: {
            conditions: ["default"],
            gb: "0057 todo cha medial form",
            eac: "TCHAZ1",
          },
        },
      },
    },
    fina: {
      "0": {
        written: ["Jb"],
        locales: {
          TOD: {
            conditions: ["default"],
            gb: "0058 todo cha final form",
            eac: "TCHAM1",
          },
        },
      },
    },
  },
  "MONGOLIAN LETTER TODO JA": {
    isol: {
      "0": {
        written: ["init", 0],
        locales: {
          TOD: {
            conditions: ["default"],
            gb: "1853 todo ja isolated form",
            eac: "TJAD1",
          },
          TODx: {
            conditions: ["default"],
          },
        },
      },
    },
    init: {
      "0": {
        written: ["Cp"],
        locales: {
          TOD: {
            conditions: ["default"],
            gb: "1853 todo ja initial form",
            eac: "TJAS1",
          },
          TODx: {
            conditions: ["default"],
          },
        },
      },
    },
    medi: {
      "0": {
        written: ["Cp"],
        locales: {
          TOD: {
            conditions: ["default"],
            gb: "0059 todo ja medial form",
            eac: "TJAZ1",
          },
          TODx: {
            conditions: ["default"],
          },
        },
      },
    },
    fina: {
      "0": {
        written: ["Cp"],
        locales: {
          TOD: {
            conditions: ["default"],
            gb: "005A todo ja final form",
            eac: "TJAM1",
          },
          TODx: {
            written: ["medi", 0],
            conditions: ["default"],
          },
        },
      },
    },
  },
  "MONGOLIAN LETTER TODO TSA": {
    isol: {
      "0": {
        written: ["init", 0],
        locales: {
          MNGx: {
            conditions: ["default"],
          },
          TOD: {
            conditions: ["default"],
            gb: "1854 todo tsa isolated form",
            eac: "TTSAD1",
          },
          TODx: {
            conditions: ["default"],
          },
        },
      },
    },
    init: {
      "0": {
        written: ["J"],
        locales: {
          MNGx: {
            conditions: ["default"],
          },
          TOD: {
            conditions: ["default"],
            gb: "1854 todo tsa initial form",
            eac: "TTSAS1",
          },
          TODx: {
            conditions: ["default"],
          },
        },
      },
    },
    medi: {
      "0": {
        written: ["J"],
        locales: {
          MNGx: {
            conditions: ["default"],
          },
          TOD: {
            conditions: ["default"],
            gb: "0031 todo tsa medial form",
            eac: "TTSAZ1",
          },
          TODx: {
            conditions: ["default"],
          },
        },
      },
    },
    fina: {
      "0": {
        written: ["J"],
        locales: {
          MNGx: {
            conditions: ["default"],
          },
          TOD: {
            conditions: ["default"],
            gb: "0032 todo tsa final form",
            eac: "TTSAM1",
          },
          TODx: {
            written: ["medi", 0],
            conditions: ["default"],
          },
        },
      },
    },
  },
  "MONGOLIAN LETTER TODO YA": {
    isol: {
      "0": {
        written: ["init", 0],
        locales: {
          MNGx: {
            conditions: ["default"],
          },
          TOD: {
            conditions: ["default"],
            gb: "1855 todo ya isolated form",
            eac: "TYAD1",
          },
          TODx: {
            conditions: ["default"],
          },
        },
      },
      "1": {
        written: ["init", 1],
        locales: {
          TOD: {
            eac: "TYAD2",
          },
        },
      },
    },
    init: {
      "0": {
        written: ["I"],
        locales: {
          MNGx: {
            conditions: ["default"],
          },
          TOD: {
            conditions: ["default"],
            gb: "1855 todo ya first initial form",
            eac: "TYAS1",
          },
          TODx: {
            conditions: ["default"],
          },
        },
      },
      "1": {
        written: ["Y"],
        locales: {
          TOD: {
            gb: "1836 todo ya second initial form",
            eac: "TYAS2",
          },
        },
      },
    },
    medi: {
      "0": {
        written: ["I"],
        locales: {
          MNGx: {
            conditions: ["default"],
          },
          TOD: {
            conditions: ["default"],
            gb: "1855 todo ya first medial form",
            eac: "TYAZ1",
          },
          TODx: {
            conditions: ["default"],
          },
        },
      },
      "1": {
        written: ["Y"],
        locales: {
          TOD: {
            gb: "1836 todo ya second medial form",
            eac: "TYAZ2",
          },
        },
      },
    },
    fina: {
      "0": {
        written: ["I3"],
        locales: {
          MNGx: {
            written: ["I4"],
            conditions: ["default"],
          },
          TOD: {
            conditions: ["default"],
            gb: "0044 todo ya final form",
            eac: "TYAM1",
          },
          TODx: {
            written: ["medi", 0],
            conditions: ["default"],
          },
        },
      },
    },
  },
  "MONGOLIAN LETTER TODO WA": {
    isol: {
      "0": {
        written: ["init", 0],
        locales: {
          TOD: {
            conditions: ["default"],
            gb: "1856 todo wa isolated form",
            eac: "TWAD1",
          },
          TODx: {
            conditions: ["default"],
          },
        },
      },
    },
    init: {
      "0": {
        written: ["Wb"],
        locales: {
          TOD: {
            conditions: ["default"],
            gb: "1856 todo wa initial form",
            eac: "TWAS1",
          },
          TODx: {
            conditions: ["default"],
          },
        },
      },
    },
    medi: {
      "0": {
        written: ["Wb"],
        locales: {
          TOD: {
            conditions: ["default"],
            gb: "1856 todo wa first medial form",
            eac: "TWAZ1",
          },
          TODx: {
            conditions: ["default"],
          },
        },
      },
      "1": {
        written: ["O"],
        locales: {
          TOD: {
            gb: "000C todo wa second medial form",
          },
        },
      },
    },
    fina: {
      "0": {
        written: ["Wb"],
        locales: {
          TOD: {
            conditions: ["default"],
            gb: "005B todo wa first final form",
            eac: "TWAM1",
          },
          TODx: {
            written: ["medi", 0],
            conditions: ["default"],
          },
        },
      },
      "1": {
        written: ["U"],
        locales: {
          TOD: {
            gb: "000E todo wa second final form",
          },
        },
      },
    },
  },
  "MONGOLIAN LETTER TODO KA": {
    isol: {
      "0": {
        written: ["init", 0],
        locales: {
          TOD: {
            conditions: ["default"],
            gb: "1857 todo ka isolated form",
            eac: "TEKAD1",
          },
        },
      },
    },
    init: {
      "0": {
        written: ["Kp"],
        locales: {
          TOD: {
            conditions: ["default"],
            gb: "1857 todo ka initial form",
            eac: "TEKAS1",
          },
        },
      },
    },
    medi: {
      "0": {
        written: ["Kp"],
        locales: {
          TOD: {
            conditions: ["default"],
            gb: "1857 todo ka medial form",
            eac: "TEKAZ1",
          },
        },
      },
    },
    fina: {
      "0": {
        written: ["Kp"],
        locales: {
          TOD: {
            conditions: ["default"],
            gb: "005C todo ka final form",
            eac: "TEKAM1",
          },
        },
      },
    },
  },
  "MONGOLIAN LETTER TODO GAA": {
    isol: {
      "0": {
        written: ["init", 0],
        locales: {
          TOD: {
            conditions: ["default"],
            gb: "1858 todo gaa isolated form",
            eac: "TGAAD1",
          },
        },
      },
    },
    init: {
      "0": {
        written: ["Gp"],
        locales: {
          TOD: {
            conditions: ["default"],
            gb: "1858 todo gaa initial form",
            eac: "TGAAS1",
          },
        },
      },
    },
    medi: {
      "0": {
        written: ["Gp"],
        locales: {
          TOD: {
            conditions: ["default"],
            gb: "1858 todo gaa medial form",
            eac: "TGAAZ1",
          },
        },
      },
    },
    fina: {
      "0": {
        written: ["medi", 0],
        locales: {
          TOD: {
            conditions: ["default"],
            gb: "1858 todo gaa final form",
            eac: "TGAAM1",
          },
        },
      },
    },
  },
  "MONGOLIAN LETTER TODO HAA": {
    isol: {
      "0": {
        written: ["init", 0],
        locales: {
          MNGx: {
            conditions: ["default"],
          },
          TOD: {
            conditions: ["default"],
            gb: "183E todo haa isolated form",
            eac: "THAAD1",
          },
          TODx: {
            conditions: ["default"],
          },
        },
      },
    },
    init: {
      "0": {
        written: ["A", "Hr"],
        locales: {
          MNGx: {
            conditions: ["default"],
          },
          TOD: {
            conditions: ["default"],
            gb: "183E todo haa first initial form",
            eac: "THAAS1",
          },
          TODx: {
            conditions: ["default"],
          },
        },
      },
    },
    medi: {
      "0": {
        written: ["A", "Hr"],
        locales: {
          MNGx: {
            conditions: ["default"],
          },
          TOD: {
            conditions: ["default"],
            gb: "005D todo haa first medial form",
            eac: "THAAZ1",
          },
          TODx: {
            conditions: ["default"],
          },
        },
      },
    },
    fina: {
      "0": {
        written: ["A", "Hr"],
        locales: {
          MNGx: {
            written: ["Hr"],
            conditions: ["default"],
          },
          TOD: {
            conditions: ["default"],
            gb: "1859 todo haa first final form",
            eac: "THAAM1",
          },
          TODx: {
            conditions: ["default"],
          },
        },
      },
    },
  },
  "MONGOLIAN LETTER TODO JIA": {
    isol: {
      "0": {
        written: ["init", 0],
        locales: {
          TOD: {
            conditions: ["default"],
            gb: "185A todo jia isolated form",
            eac: "TAKAD1",
          },
        },
      },
    },
    init: {
      "0": {
        written: ["B", "Yp"],
        locales: {
          TOD: {
            conditions: ["default"],
            gb: "185A todo jia initial form",
            eac: "TAKAS1",
          },
        },
      },
    },
    medi: {
      "0": {
        written: ["B", "Yp"],
        locales: {
          TOD: {
            conditions: ["default"],
            gb: "185A todo jia medial form",
            eac: "TAKAZ1",
          },
        },
      },
    },
    fina: {
      "0": {
        written: ["medi", 0],
        locales: {
          TOD: {
            conditions: ["default"],
            gb: "185A todo jia final form",
            eac: "TAKAM1",
          },
        },
      },
    },
  },
  "MONGOLIAN LETTER TODO NIA": {
    isol: {
      "0": {
        written: ["init", 0],
        locales: {
          MNGx: {
            conditions: ["default"],
          },
          TOD: {
            conditions: ["default"],
            gb: "185B todo nia isolated form",
            eac: "TANAD1",
          },
          TODx: {
            conditions: ["default"],
          },
        },
      },
    },
    init: {
      "0": {
        written: ["Ny"],
        locales: {
          MNGx: {
            conditions: ["default"],
          },
          TOD: {
            conditions: ["default"],
            gb: "185B todo nia initial form",
            eac: "TANAS1",
          },
          TODx: {
            conditions: ["default"],
          },
        },
      },
    },
    medi: {
      "0": {
        written: ["Ny"],
        locales: {
          MNGx: {
            conditions: ["default"],
          },
          TOD: {
            conditions: ["default"],
            gb: "185B todo nia medial form",
            eac: "TANAZ1",
          },
          TODx: {
            conditions: ["default"],
          },
        },
      },
    },
    fina: {
      "0": {
        written: ["medi", 0],
        locales: {
          MNGx: {
            written: ["Ny"],
            conditions: ["default"],
          },
          TOD: {
            conditions: ["default"],
            gb: "185B todo nia final form",
            eac: "TANAM1",
          },
          TODx: {
            conditions: ["default"],
          },
        },
      },
    },
  },
  "MONGOLIAN LETTER TODO DZA": {
    isol: {
      "0": {
        written: ["init", 0],
        locales: {
          TOD: {
            conditions: ["default"],
            gb: "185C todo dza isolated form",
            eac: "TADZAD1",
          },
          TODx: {
            written: ["init", 0, "TODx"],
            conditions: ["default"],
          },
        },
      },
    },
    init: {
      "0": {
        written: ["Zz"],
        locales: {
          TOD: {
            conditions: ["default"],
            gb: "185C todo dza first initial form",
            eac: "TADZAS1",
          },
          TODx: {
            written: ["Zc"],
            conditions: ["default"],
          },
        },
      },
    },
    medi: {
      "0": {
        written: ["Zz"],
        locales: {
          TOD: {
            conditions: ["default"],
            gb: "005E todo dza first medial form",
            eac: "TADZAZ1",
          },
          TODx: {
            written: ["Zc"],
            conditions: ["default"],
          },
        },
      },
    },
    fina: {
      "0": {
        written: ["Zz"],
        locales: {
          TOD: {
            conditions: ["default"],
            gb: "005F todo dza first final form",
            eac: "TADZAM1",
          },
          TODx: {
            written: ["Zc"],
            conditions: ["default"],
          },
        },
      },
    },
  },
  "MONGOLIAN LETTER SIBE E": {
    isol: {
      "0": {
        written: ["A"],
        locales: {
          SIB: {
            conditions: ["default"],
            eac: "SED1",
          },
          MCH: {
            conditions: ["default"],
            gb: "1821 manchu e isolated form",
            eac: "MED1",
          },
          MCHx: {
            conditions: ["default"],
          },
        },
      },
    },
    init: {
      "0": {
        written: ["A"],
        locales: {
          SIB: {
            conditions: ["default"],
            eac: "SES1",
          },
          MCH: {
            conditions: ["default"],
            gb: "0007 manchu e initial form",
            eac: "MES1",
          },
          MCHx: {
            conditions: ["default"],
          },
        },
      },
    },
    medi: {
      "1": {
        written: ["A"],
        locales: {
          SIB: {
            conditions: ["feminine"],
            eac: "SEZ2",
          },
          MCH: {
            conditions: ["feminine"],
            gb: "0005 manchu e second medial form",
            eac: "MEZ2",
          },
          MCHx: {
            conditions: ["feminine"],
          },
        },
      },
      "2": {
        written: ["Ah"],
        locales: {
          SIB: {
            conditions: ["default"],
            eac: "SEZ1",
          },
          MCH: {
            conditions: ["default"],
            gb: "0060 manchu e first medial form",
            eac: "MEZ1",
          },
          MCHx: {
            conditions: ["default"],
          },
        },
      },
    },
    fina: {
      "1": {
        written: ["A"],
        locales: {
          SIB: {
            conditions: ["feminine"],
            eac: "SEM2",
          },
          MCH: {
            conditions: ["feminine"],
            gb: "0008 manchu e second final form",
            eac: "MEM2",
          },
          MCHx: {
            conditions: ["feminine"],
          },
        },
      },
      "2": {
        written: ["At"],
        locales: {
          SIB: {
            conditions: ["post_bowed"],
            eac: "SEM3",
          },
          MCH: {
            conditions: ["post_bowed"],
            eac: "MEM3",
          },
          MCHx: {
            conditions: ["post_bowed"],
          },
        },
      },
      "3": {
        written: ["Aa"],
        locales: {
          SIB: {
            conditions: ["post_bowed"],
            eac: "SEM4",
          },
          MCH: {
            conditions: ["post_bowed"],
            eac: "MEM4",
          },
          MCHx: {
            conditions: ["post_bowed"],
          },
        },
      },
      "4": {
        written: ["Ah"],
        locales: {
          SIB: {
            conditions: ["default"],
            eac: "SEM1",
          },
          MCH: {
            conditions: ["default"],
            gb: "185D manchu e first final form",
            eac: "MEM1",
          },
          MCHx: {
            conditions: ["default"],
          },
        },
      },
    },
  },
  "MONGOLIAN LETTER SIBE I": {
    isol: {
      "1": {
        written: ["I"],
        locales: {
          SIB: {
            conditions: ["particle"],
          },
        },
      },
      "2": {
        written: ["A", "I"],
        locales: {
          SIB: {
            conditions: ["default"],
            eac: "SID1",
          },
        },
      },
    },
    init: {
      "0": {
        written: ["A", "I"],
        locales: {
          SIB: {
            conditions: ["default"],
            eac: "SIS1",
          },
        },
      },
    },
    medi: {
      "2": {
        written: ["A", "I"],
        locales: {
          SIB: {
            conditions: ["devsger"],
            eac: "SIZ2",
          },
        },
      },
      "3": {
        written: ["I"],
        locales: {
          SIB: {
            conditions: ["default"],
            eac: "SIZ1",
          },
        },
      },
    },
    fina: {
      "1": {
        written: ["I2"],
        locales: {
          SIB: {
            conditions: ["marked"],
            eac: "SIM2",
          },
        },
      },
      "2": {
        written: ["A", "I"],
        locales: {
          SIB: {
            gb: "1834 sibe cha second final form",
            eac: "SIM3",
          },
        },
      },
      "3": {
        written: ["I"],
        locales: {
          SIB: {
            conditions: ["default"],
            eac: "SIM1",
          },
        },
      },
    },
  },
  "MONGOLIAN LETTER SIBE IY": {
    isol: {
      "0": {
        written: ["medi", 0],
        locales: {
          SIB: {
            conditions: ["default"],
            eac: "SIYD1",
          },
          MCH: {
            conditions: ["default"],
            eac: "MIYD1",
          },
          MCHx: {
            conditions: ["default"],
          },
        },
      },
    },
    init: {
      "0": {
        written: ["medi", 0],
        locales: {
          SIB: {
            conditions: ["default"],
            eac: "SIYS1",
          },
          MCH: {
            conditions: ["default"],
            eac: "MIYS1",
          },
          MCHx: {
            conditions: ["default"],
          },
        },
      },
    },
    medi: {
      "0": {
        written: ["Ai"],
        locales: {
          SIB: {
            conditions: ["default"],
            gb: "185F sibe iy medial form",
            eac: "SIYZ1",
          },
          MCH: {
            conditions: ["default"],
            gb: "185F manchu iy medial form",
            eac: "MIYZ1",
          },
          MCHx: {
            conditions: ["default"],
          },
        },
      },
    },
    fina: {
      "0": {
        written: ["Ai"],
        locales: {
          SIB: {
            conditions: ["default"],
            gb: "185F sibe iy final form",
            eac: "SIYM1",
          },
          MCH: {
            conditions: ["default"],
            gb: "0064 manchu iy final form",
            eac: "MIYM1",
          },
          MCHx: {
            conditions: ["default"],
          },
        },
      },
    },
  },
  "MONGOLIAN LETTER SIBE UE": {
    isol: {
      "0": {
        written: ["A", "Oh"],
        locales: {
          SIB: {
            conditions: ["default"],
            gb: "1860 sibe ue isolated form",
            eac: "SUED1",
          },
          MCH: {
            conditions: ["default"],
            gb: "1860 manchu ue isolated form",
            eac: "MUED1",
          },
          MCHx: {
            conditions: ["default"],
          },
        },
      },
    },
    init: {
      "0": {
        written: ["A", "Oh"],
        locales: {
          SIB: {
            conditions: ["default"],
            gb: "1860 sibe ue initial form",
            eac: "SUES1",
          },
          MCH: {
            conditions: ["default"],
            gb: "0065 manchu ue initial form",
            eac: "MUES1",
          },
          MCHx: {
            conditions: ["default"],
          },
        },
      },
    },
    medi: {
      "1": {
        written: ["O"],
        locales: {
          SIB: {
            conditions: ["feminine"],
            gb: "1860 sibe ue second medial form",
            eac: "SUEZ2",
          },
          MCH: {
            conditions: ["feminine"],
            gb: "000C manchu ue second medial form",
            eac: "MUEZ2",
          },
          MCHx: {
            conditions: ["feminine"],
          },
        },
      },
      "2": {
        written: ["Oh"],
        locales: {
          SIB: {
            conditions: ["default"],
            gb: "1860 sibe ue first medial form",
            eac: "SUEZ1",
          },
          MCH: {
            conditions: ["default"],
            gb: "0066 manchu ue first medial form",
            eac: "MUEZ1",
          },
          MCHx: {
            conditions: ["default"],
          },
        },
      },
    },
    fina: {
      "1": {
        written: ["U"],
        locales: {
          SIB: {
            conditions: ["feminine"],
            gb: "1860 sibe ue second final form",
            eac: "SUEM2",
          },
          MCH: {
            conditions: ["feminine"],
            gb: "000E manchu ue second final form",
            eac: "MUEM2",
          },
          MCHx: {
            conditions: ["feminine"],
          },
        },
      },
      "2": {
        written: ["Oh"],
        locales: {
          SIB: {
            conditions: ["marked", "post_bowed"],
            gb: "1860 sibe ue third final form",
            eac: "SUEM3",
          },
          MCH: {
            conditions: ["marked", "post_bowed"],
            gb: "0068 manchu ue third final form",
            eac: "MUEM3",
          },
          MCHx: {
            conditions: ["marked", "post_bowed"],
          },
        },
      },
      "3": {
        written: ["O"],
        locales: {
          SIB: {
            conditions: ["feminine", "post_bowed"],
            gb: "1860 sibe ue fourth final form",
            eac: "SUEM4",
          },
          MCH: {
            conditions: ["feminine", "post_bowed"],
            gb: "000F manchu ue fourth final form",
            eac: "MUEM4",
          },
          MCHx: {
            conditions: ["feminine", "post_bowed"],
          },
        },
      },
      "4": {
        written: ["Uh"],
        locales: {
          SIB: {
            conditions: ["default"],
            gb: "1860 sibe ue first final form",
            eac: "SUEM1",
          },
          MCH: {
            conditions: ["default"],
            gb: "0067 manchu ue first final form",
            eac: "MUEM1",
          },
          MCHx: {
            conditions: ["default"],
          },
        },
      },
    },
  },
  "MONGOLIAN LETTER SIBE U": {
    isol: {
      "0": {
        written: ["A", "Ue"],
        locales: {
          SIB: {
            conditions: ["default"],
            eac: "SUD1",
          },
          MCH: {
            conditions: ["default"],
            gb: "1825 manchu u isolated form",
            eac: "MUD1",
          },
          MCHx: {
            conditions: ["default"],
          },
        },
      },
    },
    init: {
      "0": {
        written: ["A", "O", "I"],
        locales: {
          SIB: {
            conditions: ["default"],
            eac: "SUS1",
          },
          MCH: {
            conditions: ["default"],
            gb: "1826 manchu u initial form",
            eac: "MUS1",
          },
          MCHx: {
            conditions: ["default"],
          },
        },
      },
    },
    medi: {
      "0": {
        written: ["O", "I"],
        locales: {
          SIB: {
            conditions: ["default"],
            gb: "1861 sibe u medial form",
            eac: "SUZ1",
          },
          MCH: {
            conditions: ["default"],
            gb: "1861 manchu u medial form",
            eac: "MUZ1",
          },
          MCHx: {
            conditions: ["default"],
          },
        },
      },
    },
    fina: {
      "0": {
        written: ["Ue"],
        locales: {
          SIB: {
            conditions: ["default"],
            gb: "1861 sibe u final form",
            eac: "SUM1",
          },
          MCH: {
            conditions: ["default"],
            gb: "0011 manchu u final form",
            eac: "MUM1",
          },
          MCHx: {
            conditions: ["default"],
          },
        },
      },
    },
  },
  "MONGOLIAN LETTER SIBE ANG": {
    isol: {
      "0": {
        written: ["medi", 0],
        locales: {
          SIB: {
            conditions: ["default"],
            eac: "SANGD1",
          },
        },
      },
    },
    init: {
      "0": {
        written: ["medi", 0],
        locales: {
          SIB: {
            conditions: ["default"],
            eac: "SANGS1",
          },
        },
      },
    },
    medi: {
      "0": {
        written: ["A", "G"],
        locales: {
          SIB: {
            conditions: ["default"],
            gb: "1862 sibe ang medial form",
            eac: "SANGZ1",
          },
        },
      },
    },
    fina: {
      "0": {
        written: ["A", "G3"],
        locales: {
          SIB: {
            conditions: ["default"],
            gb: "1862 sibe ang final form",
            eac: "SANGM1",
          },
        },
      },
    },
  },
  "MONGOLIAN LETTER SIBE KA": {
    isol: {
      "0": {
        written: ["init", 3],
        locales: {
          SIB: {
            conditions: ["default"],
            eac: "SKAD1",
          },
        },
      },
      "1": {
        written: ["init", 1],
        locales: {
          SIB: {
            eac: "SKAD2",
          },
        },
      },
      "2": {
        written: ["init", 2],
        locales: {
          SIB: {
            eac: "SKAD3",
          },
        },
      },
    },
    init: {
      "1": {
        written: ["G"],
        locales: {
          SIB: {
            conditions: ["feminine"],
            gb: "1863 sibe ka initial form",
            eac: "SKAS2",
          },
        },
      },
      "2": {
        written: ["Gx"],
        locales: {
          SIB: {
            eac: "SKAS3",
          },
        },
      },
      "3": {
        written: ["H"],
        locales: {
          SIB: {
            conditions: ["default", "masculine_onset"],
            eac: "SKAS1",
          },
        },
      },
    },
    medi: {
      "1": {
        written: ["Nx"],
        locales: {
          SIB: {
            conditions: ["devsger"],
            gb: "1863 sibe ka medial form",
            eac: "SKAZ2",
          },
        },
      },
      "2": {
        written: ["G"],
        locales: {
          SIB: {
            conditions: ["feminine"],
            eac: "SKAZ3",
          },
        },
      },
      "3": {
        written: ["H"],
        locales: {
          SIB: {
            conditions: ["default", "masculine_onset"],
            eac: "SKAZ1",
          },
        },
      },
      "4": {
        written: ["Gx"],
        locales: {
          SIB: {
            eac: "SKAZ4",
          },
        },
      },
    },
    fina: {
      "0": {
        written: ["Nx"],
        locales: {
          SIB: {
            conditions: ["default"],
            gb: "1863 sibe ka final form",
            eac: "SKAM1",
          },
        },
      },
      "1": {
        written: ["G4"],
        locales: {
          SIB: {
            eac: "SKAM2",
          },
        },
      },
      "2": {
        written: ["Gx"],
        locales: {
          SIB: {
            eac: "SKAM3",
          },
        },
      },
    },
  },
  "MONGOLIAN LETTER SIBE GA": {
    isol: {
      "0": {
        written: ["init", 2],
        locales: {
          SIB: {
            conditions: ["default"],
            eac: "SGAD1",
          },
          MCH: {
            conditions: ["default"],
            eac: "MGAD1",
          },
          MCHx: {
            conditions: ["default"],
          },
        },
      },
      "1": {
        written: ["init", 1],
        locales: {
          SIB: {
            eac: "SGAD2",
          },
          MCH: {
            eac: "MGAD2",
          },
          MCHx: {},
        },
      },
    },
    init: {
      "1": {
        written: ["Gh"],
        locales: {
          SIB: {
            conditions: ["feminine"],
            eac: "SGAS2",
          },
          MCH: {
            conditions: ["feminine"],
            gb: "006B manchu ga second initial form",
            eac: "MGAS2",
          },
          MCHx: {
            conditions: ["feminine"],
          },
        },
      },
      "2": {
        written: ["Hh"],
        locales: {
          SIB: {
            conditions: ["default", "masculine_onset"],
            gb: "1864 sibe ga initial form",
            eac: "SGAS1",
          },
          MCH: {
            conditions: ["default", "masculine_onset"],
            gb: "1864 manchu ga first initial form",
            eac: "MGAS1",
          },
          MCHx: {
            conditions: ["default", "masculine_onset"],
          },
        },
      },
    },
    medi: {
      "1": {
        written: ["Gh"],
        locales: {
          SIB: {
            conditions: ["feminine"],
            eac: "SGAZ2",
          },
          MCH: {
            conditions: ["feminine"],
            gb: "030D manchu ga second medial form",
            eac: "MGAZ2",
          },
          MCHx: {
            conditions: ["feminine"],
          },
        },
      },
      "2": {
        written: ["Hh"],
        locales: {
          SIB: {
            conditions: ["default", "masculine_onset"],
            gb: "1864 sibe ga medial form",
            eac: "SGAZ1",
          },
          MCH: {
            conditions: ["default", "masculine_onset"],
            gb: "006A manchu ga first medial form",
            eac: "MGAZ1",
          },
          MCHx: {
            conditions: ["default", "masculine_onset"],
          },
        },
      },
    },
    fina: {
      "0": {
        written: ["medi", 2],
        locales: {
          SIB: {
            conditions: ["default"],
            eac: "SGAM1",
          },
          MCH: {
            conditions: ["default"],
            eac: "MGAM1",
          },
          MCHx: {
            conditions: ["default"],
          },
        },
      },
    },
  },
  "MONGOLIAN LETTER SIBE HA": {
    isol: {
      "0": {
        written: ["init", 2],
        locales: {
          SIB: {
            conditions: ["default"],
            eac: "SHAD1",
          },
          MCH: {
            conditions: ["default"],
            eac: "MHAD1",
          },
          MCHx: {
            conditions: ["default"],
          },
        },
      },
      "1": {
        written: ["init", 1],
        locales: {
          SIB: {
            eac: "SHAD2",
          },
          MCH: {
            eac: "MHAD2",
          },
          MCHx: {},
        },
      },
    },
    init: {
      "1": {
        written: ["Gc"],
        locales: {
          SIB: {
            conditions: ["feminine"],
            eac: "SHAS2",
          },
          MCH: {
            conditions: ["feminine"],
            gb: "006D manchu ha second initial form",
            eac: "MHAS2",
          },
          MCHx: {
            conditions: ["feminine"],
          },
        },
      },
      "2": {
        written: ["Hc"],
        locales: {
          SIB: {
            conditions: ["default", "masculine_onset"],
            gb: "1865 sibe ha initial form",
            eac: "SHAS1",
          },
          MCH: {
            conditions: ["default", "masculine_onset"],
            gb: "1865 manchu ha first initial form",
            eac: "MHAS1",
          },
          MCHx: {
            conditions: ["default", "masculine_onset"],
          },
        },
      },
    },
    medi: {
      "1": {
        written: ["Gc"],
        locales: {
          SIB: {
            conditions: ["feminine"],
            eac: "SHAZ2",
          },
          MCH: {
            conditions: ["feminine"],
            gb: "030E manchu ha second medial form",
            eac: "MHAZ2",
          },
          MCHx: {
            conditions: ["feminine"],
          },
        },
      },
      "2": {
        written: ["Hc"],
        locales: {
          SIB: {
            conditions: ["default", "masculine_onset"],
            gb: "1865 sibe ha medial form",
            eac: "SHAZ1",
          },
          MCH: {
            conditions: ["default", "masculine_onset"],
            gb: "006C manchu ha first medial form",
            eac: "MHAZ1",
          },
          MCHx: {
            conditions: ["default", "masculine_onset"],
          },
        },
      },
    },
    fina: {
      "0": {
        written: ["medi", 2],
        locales: {
          SIB: {
            conditions: ["default"],
            eac: "SHAM1",
          },
          MCH: {
            conditions: ["default"],
            eac: "MHAM1",
          },
          MCHx: {
            conditions: ["default"],
          },
        },
      },
    },
  },
  "MONGOLIAN LETTER SIBE PA": {
    isol: {
      "0": {
        written: ["init", 0],
        locales: {
          SIB: {
            conditions: ["default"],
            eac: "SPAD1",
          },
          MCH: {
            conditions: ["default"],
            eac: "MPAD1",
          },
          MCHx: {
            conditions: ["default"],
          },
        },
      },
    },
    init: {
      "0": {
        written: ["Pb"],
        locales: {
          SIB: {
            conditions: ["default"],
            gb: "1866 sibe pa initial form",
            eac: "SPAS1",
          },
          MCH: {
            conditions: ["default"],
            gb: "1866 manchu pa first initial form",
            eac: "MPAS1",
          },
          MCHx: {
            conditions: ["default"],
          },
        },
      },
    },
    medi: {
      "0": {
        written: ["Pb"],
        locales: {
          SIB: {
            conditions: ["default"],
            gb: "1866 sibe pa medial form",
            eac: "SPAZ1",
          },
          MCH: {
            conditions: ["default"],
            gb: "1866 manchu pa first medial form",
            eac: "MPAZ1",
          },
          MCHx: {
            conditions: ["default"],
          },
        },
      },
    },
    fina: {
      "0": {
        written: ["medi", 0],
        locales: {
          SIB: {
            conditions: ["default"],
            eac: "SPAM1",
          },
          MCH: {
            conditions: ["default"],
            eac: "MPAM1",
          },
          MCHx: {
            conditions: ["default"],
          },
        },
      },
    },
  },
  "MONGOLIAN LETTER SIBE SHA": {
    isol: {
      "0": {
        written: ["init", 0],
        locales: {
          SIB: {
            conditions: ["default"],
            eac: "SSHAD1",
          },
          MCH: {
            conditions: ["default"],
            eac: "MSHAD1",
          },
          MCHx: {
            conditions: ["default"],
          },
        },
      },
    },
    init: {
      "0": {
        written: ["Sp"],
        locales: {
          SIB: {
            conditions: ["default"],
            gb: "1867 sibe sha initial form",
            eac: "SSHAS1",
          },
          MCH: {
            conditions: ["default"],
            gb: "1867 manchu sha initial form",
            eac: "MSHAS1",
          },
          MCHx: {
            conditions: ["default"],
          },
        },
      },
    },
    medi: {
      "0": {
        written: ["Sp"],
        locales: {
          SIB: {
            conditions: ["default"],
            gb: "1867 sibe sha medial form",
            eac: "SSHAZ1",
          },
          MCH: {
            conditions: ["default"],
            gb: "006E manchu sha medial form",
            eac: "MSHAZ1",
          },
          MCHx: {
            conditions: ["default"],
          },
        },
      },
    },
    fina: {
      "0": {
        written: ["Sp"],
        locales: {
          SIB: {
            conditions: ["default"],
            eac: "SSHAM1",
          },
          MCH: {
            conditions: ["default"],
            gb: "006F manchu sha final form",
            eac: "MSHAM1",
          },
          MCHx: {
            conditions: ["default"],
          },
        },
      },
    },
  },
  "MONGOLIAN LETTER SIBE TA": {
    isol: {
      "0": {
        written: ["init", 2],
        locales: {
          SIB: {
            conditions: ["default"],
            eac: "STAD1",
          },
          MCH: {
            conditions: ["default"],
            eac: "MTAD1",
          },
          MCHx: {
            conditions: ["default"],
          },
        },
      },
      "1": {
        written: ["init", 1],
        locales: {
          SIB: {
            eac: "STAD2",
          },
          MCH: {
            eac: "MTAD2",
          },
          MCHx: {},
        },
      },
    },
    init: {
      "1": {
        written: ["T"],
        locales: {
          SIB: {
            conditions: ["masculine_onset"],
            gb: "1868 sibe ta second initial form",
            eac: "STAS2",
          },
          MCH: {
            conditions: ["masculine_onset"],
            gb: "1832 manchu ta second initial form",
            eac: "MTAS2",
          },
          MCHx: {
            conditions: ["masculine_onset"],
          },
        },
      },
      "2": {
        written: ["Tb"],
        locales: {
          SIB: {
            conditions: ["default", "feminine"],
            gb: "1868 sibe ta first initial form",
            eac: "STAS1",
          },
          MCH: {
            conditions: ["default", "feminine"],
            gb: "1868 manchu ta first initial form",
            eac: "MTAS1",
          },
          MCHx: {
            conditions: ["default", "feminine"],
          },
        },
      },
    },
    medi: {
      "1": {
        written: ["D"],
        locales: {
          SIB: {
            conditions: ["masculine_onset"],
            gb: "1868 sibe ta second medial form",
            eac: "STAZ2",
          },
          MCH: {
            conditions: ["masculine_onset"],
            gb: "1833 manchu ta second medial form",
            eac: "MTAZ2",
          },
          MCHx: {
            conditions: ["masculine_onset"],
          },
        },
      },
      "2": {
        written: ["Dd"],
        locales: {
          SIB: {
            conditions: ["devsger"],
            gb: "1868 sibe ta third medial form",
            eac: "STAZ3",
          },
          MCH: {
            conditions: ["devsger"],
            gb: "002C manchu ta third medial form",
            eac: "MTAZ3",
          },
          MCHx: {
            conditions: ["devsger"],
          },
        },
      },
      "3": {
        written: ["Db"],
        locales: {
          SIB: {
            conditions: ["default", "feminine"],
            gb: "1868 sibe ta first medial form",
            eac: "STAZ1",
          },
          MCH: {
            conditions: ["default", "feminine"],
            gb: "0070 manchu ta first medial form",
            eac: "MTAZ1",
          },
          MCHx: {
            conditions: ["default", "feminine"],
          },
        },
      },
    },
    fina: {
      "0": {
        written: ["Dd"],
        locales: {
          SIB: {
            conditions: ["default"],
            gb: "1868 sibe ta first final form",
            eac: "STAM1",
          },
          MCH: {
            conditions: ["default"],
            gb: "002D manchu ta final form",
            eac: "MTAM1",
          },
          MCHx: {
            conditions: ["default"],
          },
        },
      },
    },
  },
  "MONGOLIAN LETTER SIBE DA": {
    isol: {
      "0": {
        written: ["init", 2],
        locales: {
          SIB: {
            conditions: ["default"],
            eac: "SDAD1",
          },
          MCH: {
            conditions: ["default"],
            eac: "MDAD1",
          },
          MCHx: {
            conditions: ["default"],
          },
        },
      },
      "1": {
        written: ["init", 1],
        locales: {
          SIB: {
            eac: "SDAD2",
          },
          MCH: {
            eac: "MDAD2",
          },
          MCHx: {},
        },
      },
    },
    init: {
      "1": {
        written: ["Tt"],
        locales: {
          SIB: {
            conditions: ["feminine"],
            gb: "1869 sibe da second initial form",
            eac: "SDAS2",
          },
          MCH: {
            conditions: ["feminine"],
            gb: "0071 manchu da second initial form",
            eac: "MDAS2",
          },
          MCHx: {
            conditions: ["feminine"],
          },
        },
      },
      "2": {
        written: ["Th"],
        locales: {
          SIB: {
            conditions: ["default", "masculine_onset"],
            gb: "1869 sibe da first initial form",
            eac: "SDAS1",
          },
          MCH: {
            conditions: ["default", "masculine_onset"],
            gb: "1869 manchu da first initial form",
            eac: "MDAS1",
          },
          MCHx: {
            conditions: ["default", "masculine_onset"],
          },
        },
      },
    },
    medi: {
      "1": {
        written: ["Dt"],
        locales: {
          SIB: {
            conditions: ["default"],
            gb: "1869 sibe da second medial form",
            eac: "SDAZ1",
          },
          MCH: {
            conditions: ["feminine"],
            gb: "0073 manchu da second medial form",
            eac: "MDAZ2",
          },
          MCHx: {
            conditions: ["feminine"],
          },
        },
      },
      "2": {
        written: ["Dh"],
        locales: {
          SIB: {
            conditions: ["default", "masculine_onset"],
            gb: "1869 sibe da first medial form",
            eac: "SDAZ2",
          },
          MCH: {
            conditions: ["default", "masculine_onset"],
            gb: "0072 manchu da first medial form",
            eac: "MDAZ1",
          },
          MCHx: {
            conditions: ["default", "masculine_onset"],
          },
        },
      },
    },
    fina: {
      "0": {
        written: ["medi", 2],
        locales: {
          SIB: {
            conditions: ["default"],
            eac: "SDAM1",
          },
          MCH: {
            conditions: ["default"],
            eac: "MDAM1",
          },
          MCHx: {
            conditions: ["default"],
          },
        },
      },
    },
  },
  "MONGOLIAN LETTER SIBE JA": {
    isol: {
      "0": {
        written: ["init", 0],
        locales: {
          SIB: {
            conditions: ["default"],
            eac: "SJAD1",
          },
        },
      },
    },
    init: {
      "0": {
        written: ["I"],
        locales: {
          SIB: {
            conditions: ["default"],
            gb: "186A sibe ja initial form",
            eac: "SJAS1",
          },
        },
      },
    },
    medi: {
      "0": {
        written: ["J2"],
        locales: {
          SIB: {
            conditions: ["default"],
            gb: "186A sibe ja medial form",
            eac: "SJAZ1",
          },
        },
      },
    },
    fina: {
      "0": {
        written: ["medi", 0],
        locales: {
          SIB: {
            conditions: ["default"],
            eac: "SJAM1",
          },
        },
      },
    },
  },
  "MONGOLIAN LETTER SIBE FA": {
    isol: {
      "0": {
        written: ["init", 0],
        locales: {
          SIB: {
            conditions: ["default"],
            eac: "SFAD1",
          },
        },
      },
    },
    init: {
      "0": {
        written: ["V"],
        locales: {
          SIB: {
            conditions: ["default"],
            gb: "186B sibe fa initial form",
            eac: "SFAS1",
          },
        },
      },
    },
    medi: {
      "0": {
        written: ["V"],
        locales: {
          SIB: {
            conditions: ["default"],
            gb: "186B sibe fa medial form",
            eac: "SFAZ1",
          },
        },
      },
    },
    fina: {
      "0": {
        written: ["medi", 0],
        locales: {
          SIB: {
            conditions: ["default"],
            eac: "SFAM1",
          },
        },
      },
    },
  },
  "MONGOLIAN LETTER SIBE GAA": {
    isol: {
      "0": {
        written: ["init", 0],
        locales: {
          SIB: {
            conditions: ["default"],
            eac: "SGAAD1",
          },
          MCH: {
            conditions: ["default"],
            eac: "MGAAD1",
          },
          MCHx: {
            conditions: ["default"],
          },
        },
      },
    },
    init: {
      "0": {
        written: ["Kh"],
        locales: {
          SIB: {
            conditions: ["default"],
            gb: "186C sibe gaa initial form",
            eac: "SGAAS1",
          },
          MCH: {
            conditions: ["default"],
            gb: "186C manchu gaa initial form",
            eac: "MGAAS1",
          },
          MCHx: {
            conditions: ["default"],
          },
        },
      },
    },
    medi: {
      "0": {
        written: ["Kh"],
        locales: {
          SIB: {
            conditions: ["default"],
            gb: "186C sibe gaa medial form",
            eac: "SGAAZ1",
          },
          MCH: {
            conditions: ["default"],
            gb: "186C manchu gaa medial form",
            eac: "MGAAZ1",
          },
          MCHx: {
            conditions: ["default"],
          },
        },
      },
    },
    fina: {
      "0": {
        written: ["medi", 0],
        locales: {
          SIB: {
            conditions: ["default"],
            eac: "SGAAM1",
          },
          MCH: {
            conditions: ["default"],
            eac: "MGAAM1",
          },
          MCHx: {
            conditions: ["default"],
          },
        },
      },
    },
  },
  "MONGOLIAN LETTER SIBE HAA": {
    isol: {
      "0": {
        written: ["init", 0],
        locales: {
          SIB: {
            conditions: ["default"],
            eac: "SHAAD1",
          },
          MCH: {
            conditions: ["default"],
            eac: "MHAAD1",
          },
        },
      },
    },
    init: {
      "0": {
        written: ["Kc"],
        locales: {
          SIB: {
            conditions: ["default"],
            gb: "186D sibe haa initial form",
            eac: "SHAAS1",
          },
          MCH: {
            conditions: ["default"],
            gb: "186D manchu haa initial form",
            eac: "MHAAS1",
          },
        },
      },
    },
    medi: {
      "0": {
        written: ["Kc"],
        locales: {
          SIB: {
            conditions: ["default"],
            gb: "186D sibe haa medial form",
            eac: "SHAAZ1",
          },
          MCH: {
            conditions: ["default"],
            gb: "186D manchu haa medial form",
            eac: "MHAAZ1",
          },
        },
      },
    },
    fina: {
      "0": {
        written: ["medi", 0],
        locales: {
          SIB: {
            conditions: ["default"],
            eac: "SHAAM1",
          },
          MCH: {
            conditions: ["default"],
            eac: "MHAAM1",
          },
        },
      },
    },
  },
  "MONGOLIAN LETTER SIBE TSA": {
    isol: {
      "0": {
        written: ["init", 0],
        locales: {
          SIB: {
            conditions: ["default"],
            eac: "STSAD1",
          },
          MCH: {
            conditions: ["default"],
            eac: "MTSAD1",
          },
          MCHx: {
            conditions: ["default"],
          },
        },
      },
    },
    init: {
      "0": {
        written: ["Cs"],
        locales: {
          SIB: {
            conditions: ["default"],
            gb: "186E sibe tsa initial form",
            eac: "STSAS1",
          },
          MCH: {
            conditions: ["default"],
            gb: "186E manchu tsa initial form",
            eac: "MTSAS1",
          },
          MCHx: {
            conditions: ["default"],
          },
        },
      },
    },
    medi: {
      "0": {
        written: ["Cs"],
        locales: {
          SIB: {
            conditions: ["default"],
            gb: "186E sibe tsa medial form",
            eac: "STSAZ1",
          },
          MCH: {
            conditions: ["default"],
            gb: "0074 manchu tsa medial form",
            eac: "MTSAZ1",
          },
          MCHx: {
            conditions: ["default"],
          },
        },
      },
    },
    fina: {
      "0": {
        written: ["medi", 0],
        locales: {
          SIB: {
            conditions: ["default"],
            eac: "STSAM1",
          },
          MCH: {
            conditions: ["default"],
            eac: "MTSAM1",
          },
          MCHx: {
            conditions: ["default"],
          },
        },
      },
    },
  },
  "MONGOLIAN LETTER SIBE ZA": {
    isol: {
      "0": {
        written: ["init", 0],
        locales: {
          SIB: {
            conditions: ["default"],
            eac: "SZAD1",
          },
          MCH: {
            conditions: ["default"],
            eac: "MZAD1",
          },
          MCHx: {
            conditions: ["default"],
          },
        },
      },
    },
    init: {
      "0": {
        written: ["Zs"],
        locales: {
          SIB: {
            conditions: ["default"],
            gb: "186F sibe za first initial form",
            eac: "SZAS1",
          },
          MCH: {
            conditions: ["default"],
            gb: "186F manchu za first initial form",
            eac: "MZAS1",
          },
          MCHx: {
            conditions: ["default"],
          },
        },
      },
    },
    medi: {
      "0": {
        written: ["Zs"],
        locales: {
          SIB: {
            conditions: ["default"],
            gb: "186F sibe za first medial form",
            eac: "SZAZ1",
          },
          MCH: {
            conditions: ["default"],
            gb: "0076 manchu za first medial form",
            eac: "MZAZ1",
          },
          MCHx: {
            conditions: ["default"],
          },
        },
      },
    },
    fina: {
      "0": {
        written: ["Zs"],
        locales: {
          SIB: {
            conditions: ["default"],
            eac: "SZAM1",
          },
          MCH: {
            conditions: ["default"],
            eac: "MZAM1",
          },
          MCHx: {
            conditions: ["default"],
          },
        },
      },
    },
  },
  "MONGOLIAN LETTER SIBE RAA": {
    isol: {
      "0": {
        written: ["init", 0],
        locales: {
          SIB: {
            conditions: ["default"],
            eac: "SRAD1",
          },
          MCH: {
            conditions: ["default"],
            eac: "MRAAD1",
          },
        },
      },
    },
    init: {
      "0": {
        written: ["Rr"],
        locales: {
          SIB: {
            conditions: ["default"],
            gb: "1870 sibe raa initial form",
            eac: "SRAS1",
          },
          MCH: {
            conditions: ["default"],
            gb: "1870 manchu raa initial form",
            eac: "MRAAS1",
          },
        },
      },
    },
    medi: {
      "0": {
        written: ["Rr"],
        locales: {
          SIB: {
            conditions: ["default"],
            gb: "1870 sibe raa medial form",
            eac: "SRAZ1",
          },
          MCH: {
            conditions: ["default"],
            gb: "1870 manchu raa medial form",
            eac: "MRAAZ1",
          },
        },
      },
    },
    fina: {
      "0": {
        written: ["medi", 0],
        locales: {
          SIB: {
            conditions: ["default"],
            eac: "SRAM1",
          },
          MCH: {
            conditions: ["default"],
            eac: "MRAAM1",
          },
        },
      },
    },
  },
  "MONGOLIAN LETTER SIBE CHA": {
    isol: {
      "0": {
        written: ["init", 0],
        locales: {
          SIB: {
            conditions: ["default"],
            eac: "SCHAD1",
          },
          MCH: {
            conditions: ["default"],
            eac: "MCHAAD1",
          },
          MCHx: {
            conditions: ["default"],
          },
        },
      },
    },
    init: {
      "0": {
        written: ["Cc"],
        locales: {
          SIB: {
            conditions: ["default"],
            gb: "1871 sibe cha initial form",
            eac: "SCHAS1",
          },
          MCH: {
            conditions: ["default"],
            gb: "1871 manchu cha initial form",
            eac: "MCHAAS1",
          },
          MCHx: {
            conditions: ["default"],
          },
        },
      },
    },
    medi: {
      "0": {
        written: ["Cc"],
        locales: {
          SIB: {
            conditions: ["default"],
            gb: "1871 sibe cha medial form",
            eac: "SCHAZ1",
          },
          MCH: {
            conditions: ["default"],
            gb: "0078 manchu cha medial form",
            eac: "MCHAAZ1",
          },
          MCHx: {
            conditions: ["default"],
          },
        },
      },
    },
    fina: {
      "0": {
        written: ["medi", 0],
        locales: {
          SIB: {
            conditions: ["default"],
            eac: "SCHAM1",
          },
          MCH: {
            conditions: ["default"],
            eac: "MCHAAM1",
          },
          MCHx: {
            written: ["Cc"],
            conditions: ["default"],
          },
        },
      },
    },
  },
  "MONGOLIAN LETTER SIBE ZHA": {
    isol: {
      "0": {
        written: ["init", 0],
        locales: {
          SIB: {
            conditions: ["default"],
            eac: "SZHAD1",
          },
        },
      },
    },
    init: {
      "0": {
        written: ["Ic"],
        locales: {
          SIB: {
            conditions: ["default"],
            gb: "1872 sibe zha initial form",
            eac: "SZHAS1",
          },
        },
      },
    },
    medi: {
      "0": {
        written: ["Ic"],
        locales: {
          SIB: {
            conditions: ["default"],
            gb: "1872 sibe zha medial form",
            eac: "SZHAZ1",
          },
        },
      },
    },
    fina: {
      "0": {
        written: ["medi", 0],
        locales: {
          SIB: {
            conditions: ["default"],
            eac: "SZHAM1",
          },
        },
      },
    },
  },
  "MONGOLIAN LETTER MANCHU I": {
    isol: {
      "1": {
        written: ["I"],
        locales: {
          MCH: {
            conditions: ["particle"],
          },
        },
      },
      "2": {
        written: ["A", "I"],
        locales: {
          MCH: {
            conditions: ["default"],
            gb: "1822 manchu i isolated form",
            eac: "MID1",
          },
          MCHx: {
            conditions: ["default"],
          },
        },
      },
    },
    init: {
      "0": {
        written: ["A", "I"],
        locales: {
          MCH: {
            conditions: ["default"],
            gb: "000A manchu i initial form",
            eac: "MIS1",
          },
          MCHx: {
            conditions: ["default"],
          },
        },
      },
    },
    medi: {
      "2": {
        written: ["I", "I"],
        locales: {
          MCH: {
            conditions: ["devsger"],
            gb: "1873 manchu i third medial form",
            eac: "MIZ2",
          },
          MCHx: {
            conditions: ["devsger"],
          },
        },
      },
      "3": {
        written: ["I"],
        locales: {
          MCH: {
            conditions: ["default"],
            gb: "1835 manchu i first medial form",
            eac: "MIZ1",
          },
          MCHx: {
            conditions: ["default"],
          },
        },
      },
    },
    fina: {
      "1": {
        written: ["I2"],
        locales: {
          MCH: {
            gb: "0062 manchu i second final form",
            eac: "MIM2",
          },
          MCHx: {},
        },
      },
      "2": {
        written: ["Iy"],
        locales: {
          MCH: {
            conditions: ["marked"],
            gb: "0063 manchu i third final form",
            eac: "MIM3",
          },
          MCHx: {
            conditions: ["marked"],
          },
        },
      },
      "3": {
        written: ["I"],
        locales: {
          MCH: {
            conditions: ["default"],
            gb: "000B manchu i first final form",
            eac: "MIM1",
          },
          MCHx: {
            conditions: ["default"],
          },
        },
      },
      "4": {
        written: ["A", "I"],
        locales: {
          MCH: {
            gb: "0303 manchu i fourth final form",
            eac: "MIM4",
          },
          MCHx: {},
        },
      },
    },
  },
  "MONGOLIAN LETTER MANCHU KA": {
    isol: {
      "0": {
        written: ["init", 3],
        locales: {
          MCH: {
            conditions: ["default"],
            eac: "MKAD1",
          },
          MCHx: {
            conditions: ["default"],
          },
        },
      },
      "1": {
        written: ["init", 1],
        locales: {
          MCH: {
            eac: "MKAD2",
          },
          MCHx: {},
        },
      },
      "2": {
        written: ["init", 2],
        locales: {
          MCH: {
            eac: "MKAD3",
          },
          MCHx: {},
        },
      },
    },
    init: {
      "1": {
        written: ["G"],
        locales: {
          MCH: {
            conditions: ["feminine"],
            gb: "1889 manchu ka second initial form",
            eac: "MKAS2",
          },
          MCHx: {
            conditions: ["feminine"],
          },
        },
      },
      "2": {
        written: ["Gx"],
        locales: {
          MCH: {
            gb: "001B manchu ka third initial form",
            eac: "MKAS3",
          },
          MCHx: {},
        },
      },
      "3": {
        written: ["H"],
        locales: {
          MCH: {
            conditions: ["default", "masculine_onset"],
            gb: "182C manchu ka first initial form",
            eac: "MKAS1",
          },
          MCHx: {
            conditions: ["default", "masculine_onset"],
          },
        },
      },
    },
    medi: {
      "1": {
        written: ["Hx"],
        locales: {
          MCH: {
            conditions: ["masculine_devsger"],
            gb: "001C manchu ka second medial form",
            eac: "MKAZ2",
          },
          MCHx: {
            conditions: ["masculine_devsger"],
          },
        },
      },
      "2": {
        written: ["G"],
        locales: {
          MCH: {
            conditions: ["feminine"],
            gb: "001E manchu ka third medial form",
            eac: "MKAZ3",
          },
          MCHx: {
            conditions: ["feminine"],
          },
        },
      },
      "3": {
        written: ["H"],
        locales: {
          MCH: {
            conditions: ["default", "masculine_onset"],
            gb: "0006 manchu ka first medial form",
            eac: "MKAZ1",
          },
          MCHx: {
            conditions: ["default", "masculine_onset"],
          },
        },
      },
      "4": {
        written: ["Gx"],
        locales: {
          MCH: {
            gb: "0079 manchu ka fourth medial form",
            eac: "MKAZ4",
          },
          MCHx: {},
        },
      },
    },
    fina: {
      "1": {
        written: ["G4"],
        locales: {
          MCH: {
            conditions: ["feminine"],
            gb: "007A manchu ka second final form",
            eac: "MKAM2",
          },
          MCHx: {
            conditions: ["feminine"],
          },
        },
      },
      "2": {
        written: ["Gx"],
        locales: {
          MCH: {
            gb: "007B manchu ka third final form",
            eac: "MKAM3",
          },
          MCHx: {},
        },
      },
      "3": {
        written: ["Hx"],
        locales: {
          MCH: {
            conditions: ["default", "masculine_devsger"],
            gb: "1874 manchu ka first final form",
            eac: "MKAM1",
          },
          MCHx: {
            conditions: ["default", "masculine_devsger"],
          },
        },
      },
    },
  },
  "MONGOLIAN LETTER MANCHU RA": {
    isol: {
      "0": {
        written: ["init", 0],
        locales: {
          MCH: {
            conditions: ["default"],
            eac: "MRAD1",
          },
          MCHx: {
            conditions: ["default"],
          },
        },
      },
    },
    init: {
      "0": {
        written: ["R"],
        locales: {
          MCH: {
            conditions: ["default"],
            gb: "1837 manchu ra initial form",
            eac: "MRAS1",
          },
          MCHx: {
            conditions: ["default"],
          },
        },
      },
    },
    medi: {
      "0": {
        written: ["R"],
        locales: {
          MCH: {
            conditions: ["default"],
            gb: "1837 manchu ra medial form",
            eac: "MRAZ1",
          },
          MCHx: {
            conditions: ["default"],
          },
        },
      },
    },
    fina: {
      "0": {
        written: ["R2"],
        locales: {
          MCH: {
            conditions: ["default"],
            gb: "1875 manchu ra final form",
            eac: "MRAM1",
          },
          MCHx: {
            conditions: ["default"],
          },
        },
      },
    },
  },
  "MONGOLIAN LETTER MANCHU FA": {
    isol: {
      "0": {
        written: ["init", 2],
        locales: {
          MCH: {
            conditions: ["default"],
            eac: "MFAD1",
          },
        },
      },
      "1": {
        written: ["init", 1],
        locales: {
          MCH: {
            conditions: ["default"],
            eac: "MFAD2",
          },
        },
      },
    },
    init: {
      "1": {
        written: ["W"],
        locales: {
          MCH: {
            conditions: ["marked"],
            gb: "1838 manchu fa second initial form",
            eac: "MFAS2",
          },
        },
      },
      "2": {
        written: ["V"],
        locales: {
          MCH: {
            conditions: ["default"],
            gb: "186B manchu fa first initial form",
            eac: "MFAS1",
          },
        },
      },
    },
    medi: {
      "1": {
        written: ["W"],
        locales: {
          MCH: {
            conditions: ["marked"],
            gb: "1838 manchu fa second medial form",
            eac: "MFAZ2",
          },
        },
      },
      "2": {
        written: ["V"],
        locales: {
          MCH: {
            conditions: ["default"],
            gb: "1876 manchu fa first medial form",
            eac: "MFAZ1",
          },
        },
      },
    },
    fina: {
      "0": {
        written: ["medi", 2],
        locales: {
          MCH: {
            conditions: ["default"],
            eac: "MFAM1",
          },
        },
      },
    },
  },
  "MONGOLIAN LETTER MANCHU ZHA": {
    isol: {
      "0": {
        written: ["init", 0],
        locales: {
          MCH: {
            conditions: ["default"],
            eac: "MZHAD1",
          },
          MCHx: {
            conditions: ["default"],
          },
        },
      },
    },
    init: {
      "0": {
        written: ["Ic"],
        locales: {
          MCH: {
            conditions: ["default"],
            gb: "1877 manchu zha initial form",
            eac: "MZHAS1",
          },
          MCHx: {
            conditions: ["default"],
          },
        },
      },
    },
    medi: {
      "0": {
        written: ["Jc"],
        locales: {
          MCH: {
            conditions: ["default"],
            gb: "007C manchu zha medial form",
            eac: "MZHAZ1",
          },
          MCHx: {
            conditions: ["default"],
          },
        },
      },
    },
    fina: {
      "0": {
        written: ["medi", 0],
        locales: {
          MCH: {
            conditions: ["default"],
            eac: "MZHAM1",
          },
          MCHx: {
            written: ["Jc"],
            conditions: ["default"],
          },
        },
      },
    },
  },
  "MONGOLIAN LETTER ALI GALI A": {
    isol: {
      "0": {
        written: ["A", "Aw"],
        locales: {
          MNGx: {
            written: ["fina", 1],
            conditions: ["default"],
          },
          MCHx: {
            conditions: ["default"],
          },
        },
      },
    },
    init: {
      "0": {
        written: ["A", "A"],
        locales: {
          MNGx: {
            written: ["fina", 1],
            conditions: ["default"],
          },
          MCHx: {
            conditions: ["default"],
          },
        },
      },
    },
    medi: {
      "0": {
        written: ["A"],
        locales: {
          MNGx: {
            written: ["fina", 1],
            conditions: ["default"],
          },
          MCHx: {
            conditions: ["default"],
          },
        },
      },
    },
    fina: {
      "0": {
        written: ["Aw"],
        locales: {
          MCHx: {
            conditions: ["default"],
          },
        },
      },
      "1": {
        written: ["A2"],
        locales: {
          MNGx: {
            conditions: ["default", "post_wa"],
          },
        },
      },
    },
  },
  "MONGOLIAN LETTER ALI GALI I": {
    isol: {
      "0": {
        written: ["A", "I4"],
        locales: {
          MNGx: {
            conditions: ["default"],
          },
        },
      },
    },
    init: {
      "0": {
        written: ["A", "I"],
        locales: {
          MNGx: {
            conditions: ["default"],
          },
        },
      },
    },
    medi: {
      "0": {
        written: ["I"],
        locales: {
          MNGx: {
            conditions: ["default"],
          },
        },
      },
    },
    fina: {
      "0": {
        written: ["I4"],
        locales: {
          MNGx: {
            conditions: ["default"],
          },
        },
      },
    },
  },
  "MONGOLIAN LETTER ALI GALI KA": {
    isol: {
      "0": {
        written: ["init", 0],
        locales: {
          MNGx: {
            conditions: ["default"],
          },
          TODx: {
            conditions: ["default"],
          },
        },
      },
    },
    init: {
      "0": {
        written: ["G"],
        locales: {
          MNGx: {
            conditions: ["default"],
          },
          TODx: {
            conditions: ["default"],
          },
        },
      },
    },
    medi: {
      "0": {
        written: ["G"],
        locales: {
          MNGx: {
            conditions: ["default"],
          },
          TODx: {
            conditions: ["default"],
          },
        },
      },
    },
    fina: {
      "0": {
        written: ["G", "Vi"],
        locales: {
          MNGx: {
            conditions: ["default"],
          },
          TODx: {
            written: ["medi", 0],
            conditions: ["default"],
          },
        },
      },
    },
  },
  "MONGOLIAN LETTER ALI GALI NGA": {
    isol: {
      "0": {
        written: ["init", 0],
        locales: {
          MNGx: {
            conditions: ["default"],
          },
          TODx: {
            conditions: ["default"],
          },
        },
      },
    },
    init: {
      "0": {
        written: ["N", "G"],
        locales: {
          MNGx: {
            conditions: ["default"],
          },
          TODx: {
            conditions: ["default"],
          },
        },
      },
    },
    medi: {
      "0": {
        written: ["N", "G"],
        locales: {
          MNGx: {
            conditions: ["default"],
          },
          TODx: {
            conditions: ["default"],
          },
        },
      },
    },
    fina: {
      "0": {
        written: ["N", "G4"],
        locales: {
          MNGx: {
            conditions: ["default"],
          },
          TODx: {
            written: ["medi", 0],
            conditions: ["default"],
          },
        },
      },
    },
  },
  "MONGOLIAN LETTER ALI GALI CA": {
    isol: {
      "0": {
        written: ["init", 0],
        locales: {
          MNGx: {
            conditions: ["default"],
          },
        },
      },
    },
    init: {
      "0": {
        written: ["Zc"],
        locales: {
          MNGx: {
            conditions: ["default"],
          },
        },
      },
    },
    medi: {
      "0": {
        written: ["Zc"],
        locales: {
          MNGx: {
            conditions: ["default"],
          },
        },
      },
    },
    fina: {
      "0": {
        written: ["Zc"],
        locales: {
          MNGx: {
            conditions: ["default"],
          },
        },
      },
    },
  },
  "MONGOLIAN LETTER ALI GALI TTA": {
    isol: {
      "0": {
        written: ["init", 0],
        locales: {
          MNGx: {
            conditions: ["default"],
          },
          TODx: {
            conditions: ["default"],
          },
        },
      },
    },
    init: {
      "0": {
        written: ["Zr"],
        locales: {
          MNGx: {
            conditions: ["default"],
          },
          TODx: {
            conditions: ["default"],
          },
        },
      },
    },
    medi: {
      "0": {
        written: ["Zr"],
        locales: {
          MNGx: {
            conditions: ["default"],
          },
          TODx: {
            conditions: ["default"],
          },
        },
      },
    },
    fina: {
      "0": {
        written: ["Zr"],
        locales: {
          MNGx: {
            conditions: ["default"],
          },
          TODx: {
            written: ["medi", 0],
            conditions: ["default"],
          },
        },
      },
    },
  },
  "MONGOLIAN LETTER ALI GALI TTHA": {
    isol: {
      "0": {
        written: ["init", 0],
        locales: {
          MNGx: {
            conditions: ["default"],
          },
          TODx: {
            conditions: ["default"],
          },
        },
      },
    },
    init: {
      "0": {
        written: ["Cr2"],
        locales: {
          MNGx: {
            conditions: ["default"],
          },
          TODx: {
            conditions: ["default"],
          },
        },
      },
    },
    medi: {
      "0": {
        written: ["Cr2"],
        locales: {
          MNGx: {
            conditions: ["default"],
          },
          TODx: {
            conditions: ["default"],
          },
        },
      },
    },
    fina: {
      "0": {
        written: ["medi", 0],
        locales: {
          MNGx: {
            conditions: ["default"],
          },
          TODx: {
            conditions: ["default"],
          },
        },
      },
    },
  },
  "MONGOLIAN LETTER ALI GALI DDA": {
    isol: {
      "0": {
        written: ["init", 0],
        locales: {
          MNGx: {
            conditions: ["default"],
          },
        },
      },
      "1": {
        written: ["init", 1],
        locales: {
          TODx: {
            conditions: ["default"],
          },
        },
      },
    },
    init: {
      "0": {
        written: ["Ds"],
        locales: {
          MNGx: {
            conditions: ["default"],
          },
        },
      },
      "1": {
        written: ["Ds2"],
        locales: {
          TODx: {
            conditions: ["default"],
          },
        },
      },
    },
    medi: {
      "0": {
        written: ["Ds"],
        locales: {
          MNGx: {
            conditions: ["default"],
          },
        },
      },
      "1": {
        written: ["Ds2"],
        locales: {
          TODx: {
            conditions: ["default"],
          },
        },
      },
    },
    fina: {
      "0": {
        written: ["Ds"],
        locales: {
          MNGx: {
            conditions: ["default"],
          },
          TODx: {
            conditions: ["default"],
          },
        },
      },
    },
  },
  "MONGOLIAN LETTER ALI GALI NNA": {
    isol: {
      "0": {
        written: ["init", 0],
        locales: {
          MNGx: {
            conditions: ["default"],
          },
          TODx: {
            conditions: ["default"],
          },
          MCHx: {
            conditions: ["default"],
          },
        },
      },
    },
    init: {
      "0": {
        written: ["Wn"],
        locales: {
          MNGx: {
            conditions: ["default"],
          },
          TODx: {
            conditions: ["default"],
          },
          MCHx: {
            conditions: ["default"],
          },
        },
      },
    },
    medi: {
      "0": {
        written: ["Wn"],
        locales: {
          MNGx: {
            conditions: ["default"],
          },
          TODx: {
            conditions: ["default"],
          },
          MCHx: {
            conditions: ["default"],
          },
        },
      },
    },
    fina: {
      "0": {
        written: ["Wn"],
        locales: {
          MNGx: {
            conditions: ["default"],
          },
          TODx: {
            written: ["medi", 0],
            conditions: ["default"],
          },
          MCHx: {
            conditions: ["default"],
          },
        },
      },
    },
  },
  "MONGOLIAN LETTER ALI GALI TA": {
    isol: {
      "0": {
        written: ["init", 0],
        locales: {
          MNGx: {
            conditions: ["default"],
          },
          TODx: {
            conditions: ["default"],
          },
        },
      },
    },
    init: {
      "0": {
        written: ["Dv"],
        locales: {
          MNGx: {
            conditions: ["default"],
          },
          TODx: {
            conditions: ["default"],
          },
        },
      },
    },
    medi: {
      "0": {
        written: ["Dv"],
        locales: {
          MNGx: {
            conditions: ["default"],
          },
          TODx: {
            conditions: ["default"],
          },
        },
      },
    },
    fina: {
      "0": {
        written: ["Dv"],
        locales: {
          MNGx: {
            conditions: ["default"],
          },
          TODx: {
            conditions: ["default"],
          },
        },
      },
    },
  },
  "MONGOLIAN LETTER ALI GALI DA": {
    isol: {
      "0": {
        written: ["init", 0],
        locales: {
          MNGx: {
            conditions: ["default"],
          },
        },
      },
    },
    init: {
      "0": {
        written: ["Dq"],
        locales: {
          MNGx: {
            conditions: ["default"],
          },
        },
      },
    },
    medi: {
      "0": {
        written: ["Dq"],
        locales: {
          MNGx: {
            conditions: ["default"],
          },
        },
      },
    },
    fina: {
      "0": {
        written: ["Dq"],
        locales: {
          MNGx: {
            conditions: ["default"],
          },
        },
      },
    },
  },
  "MONGOLIAN LETTER ALI GALI PA": {
    isol: {
      "0": {
        written: ["init", 0],
        locales: {
          MNGx: {
            conditions: ["default"],
          },
          MCHx: {
            conditions: ["default"],
          },
        },
      },
      "1": {
        written: ["init", 1],
        locales: {
          TODx: {
            conditions: ["default"],
          },
        },
      },
    },
    init: {
      "0": {
        written: ["Bg"],
        locales: {
          MNGx: {
            conditions: ["default"],
          },
          MCHx: {
            conditions: ["default"],
          },
        },
      },
      "1": {
        written: ["Bh"],
        locales: {
          TODx: {
            conditions: ["default"],
          },
        },
      },
    },
    medi: {
      "0": {
        written: ["Bg"],
        locales: {
          MNGx: {
            conditions: ["default"],
          },
          MCHx: {
            conditions: ["default"],
          },
        },
      },
      "1": {
        written: ["Bh"],
        locales: {
          TODx: {
            conditions: ["default"],
          },
        },
      },
    },
    fina: {
      "0": {
        written: ["Bg"],
        locales: {
          MNGx: {
            conditions: ["default"],
          },
          TODx: {
            written: ["medi", 1],
            conditions: ["default"],
          },
          MCHx: {
            conditions: ["default"],
          },
        },
      },
    },
  },
  "MONGOLIAN LETTER ALI GALI PHA": {
    isol: {
      "0": {
        written: ["init", 0],
        locales: {
          MNGx: {
            conditions: ["default"],
          },
        },
      },
    },
    init: {
      "0": {
        written: ["Pg"],
        locales: {
          MNGx: {
            conditions: ["default"],
          },
        },
      },
    },
    medi: {
      "0": {
        written: ["Pg"],
        locales: {
          MNGx: {
            conditions: ["default"],
          },
        },
      },
    },
    fina: {
      "0": {
        written: ["Pg"],
        locales: {
          MNGx: {
            conditions: ["default"],
          },
        },
      },
    },
  },
  "MONGOLIAN LETTER ALI GALI SSA": {
    isol: {
      "0": {
        written: ["init", 0],
        locales: {
          MNGx: {
            conditions: ["default"],
          },
          TODx: {
            conditions: ["default"],
          },
        },
      },
    },
    init: {
      "0": {
        written: ["Sx"],
        locales: {
          MNGx: {
            conditions: ["default"],
          },
          TODx: {
            conditions: ["default"],
          },
        },
      },
    },
    medi: {
      "0": {
        written: ["Sx"],
        locales: {
          MNGx: {
            conditions: ["default"],
          },
          TODx: {
            conditions: ["default"],
          },
        },
      },
    },
    fina: {
      "0": {
        written: ["Sx"],
        locales: {
          MNGx: {
            conditions: ["default"],
          },
          TODx: {
            written: ["medi", 0],
            conditions: ["default"],
          },
        },
      },
    },
  },
  "MONGOLIAN LETTER ALI GALI ZHA": {
    isol: {
      "0": {
        written: ["init", 0],
        locales: {
          MNGx: {
            conditions: ["default"],
          },
        },
      },
    },
    init: {
      "0": {
        written: ["Rh2"],
        locales: {
          MNGx: {
            conditions: ["default"],
          },
        },
      },
    },
    medi: {
      "0": {
        written: ["Rh2"],
        locales: {
          MNGx: {
            conditions: ["default"],
          },
        },
      },
    },
    fina: {
      "0": {
        written: ["Rh2"],
        locales: {
          MNGx: {
            conditions: ["default"],
          },
        },
      },
    },
  },
  "MONGOLIAN LETTER ALI GALI ZA": {
    isol: {
      "0": {
        written: ["init", 0],
        locales: {
          MNGx: {
            conditions: ["default"],
          },
          TODx: {
            conditions: ["default"],
          },
        },
      },
    },
    init: {
      "0": {
        written: ["Zz"],
        locales: {
          MNGx: {
            conditions: ["default"],
          },
          TODx: {
            conditions: ["default"],
          },
        },
      },
    },
    medi: {
      "0": {
        written: ["Zz"],
        locales: {
          MNGx: {
            conditions: ["default"],
          },
          TODx: {
            conditions: ["default"],
          },
        },
      },
    },
    fina: {
      "0": {
        written: ["Zz"],
        locales: {
          MNGx: {
            conditions: ["default"],
          },
          TODx: {
            written: ["medi", 0],
            conditions: ["default"],
          },
        },
      },
    },
  },
  "MONGOLIAN LETTER ALI GALI AH": {
    isol: {
      "0": {
        written: ["init", 0],
        locales: {
          MNGx: {
            conditions: ["default"],
          },
          TODx: {
            conditions: ["default"],
          },
        },
      },
    },
    init: {
      "0": {
        written: ["Q"],
        locales: {
          MNGx: {
            conditions: ["default"],
          },
          TODx: {
            conditions: ["default"],
          },
        },
      },
    },
    medi: {
      "0": {
        written: ["Q"],
        locales: {
          MNGx: {
            conditions: ["default"],
          },
          TODx: {
            conditions: ["default"],
          },
        },
      },
    },
    fina: {
      "0": {
        written: ["medi", 0],
        locales: {
          MNGx: {
            conditions: ["default"],
          },
          TODx: {
            conditions: ["default"],
          },
        },
      },
    },
  },
  "MONGOLIAN LETTER TODO ALI GALI ZHA": {
    isol: {
      "0": {
        written: ["init", 0],
        locales: {
          TODx: {
            conditions: ["default"],
          },
        },
      },
    },
    init: {
      "0": {
        written: ["Rz"],
        locales: {
          TODx: {
            conditions: ["default"],
          },
        },
      },
    },
    medi: {
      "0": {
        written: ["Rz"],
        locales: {
          TODx: {
            conditions: ["default"],
          },
        },
      },
    },
    fina: {
      "0": {
        written: ["medi", 0],
        locales: {
          TODx: {
            conditions: ["default"],
          },
        },
      },
    },
  },
  "MONGOLIAN LETTER MANCHU ALI GALI GHA": {
    isol: {
      "0": {
        written: ["init", 0],
        locales: {
          MCHx: {
            conditions: ["default"],
          },
        },
      },
    },
    init: {
      "0": {
        written: ["Hy"],
        locales: {
          MCHx: {
            conditions: ["default"],
          },
        },
      },
    },
    medi: {
      "0": {
        written: ["Hy"],
        locales: {
          MCHx: {
            conditions: ["default"],
          },
        },
      },
      "1": {
        written: ["Hy2"],
        locales: {
          MCHx: {},
        },
      },
    },
    fina: {
      "0": {
        written: ["medi", 0],
        locales: {
          MCHx: {
            conditions: ["default"],
          },
        },
      },
    },
  },
  "MONGOLIAN LETTER MANCHU ALI GALI NGA": {
    isol: {
      "0": {
        written: ["init", 0],
        locales: {
          MCHx: {
            conditions: ["default"],
          },
        },
      },
    },
    init: {
      "0": {
        written: ["Nb"],
        locales: {
          MCHx: {
            conditions: ["default"],
          },
        },
      },
    },
    medi: {
      "0": {
        written: ["Nb"],
        locales: {
          MCHx: {
            conditions: ["default"],
          },
        },
      },
    },
    fina: {
      "0": {
        written: ["medi", 0],
        locales: {
          MCHx: {
            conditions: ["default"],
          },
        },
      },
    },
  },
  "MONGOLIAN LETTER MANCHU ALI GALI CA": {
    isol: {
      "0": {
        written: ["init", 0],
        locales: {
          MCHx: {
            conditions: ["default"],
          },
        },
      },
    },
    init: {
      "0": {
        written: ["Ct"],
        locales: {
          MCHx: {
            conditions: ["default"],
          },
        },
      },
    },
    medi: {
      "0": {
        written: ["Ct"],
        locales: {
          MCHx: {
            conditions: ["default"],
          },
        },
      },
    },
    fina: {
      "0": {
        written: ["medi", 0],
        locales: {
          MCHx: {
            conditions: ["default"],
          },
        },
      },
    },
  },
  "MONGOLIAN LETTER MANCHU ALI GALI JHA": {
    isol: {
      "0": {
        written: ["init", 0],
        locales: {
          MCHx: {
            conditions: ["default"],
          },
        },
      },
    },
    init: {
      "0": {
        written: ["Zt"],
        locales: {
          MCHx: {
            conditions: ["default"],
          },
        },
      },
    },
    medi: {
      "0": {
        written: ["Zt"],
        locales: {
          MCHx: {
            conditions: ["default"],
          },
        },
      },
    },
    fina: {
      "0": {
        written: ["medi", 0],
        locales: {
          MCHx: {
            conditions: ["default"],
          },
        },
      },
    },
  },
  "MONGOLIAN LETTER MANCHU ALI GALI TTA": {
    isol: {
      "0": {
        written: ["init", 0],
        locales: {
          MCHx: {
            conditions: ["default"],
          },
        },
      },
    },
    init: {
      "0": {
        written: ["It"],
        locales: {
          MCHx: {
            conditions: ["default"],
          },
        },
      },
    },
    medi: {
      "0": {
        written: ["Jt"],
        locales: {
          MCHx: {
            conditions: ["default"],
          },
        },
      },
    },
    fina: {
      "0": {
        written: ["Jt"],
        locales: {
          MCHx: {
            conditions: ["default"],
          },
        },
      },
    },
  },
  "MONGOLIAN LETTER MANCHU ALI GALI DDHA": {
    isol: {
      "0": {
        written: ["init", 0],
        locales: {
          MCHx: {
            conditions: ["default"],
          },
        },
      },
    },
    init: {
      "0": {
        written: ["Ih"],
        locales: {
          MCHx: {
            conditions: ["default"],
          },
        },
      },
    },
    medi: {
      "0": {
        written: ["Jh"],
        locales: {
          MCHx: {
            conditions: ["default"],
          },
        },
      },
    },
    fina: {
      "0": {
        written: ["Jh"],
        locales: {
          MCHx: {
            conditions: ["default"],
          },
        },
      },
    },
  },
  "MONGOLIAN LETTER MANCHU ALI GALI TA": {
    isol: {
      "0": {
        written: ["init", 2],
        locales: {
          MCHx: {
            conditions: ["default"],
          },
        },
      },
      "1": {
        written: ["init", 1],
        locales: {
          MCHx: {},
        },
      },
    },
    init: {
      "1": {
        written: ["Dy"],
        locales: {
          MCHx: {
            conditions: ["feminine"],
          },
        },
      },
      "2": {
        written: ["Dr"],
        locales: {
          MCHx: {
            conditions: ["default", "masculine_onset"],
          },
        },
      },
    },
    medi: {
      "1": {
        written: ["Dy"],
        locales: {
          MCHx: {
            conditions: ["feminine"],
          },
        },
      },
      "2": {
        written: ["Dr"],
        locales: {
          MCHx: {
            conditions: ["default", "masculine_onset"],
          },
        },
      },
    },
    fina: {
      "0": {
        written: ["Dr"],
        locales: {
          MCHx: {
            conditions: ["default"],
          },
        },
      },
    },
  },
  "MONGOLIAN LETTER MANCHU ALI GALI DHA": {
    isol: {
      "0": {
        written: ["init", 2],
        locales: {
          MCHx: {
            conditions: ["default"],
          },
        },
      },
      "1": {
        written: ["init", 1],
        locales: {
          MCHx: {},
        },
      },
    },
    init: {
      "1": {
        written: ["Ts"],
        locales: {
          MCHx: {
            conditions: ["feminine"],
          },
        },
      },
      "2": {
        written: ["Tx"],
        locales: {
          MCHx: {
            conditions: ["default", "masculine_onset"],
          },
        },
      },
    },
    medi: {
      "1": {
        written: ["Ds"],
        locales: {
          MCHx: {
            conditions: ["feminine"],
          },
        },
      },
      "2": {
        written: ["Dx"],
        locales: {
          MCHx: {
            conditions: ["default", "masculine_onset"],
          },
        },
      },
    },
    fina: {
      "0": {
        written: ["medi", 2],
        locales: {
          MCHx: {
            conditions: ["default"],
          },
        },
      },
    },
  },
  "MONGOLIAN LETTER MANCHU ALI GALI SSA": {
    isol: {
      "0": {
        written: ["init", 0],
        locales: {
          MCHx: {
            conditions: ["default"],
          },
        },
      },
    },
    init: {
      "0": {
        written: ["Sx"],
        locales: {
          MCHx: {
            conditions: ["default"],
          },
        },
      },
    },
    medi: {
      "0": {
        written: ["Sx"],
        locales: {
          MCHx: {
            conditions: ["default"],
          },
        },
      },
    },
    fina: {
      "0": {
        written: ["Sx"],
        locales: {
          MCHx: {
            conditions: ["default"],
          },
        },
      },
    },
  },
  "MONGOLIAN LETTER MANCHU ALI GALI CYA": {
    isol: {
      "0": {
        written: ["init", 0],
        locales: {
          MCHx: {
            conditions: ["default"],
          },
        },
      },
    },
    init: {
      "0": {
        written: ["Iq"],
        locales: {
          MCHx: {
            conditions: ["default"],
          },
        },
      },
    },
    medi: {
      "0": {
        written: ["Jq"],
        locales: {
          MCHx: {
            conditions: ["default"],
          },
        },
      },
    },
    fina: {
      "0": {
        written: ["Jq"],
        locales: {
          MCHx: {
            conditions: ["default"],
          },
        },
      },
    },
  },
  "MONGOLIAN LETTER MANCHU ALI GALI ZHA": {
    isol: {
      "0": {
        written: ["init", 0],
        locales: {
          MCHx: {
            conditions: ["default"],
          },
        },
      },
    },
    init: {
      "0": {
        written: ["St"],
        locales: {
          MCHx: {
            conditions: ["default"],
          },
        },
      },
    },
    medi: {
      "0": {
        written: ["St"],
        locales: {
          MCHx: {
            conditions: ["default"],
          },
        },
      },
    },
    fina: {
      "0": {
        written: ["St"],
        locales: {
          MCHx: {
            conditions: ["default"],
          },
        },
      },
    },
  },
  "MONGOLIAN LETTER MANCHU ALI GALI ZA": {
    isol: {
      "0": {
        written: ["init", 0],
        locales: {
          MCHx: {
            conditions: ["default"],
          },
        },
      },
    },
    init: {
      "0": {
        written: ["Sc"],
        locales: {
          MCHx: {
            conditions: ["default"],
          },
        },
      },
    },
    medi: {
      "0": {
        written: ["Sc"],
        locales: {
          MCHx: {
            conditions: ["default"],
          },
        },
      },
    },
    fina: {
      "0": {
        written: ["Sc"],
        locales: {
          MCHx: {
            conditions: ["default"],
          },
        },
      },
    },
  },
  "MONGOLIAN LETTER ALI GALI HALF U": {
    isol: {
      "0": {
        written: ["medi", 0],
        locales: {
          MNGx: {
            conditions: ["default"],
          },
          TODx: {
            written: ["fina", 0],
            conditions: ["default"],
          },
        },
      },
    },
    init: {
      "0": {
        written: ["medi", 0],
        locales: {
          MNGx: {
            conditions: ["default"],
          },
          TODx: {
            written: ["fina", 0],
            conditions: ["default"],
          },
        },
      },
    },
    medi: {
      "0": {
        written: ["Wp"],
        locales: {
          MNGx: {
            conditions: ["default"],
          },
          TODx: {
            written: ["fina", 0],
            conditions: ["default"],
          },
        },
      },
    },
    fina: {
      "0": {
        written: ["Wp"],
        locales: {
          MNGx: {
            written: ["medi", 0],
            conditions: ["default"],
          },
          TODx: {
            conditions: ["default"],
          },
        },
      },
    },
  },
  "MONGOLIAN LETTER ALI GALI HALF YA": {
    isol: {
      "0": {
        written: ["medi", 0],
        locales: {
          TODx: {
            conditions: ["default"],
          },
        },
      },
    },
    init: {
      "0": {
        written: ["medi", 0],
        locales: {
          TODx: {
            conditions: ["default"],
          },
        },
      },
    },
    medi: {
      "0": {
        written: ["Yp"],
        locales: {
          TODx: {
            conditions: ["default"],
          },
        },
      },
    },
    fina: {
      "0": {
        written: ["Yp"],
        locales: {
          TODx: {
            conditions: ["default"],
          },
        },
      },
      "1": {
        written: ["Ir"],
        locales: {
          TODx: {},
        },
      },
    },
  },
  "MONGOLIAN LETTER MANCHU ALI GALI BHA": {
    isol: {
      "0": {
        written: ["init", 0],
        locales: {
          MCHx: {
            conditions: ["default"],
          },
        },
      },
    },
    init: {
      "0": {
        written: ["Bc"],
        locales: {
          MCHx: {
            conditions: ["default"],
          },
        },
      },
    },
    medi: {
      "0": {
        written: ["Bc"],
        locales: {
          MCHx: {
            conditions: ["default"],
          },
        },
      },
    },
    fina: {
      "0": {
        written: ["medi", 0],
        locales: {
          MCHx: {
            conditions: ["default"],
          },
        },
      },
    },
  },
  "MONGOLIAN LETTER MANCHU ALI GALI LHA": {
    isol: {
      "0": {
        written: ["init", 0],
        locales: {
          MCHx: {
            conditions: ["default"],
          },
        },
      },
    },
    init: {
      "0": {
        written: ["Lc"],
        locales: {
          MCHx: {
            conditions: ["default"],
          },
        },
      },
    },
    medi: {
      "0": {
        written: ["Lc"],
        locales: {
          MCHx: {
            conditions: ["default"],
          },
        },
      },
    },
    fina: {
      "0": {
        written: ["medi", 0],
        locales: {
          MCHx: {
            conditions: ["default"],
          },
        },
      },
    },
  },
};

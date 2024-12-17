// @ts-ignore
import Names from "@unicode/unicode-16.0.0/Names";

import type { JoiningPosition } from ".";
import type { WrittenUnitID } from "./writtenUnits";

type Letter = {
  cp: number;
  variants: Record<JoiningPosition, LetterVariant[]>;
};
type LetterVariant = {
  writtenUnits: WrittenUnitID[] | `${WrittenUnitID}.${JoiningPosition}`[];
  fvs?: 1 | 2 | 3 | 4;
  representativeGlyph?: true;
};
export type LetterID = keyof typeof letters;

export const letters = {
  a: {
    cp: 0x1820,
    variants: {
      isol: [
        {
          writtenUnits: ["A", "A"],
          fvs: 3,
          representativeGlyph: true,
        },
        {
          writtenUnits: ["A"],
          fvs: 1,
        },
        {
          writtenUnits: ["Aa"],
          fvs: 2,
        },
      ],
      init: [
        {
          writtenUnits: ["A", "A"],
          fvs: 2,
        },
        {
          writtenUnits: ["A"],
          fvs: 1,
        },
      ],
      medi: [
        {
          writtenUnits: ["A"],
        },
        {
          writtenUnits: ["A", "A"],
          fvs: 1,
        },
      ],
      fina: [
        {
          writtenUnits: ["A"],
          fvs: 2,
        },
        {
          writtenUnits: ["Aa"],
          fvs: 1,
        },
      ],
    },
  },
  e: {
    cp: 0x0000,
    variants: {
      isol: [],
      init: [],
      medi: [],
      fina: [],
    },
  },
  i: {
    cp: 0x0000,
    variants: {
      isol: [],
      init: [],
      medi: [],
      fina: [],
    },
  },
  o: {
    cp: 0x0000,
    variants: {
      isol: [],
      init: [],
      medi: [],
      fina: [],
    },
  },
  u: {
    cp: 0x0000,
    variants: {
      isol: [],
      init: [],
      medi: [],
      fina: [],
    },
  },
  oe: {
    cp: 0x0000,
    variants: {
      isol: [],
      init: [],
      medi: [],
      fina: [],
    },
  },
  ue: {
    cp: 0x0000,
    variants: {
      isol: [],
      init: [],
      medi: [],
      fina: [],
    },
  },
  ee: {
    cp: 0x0000,
    variants: {
      isol: [],
      init: [],
      medi: [],
      fina: [],
    },
  },
  n: {
    cp: 0x1828,
    variants: {
      isol: [
        {
          writtenUnits: ["N.init"],
        },
        {
          writtenUnits: ["A.init"],
          fvs: 1,
        },
      ],
      init: [],
      medi: [],
      fina: [],
    },
  },
  ng: {
    cp: 0x0000,
    variants: {
      isol: [],
      init: [],
      medi: [],
      fina: [],
    },
  },
  b: {
    cp: 0x0000,
    variants: {
      isol: [],
      init: [],
      medi: [],
      fina: [],
    },
  },
  p: {
    cp: 0x0000,
    variants: {
      isol: [],
      init: [],
      medi: [],
      fina: [],
    },
  },
  h: {
    cp: 0x0000,
    variants: {
      isol: [],
      init: [],
      medi: [],
      fina: [],
    },
  },
  g: {
    cp: 0x0000,
    variants: {
      isol: [],
      init: [],
      medi: [],
      fina: [],
    },
  },
  m: {
    cp: 0x0000,
    variants: {
      isol: [],
      init: [],
      medi: [],
      fina: [],
    },
  },
  l: {
    cp: 0x0000,
    variants: {
      isol: [],
      init: [],
      medi: [],
      fina: [],
    },
  },
  s: {
    cp: 0x0000,
    variants: {
      isol: [],
      init: [],
      medi: [],
      fina: [],
    },
  },
  sh: {
    cp: 0x0000,
    variants: {
      isol: [],
      init: [],
      medi: [],
      fina: [],
    },
  },
  t: {
    cp: 0x0000,
    variants: {
      isol: [],
      init: [],
      medi: [],
      fina: [],
    },
  },
  d: {
    cp: 0x0000,
    variants: {
      isol: [],
      init: [],
      medi: [],
      fina: [],
    },
  },
  ch: {
    cp: 0x0000,
    variants: {
      isol: [],
      init: [],
      medi: [],
      fina: [],
    },
  },
  j: {
    cp: 0x0000,
    variants: {
      isol: [],
      init: [],
      medi: [],
      fina: [],
    },
  },
  y: {
    cp: 0x0000,
    variants: {
      isol: [],
      init: [],
      medi: [],
      fina: [],
    },
  },
  r: {
    cp: 0x0000,
    variants: {
      isol: [],
      init: [],
      medi: [],
      fina: [],
    },
  },
  w: {
    cp: 0x0000,
    variants: {
      isol: [],
      init: [],
      medi: [],
      fina: [],
    },
  },
  f: {
    cp: 0x0000,
    variants: {
      isol: [],
      init: [],
      medi: [],
      fina: [],
    },
  },
  k2: {
    cp: 0x0000,
    variants: {
      isol: [],
      init: [],
      medi: [],
      fina: [],
    },
  },
  k: {
    cp: 0x0000,
    variants: {
      isol: [],
      init: [],
      medi: [],
      fina: [],
    },
  },
  c: {
    cp: 0x0000,
    variants: {
      isol: [],
      init: [],
      medi: [],
      fina: [],
    },
  },
  z: {
    cp: 0x0000,
    variants: {
      isol: [],
      init: [],
      medi: [],
      fina: [],
    },
  },
  hh: {
    cp: 0x0000,
    variants: {
      isol: [],
      init: [],
      medi: [],
      fina: [],
    },
  },
  rh: {
    cp: 0x0000,
    variants: {
      isol: [],
      init: [],
      medi: [],
      fina: [],
    },
  },
  lh: {
    cp: 0x0000,
    variants: {
      isol: [],
      init: [],
      medi: [],
      fina: [],
    },
  },
  zr: {
    cp: 0x0000,
    variants: {
      isol: [],
      init: [],
      medi: [],
      fina: [],
    },
  },
  cr: {
    cp: 0x0000,
    variants: {
      isol: [],
      init: [],
      medi: [],
      fina: [],
    },
  },
} satisfies Record<string, Letter>;

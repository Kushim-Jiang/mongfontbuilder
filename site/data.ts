export type JoiningPosition = (typeof joiningPositions)[number];
export const joiningPositions = ["isol", "init", "medi", "fina"] as const;

export type WrittenUnitID = keyof typeof writtenUnits;
type WrittenUnit = Partial<Record<JoiningPosition, WrittenUnitVariant>>;
export type WrittenUnitVariant = {
  archaic?: true;
};

export const writtenUnits = {
  A: {
    isol: {},
    init: {},
    medi: {},
    fina: {},
  },
  Aa: {
    isol: {},
    fina: {},
  },
  I: {
    isol: {},
    init: {},
    medi: {},
    fina: {},
  },
  Ix: {
    isol: {
      archaic: true,
    },
  },
  N: {
    init: {},
    medi: {},
    fina: {},
  },
} satisfies Record<string, WrittenUnit>;

type LetterID = keyof typeof letters;
type Letter = {
  cp: string;
  variants: Record<JoiningPosition, LetterVariant[]>;
};
type LetterVariant = {
  writtenUnits: WrittenUnitID[] | `${WrittenUnitID}.${JoiningPosition}`[];
  fvs?: 1 | 2 | 3 | 4;
  representativeGlyph?: true;
};

export const letters = {
  a: {
    cp: "MONGOLIAN LETTER A",
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
      init: [],
      medi: [],
      fina: [],
    },
  },
  e: {},
  i: {},
  o: {},
  u: {},
  oe: {},
  ue: {},
  ee: {},
  n: {
    cp: "MONGOLIAN LETTER NA",
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
    },
  },
  ng: {},
  b: {},
  p: {},
  h: {},
  g: {},
  m: {},
  l: {},
  s: {},
  sh: {},
  t: {},
  d: {},
  ch: {},
  j: {},
  y: {},
  r: {},
  w: {},
  f: {},
  k2: {},
  k: {},
  c: {},
  z: {},
  hh: {},
  rh: {},
  lh: {},
  zr: {},
  cr: {},
} satisfies Record<string, Letter>;

export const categories = {
  masculineVowel: ["a", "o", "u"],
  feminineVowel: ["e", "ee", "oe", "ue"],
  neuterVowel: ["i"],
  consonant: [
    "n",
    "ng",
    "b",
    "p",
    "h",
    "g",
    "m",
    "l",
    "s",
    "sh",
    "t",
    "d",
    "ch",
    "j",
    "y",
    "r",
    "w",
    "f",
    "k2",
    "k",
    "c",
    "z",
    "hh",
    "rh",
    "lh",
    "zr",
    "cr",
  ],
} satisfies Record<string, LetterID[]>;

import type { LocaleID, ConditionalMappingType } from "./locales";

export const condition: ConditionalMappingType = "particle";
type MappedIndices = number[];

export const particles: Partial<
  Record<LocaleID, Record<string, MappedIndices>>
> = {
  MNG: {
    "u u": [0],
    "ue ue": [0],
    "b ue ue": [1],
    "mvs a ch a": [1],
    "mvs a ch a g a n": [1],
    "mvs i": [1],
    "mvs i y a r": [1, 2],
    "mvs i y e r": [1, 2],
    "mvs i y a n": [1, 2],
    "mvs i y e n": [1, 2],
    "mvs u": [1],
    "mvs ue": [1],
    "mvs u n": [1],
    "mvs ue n": [1],
    "mvs u d": [1],
    "mvs ue d": [1],
    "mvs ch u": [2],
    "mvs ch ue": [2],
    "mvs t u": [2],
    "mvs t ue": [2],
    "mvs t ue r": [2],
    "mvs t ue n i": [2],
    "mvs y ue g e n": [2],
    "mvs l ue g e": [2],
    "mvs n ue g ue d": [2],
    "mvs n ue g e n": [2],
    "mvs y ue m": [2],
    "mvs y ue m s e n": [2],
    "mvs h ue": [2],
    "mvs y i": [1],
    "mvs y i n": [1],
    "mvs d a g a n": [1],
    "mvs d e g e n": [1],
    "mvs d u": [1, 2],
    "mvs d ue": [1, 2],
    "mvs d a g": [1],
    "mvs d e g": [1],
    "mvs d a h i": [1],
    "mvs d e h i": [1],
    "mvs d u r": [1],
    "mvs d ue r": [1, 2],
    "mvs d u n i": [1],
    "mvs d ue n i": [1, 2],
    "mvs d u g a r": [1],
    "mvs d ue g e r": [1, 2],
    "mvs d a": [1],
    "mvs d e": [1],
  },
  SIB: {
    "mvs i": [1],
  },
  MCH: {
    "mvs i": [1],
  },
} as const;

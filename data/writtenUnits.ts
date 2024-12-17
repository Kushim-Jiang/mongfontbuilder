import type { JoiningPosition } from ".";

type WrittenUnit = Partial<Record<JoiningPosition, WrittenUnitVariant>>;
type WrittenUnitVariant = {
  archaic?: true;
};
export type WrittenUnitID = keyof typeof writtenUnits;

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

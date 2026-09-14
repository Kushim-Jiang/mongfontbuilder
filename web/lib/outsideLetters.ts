import type { JoiningPosition } from "../../data/misc";
import type { WrittenUnitID } from "../../data/writtenUnits";

/**
 * A letter that lies outside every writing system: no character of the data is written
 * with its written units, so the character table is told what it draws.
 */
export interface OutsideLetter {
  charName: string;
  /** The written unit each joining position is written with. */
  drawn: Partial<Record<JoiningPosition, WrittenUnitID>>;
  /** The joining position a position takes its form from. */
  borrowed: Partial<Record<JoiningPosition, JoiningPosition>>;
  /** The positions whose form is required by the font, but not recommended. */
  unrecommended?: JoiningPosition[];
}

/**
 * The letters that lie outside every writing system, which the character table lists by
 * code point along with the characters of the writing systems.
 */
export const outsideLetters: OutsideLetter[] = [
  {
    charName: "MONGOLIAN LETTER CHA WITH TWO DOTS",
    drawn: { init: "Cx", medi: "Cx", fina: "Cx" },
    borrowed: { isol: "init" },
  },
  {
    charName: "MONGOLIAN LETTER TODO ALI GALI TA",
    drawn: { init: "Dz", medi: "Dz" },
    borrowed: { isol: "init", fina: "medi" },
    unrecommended: ["init", "medi"],
  },
];

/** The written units those letters are drawn with, which no character of the data writes. */
export const outsideUnits: WrittenUnitID[] = [
  ...new Set(outsideLetters.flatMap((letter) => Object.values(letter.drawn))),
];

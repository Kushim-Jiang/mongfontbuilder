import Names from "@unicode/unicode-17.0.0/Names";
import type { LocaleID } from "../../data/locales";
import type { LocaleNamespace } from "../../data/aliases";
import type { JoiningPosition } from "../../data/misc";
import type { FVS, VariantData } from "../../data/variants";
import type { WrittenUnitID } from "../../data/writtenUnits";
import { joiningPositions } from "../../data/misc";
import { locales } from "../../data/locales";
import { aliases } from "../../data/aliases";
import { variants } from "../../data/variants";
import { writtenUnits, controls } from "../../data/writtenUnits";

export const nameToCP = new Map(
  [...Names].filter(([_, v]) => !v.startsWith("<")).map(([k, v]) => [v, k]),
);

export function hexFromCP(cp: number): string {
  return cp.toString(16).toUpperCase().padStart(4, "0");
}

// ── Locale helpers ──

export function localeNS(locale: LocaleID): LocaleNamespace {
  return locale.slice(0, 3) as LocaleNamespace;
}

export function orderedAliases(locale: LocaleID): string[] {
  return [
    ...locales[locale].categories.vowel,
    ...locales[locale].categories.consonant,
  ];
}

// ── Alias → charName lookup ──

export function resolveCharName(
  alias: string,
  ns: LocaleNamespace,
): string | undefined {
  for (const [name, localeToAlias] of Object.entries(aliases)) {
    if ((localeToAlias as Record<string, string>)[ns] === alias) return name;
  }
}

// ── Variant helpers ──

export function isVariantRef(
  w: unknown,
): w is [JoiningPosition, FVS, LocaleID?] {
  return Array.isArray(w) && joiningPositions.includes(w[0] as JoiningPosition);
}

export function getWritten(
  variant: VariantData,
  loc: LocaleID,
): WrittenUnitID[] | undefined {
  const w = variant.locales[loc]?.written ?? variant.written;
  if (!w) return undefined;
  if (isVariantRef(w)) return undefined;
  return w as WrittenUnitID[];
}

export function resolveRef(
  charName: string,
  refPos: JoiningPosition,
  refFvs: FVS,
  locale: LocaleID,
): WrittenUnitID[] | undefined {
  const refVariant = variants[charName]?.[refPos]?.[refFvs];
  if (!refVariant) return undefined;
  const w = refVariant.locales[locale]?.written ?? refVariant.written;
  if (!w || isVariantRef(w)) return undefined;
  return w as WrittenUnitID[];
}

// ── mapGetOrCreate ──

export function mapGetOrCreate<K, V>(
  map: Map<K, V>,
  key: K,
  factory: () => V,
): V {
  let v = map.get(key);
  if (v === undefined) {
    v = factory();
    map.set(key, v);
  }
  return v;
}

// ── Cursive unit position ──

export function unitPosition(
  wordPos: JoiningPosition,
  index: number,
  total: number,
): JoiningPosition {
  if (total === 1) return wordPos;
  if (index === 0)
    return wordPos === "init" || wordPos === "isol" ? "init" : "medi";
  if (index === total - 1)
    return wordPos === "fina" || wordPos === "isol" ? "fina" : "medi";
  return "medi";
}

// ── Text builder ──

export function buildWrittenText(
  written: WrittenUnitID[],
  position: JoiningPosition,
): string {
  let result = "";
  for (const [i, unit] of written.entries()) {
    const up = unitPosition(position, i, written.length);
    const code = (
      writtenUnits[unit] as Partial<Record<JoiningPosition, { code: number }>>
    )?.[up]?.code;
    if (code != null) result += String.fromCodePoint(code);
  }
  return result || "?";
}

export const niruguText = String.fromCodePoint(controls.Nirugu.code);

export function ctxBefore(p: JoiningPosition) {
  return p === "medi" || p === "fina";
}
export function ctxAfter(p: JoiningPosition) {
  return p === "init" || p === "medi";
}

export function sortedFVSKeys(
  map: Map<JoiningPosition, Map<FVS, unknown>>,
): FVS[] {
  return [...new Set([...map.values()].flatMap((m) => [...m.keys()]))]
    .filter((f) => f !== 0)
    .sort((a, b) => a - b);
}

// @ts-ignore
import _Names from "@unicode/unicode-16.0.0/Names";

const Names: Map<number, string> = _Names;
export const nameToCP = new Map(
  [...Names].filter(([_, v]) => !v.startsWith("<")).map(([k, v]) => [v, k]),
);

export function hexFromCP(cp: number): string {
  return cp.toString(16).toUpperCase().padStart(4, "0");
}

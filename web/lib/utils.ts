import Names from "@unicode/unicode-17.0.0/Names";

export const nameToCP = new Map(
  [...Names].filter(([_, v]) => !v.startsWith("<")).map(([k, v]) => [v, k]),
);

export function hexFromCP(cp: number): string {
  return cp.toString(16).toUpperCase().padStart(4, "0");
}

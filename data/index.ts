export const joiningPositions = ["isol", "init", "medi", "fina"] as const;
export type JoiningPosition = (typeof joiningPositions)[number];

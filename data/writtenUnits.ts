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
  A2: {
    medi: {},
    fina: {},
  },
  Aa: {
    isol: {},
    fina: {},
  },
  Ah: {
    medi: {},
    fina: {},
  },
  Ai: {
    medi: {},
    fina: {},
  },
  At: {
    fina: {},
  },
  Aw: {
    fina: {},
  },
  B: {
    init: {},
    medi: {},
    fina: {},
  },
  B2: {
    fina: {},
  },
  Bc: {
    init: {},
    medi: {},
  },
  Bg: {
    init: {},
    medi: {},
    fina: {},
  },
  Bh: {
    init: {},
    medi: {},
  },
  C: {
    init: {},
    medi: {},
    fina: {},
  },
  Cc: {
    init: {},
    medi: {},
  },
  Ch: {
    init: {},
    medi: {},
    fina: {},
  },
  Cp: {
    init: {},
    medi: {},
    fina: {},
  },
  Cr: {
    init: {},
  },
  Cr2: {
    init: {},
    medi: {},
  },
  Cs: {
    init: {},
    medi: {},
  },
  Ct: {
    init: {},
    medi: {},
  },
  D: {
    init: {},
    medi: {},
    fina: {},
  },
  Db: {
    medi: {},
  },
  Dd: {
    medi: {},
    fina: {},
  },
  Dh: {
    medi: {},
  },
  Dp: {
    init: {},
    medi: {},
    fina: {},
  },
  Dq: {
    init: {},
    medi: {},
    fina: {},
  },
  Dr: {
    init: {},
    medi: {},
    fina: {},
  },
  Ds: {
    init: {},
    medi: {},
    fina: {},
  },
  Ds2: {
    init: {},
    medi: {},
  },
  Dt: {
    medi: {},
  },
  Dv: {
    init: {},
    medi: {},
    fina: {},
  },
  Dx: {
    medi: {},
  },
  Dy: {
    init: {},
    medi: {},
  },
  E: {
    medi: {},
    fina: {},
  },
  F: {
    init: {},
    medi: {},
    fina: {},
  },
  G4: {
    fina: {},
  },
  G: {
    init: {},
    medi: {},
    fina: {},
  },
  Gc: {
    init: {},
    medi: {},
  },
  Gh: {
    init: {},
    medi: {},
  },
  Gp: {
    init: {},
    medi: {},
  },
  Gx: {
    init: { archaic: true },
    medi: { archaic: true },
    fina: { archaic: true },
  },
  H: {
    init: {},
    medi: {},
    fina: {},
  },
  Hb: {
    init: {},
    medi: {},
  },
  Hc: {
    init: {},
    medi: {},
  },
  Hh: {
    init: {},
    medi: {},
  },
  Hp: {
    init: {},
    medi: {},
    fina: {},
  },
  Hr: {
    medi: {},
    fina: {},
  },
  Hx: {
    init: {},
    medi: {},
    fina: {},
  },
  Hx2: {
    init: {},
  },
  Hy: {
    init: {},
    medi: {},
  },
  Hy2: {
    medi: {},
  },
  I: {
    isol: {},
    init: {},
    medi: {},
    fina: {},
  },
  I2: {
    fina: {},
  },
  I3: {
    fina: {},
  },
  I4: {
    fina: {},
  },
  Ic: {
    init: {},
    medi: {},
  },
  Ih: {
    init: {},
  },
  Ip: {
    medi: {},
    fina: {},
  },
  Iq: {
    init: {},
  },
  Ir: {
    fina: {},
  },
  It: {
    init: {},
  },
  Ix: {
    isol: { archaic: true },
  },
  Iy: {
    fina: {},
  },
  J: {
    init: {},
    medi: {},
    fina: {},
  },
  J2: {
    medi: {},
  },
  Jb: {
    init: {},
    medi: {},
    fina: {},
  },
  Jc: {
    medi: {},
  },
  Jh: {
    medi: {},
    fina: {},
  },
  Jq: {
    medi: {},
    fina: {},
  },
  Jt: {
    medi: {},
    fina: {},
  },
  K: {
    init: {},
    medi: {},
    fina: {},
  },
  K2: {
    init: {},
    medi: {},
    fina: {},
  },
  Kc: {
    init: {},
    medi: {},
  },
  Kh: {
    init: {},
    medi: {},
  },
  Kp: {
    init: {},
    medi: {},
    fina: {},
  },
  L: {
    init: {},
    medi: {},
    fina: {},
  },
  L2: {
    init: {},
  },
  Lc: {
    init: {},
    medi: {},
  },
  Lv: {
    isol: {},
    init: {},
    medi: {},
    fina: {},
  },
  M: {
    init: {},
    medi: {},
    fina: {},
  },
  M2: {
    fina: {},
  },
  N: {
    init: {},
    medi: {},
    fina: {},
  },
  N2: {
    init: {},
    fina: {},
  },
  Nb: {
    init: {},
    medi: {},
  },
  Nx: {
    medi: {},
    fina: {},
  },
  Ny: {
    init: {},
    medi: {},
  },
  O: {
    medi: {},
    fina: {},
    init: {},
  },
  Ob: {
    medi: {},
    fina: {},
  },
  Oh: {
    medi: {},
    fina: {},
  },
  Op: {
    medi: {},
    fina: {},
  },
  Ot: {
    medi: {},
    fina: {},
  },
  P: {
    init: {},
    medi: {},
    fina: {},
  },
  Pb: {
    init: {},
    medi: {},
  },
  Pg: {
    init: {},
    medi: {},
    fina: {},
  },
  Ph: {
    init: {},
    medi: {},
  },
  Pp: {
    init: {},
    medi: {},
    fina: {},
  },
  Q: {
    init: {},
    medi: {},
  },
  R: {
    init: {},
    medi: {},
    fina: {},
  },
  R2: {
    fina: {},
  },
  R3: {
    init: {},
    medi: {},
  },
  Rh: {
    init: {},
    medi: {},
    fina: {},
  },
  Rh2: {
    init: {},
    medi: {},
    fina: {},
  },
  Rr: {
    init: {},
    medi: {},
  },
  Rz: {
    init: {},
    medi: {},
  },
  S: {
    init: {},
    medi: {},
    fina: {},
  },
  S3: {
    fina: {},
  },
  Sc: {
    init: {},
    medi: {},
    fina: {},
  },
  Sh: {
    init: {},
    medi: {},
    fina: {},
  },
  Sp: {
    init: {},
    medi: {},
    fina: {},
  },
  St: {
    init: {},
    medi: {},
    fina: {},
  },
  Sx: {
    init: {},
    medi: {},
    fina: {},
  },
  Sz: {
    fina: { archaic: true },
  },
  T: {
    init: {},
    medi: {},
    fina: {},
  },
  Tb: {
    init: {},
  },
  Th: {
    init: {},
  },
  Tp: {
    init: {},
    medi: {},
    fina: {},
  },
  Ts: {
    init: {},
  },
  Tt: {
    init: {},
  },
  Tx: {
    init: {},
  },
  U: {
    fina: {},
    isol: {},
  },
  Ue: {
    fina: {},
  },
  Uh: {
    fina: {},
  },
  Up: {
    fina: {},
  },
  Ux: {
    isol: { archaic: true },
  },
  V: {
    init: {},
    medi: {},
  },
  W: {
    init: {},
    medi: {},
    fina: {},
  },
  Wb: {
    init: {},
    medi: {},
    fina: {},
  },
  Wn: {
    init: {},
    medi: {},
    fina: {},
  },
  Wp: {
    medi: {},
    fina: {},
  },
  Y: {
    init: {},
    medi: {},
  },
  Yp: {
    medi: {},
    fina: {},
  },
  Z: {
    init: {},
    medi: {},
    fina: {},
  },
  Zc: {
    init: {},
    medi: {},
    fina: {},
  },
  Zr: {
    init: {},
    medi: {},
    fina: {},
  },
  Zs: {
    init: {},
    medi: {},
    fina: {},
  },
  Zt: {
    init: {},
    medi: {},
  },
  Zz: {
    init: {},
    medi: {},
    fina: {},
  },
} satisfies Record<string, WrittenUnit>;

export type WrittenUnitID = keyof typeof writtenUnits;

export const writtenUnits = {
  A: {
    isol: { code: 0xe001 },
    init: { code: 0xe002 },
    medi: { code: 0xe003, post_b: 0xe200 },
    fina: { code: 0xe004, post_w: 0xe24c },
  },
  A2: {
    init: { code: 0xe102 },
  },
  Aa: {
    isol: { code: 0xe005 },
    fina: { code: 0xe006, post_b: 0xe201 },
  },
  Ah: {
    medi: { code: 0xe0a2, post_b: 0xe232 },
    fina: { code: 0xe0a3 },
  },
  Ai: {
    medi: { code: 0xe0a4 },
    fina: { code: 0xe0a5 },
  },
  At: {
    fina: { code: 0xe0a6, post_b: 0xe233 },
  },
  Aw: {
    fina: { code: 0xe103 },
  },
  B: {
    init: { code: 0xe017, pre_a: 0xe209, pre_o: 0xe20a },
    medi: { code: 0xe018, pre_a: 0xe20b, pre_o: 0xe20c },
    fina: { code: 0xe019 },
  },
  B2: {
    fina: { code: 0xe01a },
  },
  Bc: {
    init: { code: 0xe104, pre_a: 0xe259, pre_o: 0xe25a },
    medi: { code: 0xe105, pre_a: 0xe263, pre_o: 0xe264 },
  },
  Bg: {
    init: { code: 0xe0d9, pre_a: 0xe24d, pre_o: 0xe24e },
    medi: { code: 0xe0da, pre_a: 0xe24f, pre_o: 0xe250 },
    fina: { code: 0xe0db },
  },
  Bh: {
    init: { code: 0xe0fa, pre_a: 0xe257, pre_o: 0xe258 },
    medi: { code: 0xe0fb, pre_a: 0xe267, pre_o: 0xe268 },
  },
  C: {
    init: { code: 0xe055 },
    medi: { code: 0xe056 },
    fina: { code: 0xe057 },
  },
  Cc: {
    init: { code: 0xe0a7 },
    medi: { code: 0xe0a8 },
  },
  Ch: {
    init: { code: 0xe03f },
    medi: { code: 0xe040 },
    fina: { code: 0xe041 },
  },
  Cp: {
    init: { code: 0xe06b },
    medi: { code: 0xe06c },
    fina: { code: 0xe06d },
  },
  Cr: {
    init: { code: 0xe061 },
  },
  Cr2: {
    init: { code: 0xe0dd },
    medi: { code: 0xe0de },
  },
  Cs: {
    init: { code: 0xe0a9 },
    medi: { code: 0xe0aa },
  },
  Ct: {
    init: { code: 0xe106 },
    medi: { code: 0xe107 },
  },
  D: {
    init: { code: 0xe03a },
    medi: { code: 0xe03b },
    fina: { code: 0xe03c },
  },
  Db: {
    medi: { code: 0xe0ab },
  },
  Dd: {
    medi: { code: 0xe03d },
    fina: { code: 0xe03e },
  },
  Dh: {
    medi: { code: 0xe0ac },
  },
  Dp: {
    init: { code: 0xe06e },
    medi: { code: 0xe06f },
    fina: { code: 0xe070 },
  },
  Dq: {
    init: { code: 0xe0df },
    medi: { code: 0xe0e0 },
    fina: { code: 0xe0e1 },
  },
  Dr: {
    init: { code: 0xe108 },
    medi: { code: 0xe109 },
    fina: { code: 0xe10a },
  },
  Ds: {
    init: { code: 0xe0e2 },
    medi: { code: 0xe0e3 },
    fina: { code: 0xe0e4 },
  },
  Dt: {
    init: { code: 0xe10b },
    medi: { code: 0xe0ad },
  },
  Dv: {
    init: { code: 0xe0e5 },
    medi: { code: 0xe0e6 },
    fina: { code: 0xe0e7 },
  },
  Dw: {
    medi: { code: 0xe10d },
  },
  Dx: {
    medi: { code: 0xe10c },
  },
  Dy: {
    init: { code: 0xe10e },
    medi: { code: 0xe10f },
  },
  E: {
    medi: { code: 0xe071, post_b: 0xe071 },
    fina: { code: 0xe072, post_b: 0xe072 },
  },
  F: {
    init: { code: 0xe04c, pre_a: 0xe219, pre_o: 0xe21a },
    medi: { code: 0xe04d, pre_a: 0xe21b, pre_o: 0xe21c },
    fina: { code: 0xe04e },
  },
  G: {
    init: { code: 0xe025, pre_a: 0xe211, pre_o: 0xe212 },
    medi: { code: 0xe026, pre_a: 0xe213, pre_o: 0xe214 },
    fina: { code: 0xe027 },
  },
  G2: {
    fina: { code: 0xe073 },
  },
  G3: {
    fina: { code: 0xe0ae },
  },
  G4: {
    fina: { code: 0xe0d5 },
  },
  Gc: {
    init: { code: 0xe0af, pre_a: 0xe238, pre_o: 0xe239 },
    medi: { code: 0xe0b0, pre_a: 0xe23a, pre_o: 0xe23b },
  },
  Gh: {
    init: { code: 0xe0b1, pre_a: 0xe234, pre_o: 0xe235 },
    medi: { code: 0xe0b2, pre_a: 0xe236, pre_o: 0xe237 },
  },
  Gp: {
    init: { code: 0xe074, pre_a: 0xe229, pre_o: 0xe22a },
    medi: { code: 0xe075, pre_a: 0xe261, pre_o: 0xe262 },
  },
  Gx: {
    init: { code: 0xe028, pre_a: 0xe215, pre_o: 0xe216 },
    medi: { code: 0xe029, pre_a: 0xe217, pre_o: 0xe218 },
    fina: { code: 0xe0d6 },
  },
  H: {
    init: { code: 0xe01e },
    medi: { code: 0xe01f },
    fina: { code: 0xe020 },
  },
  Hb: {
    init: { code: 0xe076 },
    medi: { code: 0xe077 },
  },
  Hc: {
    init: { code: 0xe0b3 },
    medi: { code: 0xe0b4 },
  },
  Hh: {
    init: { code: 0xe0b5 },
    medi: { code: 0xe0b6 },
  },
  Hh2: {
    medi: { code: 0xe139 },
  },
  Hp: {
    medi: { code: 0xe078 },
    fina: { code: 0xe079 },
  },
  Hr: {
    medi: { code: 0xe05b },
    fina: { code: 0xe05c },
  },
  Hx: {
    init: { code: 0xe021 },
    medi: { code: 0xe022 },
    fina: { code: 0xe023, pre_mvs: 0xe024 },
  },
  Hx2: {
    init: { code: 0xe07a },
  },
  Hy: {
    init: { code: 0xe110 },
    medi: { code: 0xe111 },
  },
  Hy2: {
    medi: { code: 0xe112 },
  },
  I: {
    isol: { code: 0xe007 },
    init: { code: 0xe008 },
    medi: { code: 0xe009, post_b: 0xe202 },
    fina: { code: 0xe00a, post_b: 0xe203 },
  },
  I3: {
    fina: { code: 0xe07b, post_b: 0xe22b },
  },
  I4: {
    fina: { code: 0xe0e8 },
  },
  Ic: {
    init: { code: 0xe0b7 },
    medi: { code: 0xe0b8 },
  },
  Ih: {
    init: { code: 0xe113 },
  },
  Ip: {
    medi: { code: 0xe07c, post_b: 0xe07c },
  },
  Iq: {
    init: { code: 0xe114 },
  },
  Ir: {
    fina: { code: 0xe0fc },
  },
  It: {
    init: { code: 0xe115 },
  },
  Ix: {
    isol: { code: 0xe00b },
  },
  Iy: {
    fina: { code: 0xe116 },
  },
  J: {
    init: { code: 0xe07d },
    medi: { code: 0xe042 },
    fina: { code: 0xe043 },
  },
  J2: {
    medi: { code: 0xe0b9 },
  },
  Jb: {
    init: { code: 0xe07e },
    medi: { code: 0xe07f },
    fina: { code: 0xe080 },
  },
  Jc: {
    medi: { code: 0xe0d7 },
    fina: { code: 0xe117 },
  },
  Jh: {
    medi: { code: 0xe118 },
  },
  Jq: {
    medi: { code: 0xe119 },
  },
  Jt: {
    medi: { code: 0xe11a },
    fina: { code: 0xe11b },
  },
  K: {
    init: { code: 0xe052, pre_a: 0xe21d, pre_o: 0xe21e },
    medi: { code: 0xe053, pre_a: 0xe21f, pre_o: 0xe220 },
    fina: { code: 0xe054 },
  },
  K2: {
    init: { code: 0xe04f, pre_a: 0xe221, pre_o: 0xe222 },
    medi: { code: 0xe050, pre_a: 0xe223, pre_o: 0xe224 },
    fina: { code: 0xe051 },
  },
  Kc: {
    init: { code: 0xe0ba, pre_a: 0xe240, pre_o: 0xe241 },
    medi: { code: 0xe0bb, pre_a: 0xe242, pre_o: 0xe243 },
  },
  Kh: {
    init: { code: 0xe0bc, pre_a: 0xe23c, pre_o: 0xe23d },
    medi: { code: 0xe0bd, pre_a: 0xe23e, pre_o: 0xe23f },
    fina: { code: 0xe11c },
  },
  Kp: {
    init: { code: 0xe081, pre_a: 0xe225, pre_o: 0xe226 },
    medi: { code: 0xe082, pre_a: 0xe25c, pre_o: 0xe25e },
    fina: { code: 0xe083 },
  },
  L: {
    init: { code: 0xe02d },
    medi: { code: 0xe02e, post_b: 0xe208 },
    fina: { code: 0xe02f },
  },
  L2: {
    init: { code: 0xe11d },
  },
  Lc: {
    init: { code: 0xe11e },
    medi: { code: 0xe11f },
  },
  Lv: {
    medi: { code: 0xe084 },
    fina: { code: 0xe085 },
  },
  M: {
    init: { code: 0xe02a },
    medi: { code: 0xe02b, post_b: 0xe207 },
    fina: { code: 0xe02c },
  },
  M2: {
    fina: { code: 0xe086 },
  },
  N: {
    init: { code: 0xe013 },
    medi: { code: 0xe014 },
    fina: { code: 0xe015, pre_mvs: 0xe016 },
  },
  N2: {
    init: { code: 0xe087 },
  },
  Nb: {
    init: { code: 0xe120 },
    medi: { code: 0xe121 },
  },
  Nx: {
    medi: { code: 0xe0be },
    fina: { code: 0xe0bf },
  },
  Ny: {
    init: { code: 0xe088 },
    medi: { code: 0xe089 },
    fina: { code: 0xe0e9 },
  },
  O: {
    init: { code: 0xe00c },
    medi: { code: 0xe00d, post_b: 0xe204 },
    fina: { code: 0xe00e, post_b: 0xe205 },
  },
  Ob: {
    medi: { code: 0xe08a, post_b: 0xe22d },
    fina: { code: 0xe08b, post_b: 0xe22c },
  },
  Oh: {
    medi: { code: 0xe0c0, post_b: 0xe245 },
    fina: { code: 0xe0c1, post_b: 0xe244 },
  },
  Op: {
    medi: { code: 0xe08c, post_b: 0xe22e },
    fina: { code: 0xe08d, post_b: 0xe22f },
  },
  Ot: {
    medi: { code: 0xe08e, post_b: 0xe230 },
    fina: { code: 0xe08f, post_b: 0xe231 },
  },
  P: {
    init: { code: 0xe01b, pre_a: 0xe20d, pre_o: 0xe20e },
    medi: { code: 0xe01c, pre_a: 0xe20f, pre_o: 0xe210 },
    fina: { code: 0xe01d },
  },
  Pb: {
    init: { code: 0xe0c2, pre_a: 0xe246, pre_o: 0xe247 },
    medi: { code: 0xe0c3, pre_a: 0xe248, pre_o: 0xe249 },
  },
  Pg: {
    init: { code: 0xe0ea, pre_a: 0xe251, pre_o: 0xe252 },
    medi: { code: 0xe0eb, pre_a: 0xe253, pre_o: 0xe254 },
  },
  Ph: {
    init: { code: 0xe0fd, pre_a: 0xe255, pre_o: 0xe256 },
    medi: { code: 0xe0fe, pre_a: 0xe265, pre_o: 0xe266 },
  },
  Pp: {
    init: { code: 0xe090, pre_a: 0xe227, pre_o: 0xe228 },
    medi: { code: 0xe091, pre_a: 0xe25f, pre_o: 0xe260 },
    fina: { code: 0xe092 },
  },
  Q: {
    init: { code: 0xe0ec },
    medi: { code: 0xe0ed },
  },
  R: {
    init: { code: 0xe046 },
    medi: { code: 0xe047 },
    fina: { code: 0xe048 },
  },
  R2: {
    fina: { code: 0xe0d8 },
  },
  R3: {
    init: { code: 0xe122 },
    medi: { code: 0xe123 },
  },
  Rh: {
    init: { code: 0xe05d },
    medi: { code: 0xe05e },
    fina: { code: 0xe05f },
  },
  Rh2: {
    init: { code: 0xe0ee },
    medi: { code: 0xe0ef },
  },
  Rr: {
    init: { code: 0xe0c4 },
    medi: { code: 0xe0c5 },
  },
  Rz: {
    init: { code: 0xe0ff },
    medi: { code: 0xe100 },
  },
  S: {
    init: { code: 0xe030 },
    medi: { code: 0xe031 },
    fina: { code: 0xe032 },
  },
  S3: {
    fina: { code: 0xe124 },
  },
  Sc: {
    init: { code: 0xe125 },
    medi: { code: 0xe126 },
  },
  Sh: {
    init: { code: 0xe034 },
    medi: { code: 0xe035 },
    fina: { code: 0xe036 },
  },
  Sp: {
    init: { code: 0xe0c6 },
    medi: { code: 0xe0c7 },
    fina: { code: 0xe0c8 },
  },
  St: {
    init: { code: 0xe127 },
    medi: { code: 0xe128 },
  },
  St2: {
    init: { code: 0xe129 },
    medi: { code: 0xe12a },
  },
  Sx: {
    init: { code: 0xe0f0 },
    medi: { code: 0xe0f1 },
    fina: { code: 0xe0f2 },
  },
  Sz: {
    fina: { code: 0xe033 },
  },
  T: {
    init: { code: 0xe037 },
    medi: { code: 0xe038 },
    fina: { code: 0xe039 },
  },
  Tb: {
    init: { code: 0xe0c9 },
  },
  Th: {
    init: { code: 0xe0ca },
  },
  Tp: {
    init: { code: 0xe093 },
    medi: { code: 0xe094 },
    fina: { code: 0xe095 },
  },
  Ts: {
    init: { code: 0xe12c },
  },
  Tt: {
    init: { code: 0xe0cb },
  },
  Tx: {
    init: { code: 0xe12b },
  },
  U: {
    isol: { code: 0xe00f },
    fina: { code: 0xe010 },
  },
  Ue: {
    fina: { code: 0xe012, post_b: 0xe206 },
  },
  Uh: {
    fina: { code: 0xe0cc },
  },
  Up: {
    fina: { code: 0xe096 },
  },
  Ux: {
    isol: { code: 0xe011 },
  },
  V: {
    init: { code: 0xe0cd },
    medi: { code: 0xe0ce },
  },
  Vi: {
    fina: { code: 0xe0dc },
  },
  W: {
    init: { code: 0xe049 },
    medi: { code: 0xe04a },
    fina: { code: 0xe04b },
  },
  Wb: {
    init: { code: 0xe097 },
    medi: { code: 0xe098 },
    fina: { code: 0xe099 },
  },
  Wc: {
    init: { code: 0xe12d, pre_i: 0xe12d },
    medi: { code: 0xe12e, pre_i: 0xe12e },
  },
  Wd: {
    init: { code: 0xe12f, pre_i: 0xe12f },
    medi: { code: 0xe130, pre_i: 0xe130 },
  },
  Wn: {
    init: { code: 0xe0f3 },
    medi: { code: 0xe0f4 },
    fina: { code: 0xe0f5 },
  },
  Wp: {
    medi: { code: 0xe0f6 },
    fina: { code: 0xe101 },
  },
  Y: {
    init: { code: 0xe044 },
    medi: { code: 0xe045 },
  },
  Yp: {
    medi: { code: 0xe09a },
    fina: { code: 0xe09b },
  },
  Z: {
    init: { code: 0xe058 },
    medi: { code: 0xe059 },
    fina: { code: 0xe05a },
  },
  Zc: {
    init: { code: 0xe133 },
    medi: { code: 0xe134 },
    fina: { code: 0xe135 },
  },
  Zr: {
    init: { code: 0xe060 },
  },
  Zr2: {
    init: { code: 0xe0f7 },
    medi: { code: 0xe0f8 },
    fina: { code: 0xe0f9 },
  },
  Zs: {
    init: { code: 0xe0d0 },
    medi: { code: 0xe0d1 },
  },
  Zs2: {
    init: { code: 0xe0d3, pre_i: 0xe24a },
    medi: { code: 0xe0d4, pre_i: 0xe24b },
  },
  Zt: {
    init: { code: 0xe131 },
    medi: { code: 0xe132 },
  },
  Zz: {
    init: { code: 0xe09f },
    medi: { code: 0xe0a0 },
    fina: { code: 0xe0a1 },
  },
  Zz2: {
    init: { code: 0xe09c },
    medi: { code: 0xe09d },
    fina: { code: 0xe09e },
  },
  Zz3: {
    init: { code: 0xe136 },
    medi: { code: 0xe137 },
    fina: { code: 0xe138 },
  },
} as const;

export const controls = {
  Fvs1: { code: 0xe063 },
  Fvs2: { code: 0xe064 },
  Fvs3: { code: 0xe065 },
  Fvs4: { code: 0xe066 },
  Zwj: { code: 0xe067 },
  Zwnj: { code: 0xe068 },
  Nnbsp: { code: 0xe069 },
  Nirugu: { code: 0xe000 },
  Mvs: { code: 0xe06a, wide: 0x0020, narrow: 0xe062 },
};

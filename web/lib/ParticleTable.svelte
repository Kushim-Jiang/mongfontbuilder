<script lang="ts">
  interface Props {
    locale: LocaleID;
  }
  let { locale }: Props = $props();

  import type { LocaleID } from "../../data/locales";
  import type { JoiningPosition } from "../../data/misc";
  import type { WrittenUnitID } from "../../data/writtenUnits";
  import { particles } from "../../data/particles";
  import { writtenUnits } from "../../data/writtenUnits";

  type Atom = { unit: string; text: string; blue: boolean };
  type Row = { nominal: string[]; atoms: Atom[] };

  function wordPos(i: number, n: number): JoiningPosition {
    if (n <= 1) return "isol";
    if (i === 0) return "init";
    if (i === n - 1) return "fina";
    return "medi";
  }

  // Back/rounded vowels ride on a bow with a `pre_o` variant; the others use `pre_a`.
  const back = new Set(["O", "U", "Ue", "Ob", "Op", "Ot", "Oh", "Up", "Uh"]);
  const bowKeyFor = (vowel: string): "pre_a" | "pre_o" => (back.has(vowel) ? "pre_o" : "pre_a");

  type UnitRec = Partial<Record<JoiningPosition, Record<string, number>>>;

  function slot(unit: string, pos: JoiningPosition): Record<string, number> | undefined {
    const rec = writtenUnits[unit as WrittenUnitID] as unknown as UnitRec | undefined;
    return rec?.[pos];
  }

  function codeAt(unit: string, pos: JoiningPosition, key?: string): number | undefined {
    const s = slot(unit, pos);
    return (key ? s?.[key] : undefined) ?? s?.code;
  }

  function buildRow(key: string, form: string, indices: number[]): Row {
    const nominal = key.split(" ");

    const formTokens = form.split(" ").filter(Boolean);
    const hasMvs = formTokens[0] === "Mvs.wide";
    const wordTokens = hasMvs ? formTokens.slice(1) : formTokens;

    // Flatten each space token into atoms. An underscore token (`X_Y`) is a
    // bow cluster: `X` is the bowed onset and `Y` the vowel riding on its bow,
    // and it occupies two letter slots (not one).
    type Meta = { unit: string; kind: "plain" | "bow" | "rider" };
    const meta: Meta[] = [];
    for (const token of wordTokens) {
      const subs = token.split("_");
      subs.forEach((unit, si) => {
        meta.push({ unit, kind: subs.length === 1 ? "plain" : si === 0 ? "bow" : "rider" });
      });
    }
    const nLetters = meta.length;

    const blue = new Set(indices);
    const atoms: Atom[] = [];
    let flat = 0;
    if (hasMvs) {
      atoms.push({ unit: "Mvs.wide", text: "\u00a0", blue: false });
      flat = 1;
    }

    for (const [li, m] of meta.entries()) {
      const pos = wordPos(li, nLetters);
      let code: number | undefined;
      if (m.kind === "bow") {
        const vowel = meta[li + 1]?.unit;
        const key = vowel && bowKeyFor(vowel);
        code = codeAt(m.unit, pos, key) ?? codeAt(m.unit, pos) ?? codeAt(m.unit, "medi");
      } else if (m.kind === "rider") {
        code = codeAt(m.unit, pos, "post_b") ?? codeAt(m.unit, "medi", "post_b") ?? codeAt(m.unit, pos) ?? codeAt(m.unit, "medi");
      } else {
        code = codeAt(m.unit, pos) ?? codeAt(m.unit, "medi");
      }
      atoms.push({ unit: m.unit, text: code != null ? String.fromCodePoint(code) : "?", blue: blue.has(flat) });
      flat++;
    }

    return { nominal, atoms };
  }

  const rows = $derived(Object.entries(particles[locale] ?? {}).map(([key, p]) => buildRow(key, p.form, p.indices)));
</script>

<table>
  <thead>
    <tr><th>Particle</th><th>Form</th></tr>
  </thead>
  <tbody>
    {#each rows as row}
      <tr>
        <td class="nominal">
          {#each row.nominal as t, i}
            {i ? " " : ""}{#if t === "mvs"}<span class="mvs">mvs</span>{:else}<a class="letter" href="#{t}">{t}</a>{/if}
          {/each}
        </td>
        <td class="shape"
          ><span class="wu"
            >{#each row.atoms as a}<span class={a.blue ? "blue" : ""}>{a.text}</span>{/each}</span
          ></td
        >
      </tr>
    {/each}
  </tbody>
</table>

<style>
  td,
  th {
    text-align: center !important;
    vertical-align: middle;
  }
  td.shape .wu {
    line-height: 1;
    white-space: nowrap;
  }
  td.shape .wu span {
    color: hsl(0 0% 25%);
  }
  td.shape .wu span.blue {
    color: hsl(210 80% 45%);
  }
  td.nominal {
    text-align: left !important;
  }
  td.nominal .letter {
    font-style: italic;
  }
  td.nominal .mvs {
    color: hsl(210 30% 55%);
    font-style: italic;
  }
</style>

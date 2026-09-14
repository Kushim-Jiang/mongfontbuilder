<script lang="ts">
  interface Props {
    locale: LocaleID | LocaleID[];
    /** Written units that no character writes, which the table lists in place. */
    outside?: WrittenUnitID[];
  }
  let { locale, outside = [] }: Props = $props();

  import type { LocaleID } from "../../data/locales";
  import type { JoiningPosition } from "../../data/misc";
  import type { WrittenUnitID } from "../../data/writtenUnits";
  import { joiningPositions } from "../../data/misc";
  import { variants } from "../../data/variants";
  import { writtenUnits } from "../../data/writtenUnits";
  import { aliases } from "../../data/aliases";
  import LetterVariant from "./LetterVariant.svelte";
  import { localeNS, mapGetOrCreate, isVariantRef, niText } from "./utils";

  const localesToShow = $derived(Array.isArray(locale) ? locale : [locale]);
  /** A unified table merges the writing systems, so each shape is labelled with them. */
  const unified = $derived(localesToShow.length > 1);

  const unitToPositionToLetters = $derived.by(() => {
    const map = new Map<WrittenUnitID, Map<JoiningPosition, Map<LocaleID, Set<string>>>>();
    for (const currentLocale of localesToShow) {
      const _localeNamespace = localeNS(currentLocale);
      for (const [charName, positionToFVSToVariant] of Object.entries(variants)) {
        const aliasData = aliases[charName];
        const alias = typeof aliasData === "object" ? aliasData[_localeNamespace] : aliasData;
        if (!alias) continue;
        for (const [position, fvsToVariant] of Object.entries(positionToFVSToVariant)) {
          for (const variant of Object.values(fvsToVariant)) {
            const localeData = variant.locales[currentLocale];
            if (!localeData) continue;
            const written = localeData.written ?? variant.written;
            if (isVariantRef(written)) continue;
            for (const [index, unit] of (written as WrittenUnitID[]).entries()) {
              const positionToLetters = mapGetOrCreate(map, unit, () => new Map<JoiningPosition, Map<LocaleID, Set<string>>>());
              const up: JoiningPosition = written.length === 1 ? (position as JoiningPosition) : ["isol", "init"].includes(position) && index === 0 ? "init" : ["isol", "fina"].includes(position) && index === written.length - 1 ? "fina" : "medi";
              const localeToLetters = mapGetOrCreate(positionToLetters, up, () => new Map<LocaleID, Set<string>>());
              mapGetOrCreate(localeToLetters, currentLocale, () => new Set()).add(alias);
            }
          }
        }
      }
    }
    return map;
  });

  /**
   * The joining positions a written unit is drawn in: the positions that some character of
   * the writing systems writes it in, or, for a unit no character writes, the positions
   * the data gives it.
   */
  function positionsOf(id: WrittenUnitID): Map<JoiningPosition, Map<LocaleID, Set<string>>> | undefined {
    const written = unitToPositionToLetters.get(id);
    if (written) return written;
    if (!outside.includes(id)) return undefined;
    const positions = writtenUnits[id] as Partial<Record<JoiningPosition, unknown>>;
    return new Map(joiningPositions.filter((position) => position in positions).map((position) => [position, new Map<LocaleID, Set<string>>()]));
  }

  type LigPart = { text: string; blue: boolean; isNi?: boolean };
  type LigRow = { parts: LigPart[]; kind: string };
  type LigColumn = LigRow[];

  const unitToLigature = $derived.by(() => {
    const map = new Map<WrittenUnitID, { init: LigColumn; medi: LigColumn; fina: LigColumn }>();
    for (const [id, positions] of Object.entries(writtenUnits)) {
      const uid = id as WrittenUnitID;
      const pos = positions as Record<string, { code: number } & Record<string, number>>;

      const firstChar = id[0];
      const isBackVowel = "OU".includes(firstChar);

      const init: LigColumn = [];
      const medi: LigColumn = [];
      const fina: LigColumn = [];

      // post_b — use unit's own post_b variant; only if exists at that position
      if (pos.medi?.post_b != null) {
        const preCode = (writtenUnits.B.init as Record<string, number>)[isBackVowel ? "pre_o" : "pre_a"];
        medi.push({
          parts: [
            { text: String.fromCodePoint(preCode), blue: true },
            { text: String.fromCodePoint(pos.medi.post_b), blue: false },
            { text: niText("fina"), blue: true, isNi: true },
          ],
          kind: "post_b",
        });
      }
      if (pos.fina?.post_b != null) {
        const preCode = (writtenUnits.B.init as Record<string, number>)[isBackVowel ? "pre_o" : "pre_a"];
        fina.push({
          parts: [
            { text: String.fromCodePoint(preCode), blue: true },
            { text: String.fromCodePoint(pos.fina.post_b), blue: false },
          ],
          kind: "post_b",
        });
      }

      // pre_a — use unit's own pre_a variant
      if (pos.init?.pre_a != null) {
        const postCode = (writtenUnits.A.medi as Record<string, number>).post_b;
        init.push({
          parts: [
            { text: String.fromCodePoint(pos.init.pre_a), blue: false },
            { text: String.fromCodePoint(postCode), blue: true },
            { text: niText("fina"), blue: true, isNi: true },
          ],
          kind: "pre_a",
        });
      }
      if (pos.medi?.pre_a != null) {
        const postCode = (writtenUnits.A.medi as Record<string, number>).post_b;
        medi.push({
          parts: [
            { text: niText("init"), blue: true, isNi: true },
            { text: String.fromCodePoint(pos.medi.pre_a), blue: false },
            { text: String.fromCodePoint(postCode), blue: true },
            { text: niText("fina"), blue: true, isNi: true },
          ],
          kind: "pre_a",
        });
      }

      // pre_o — use unit's own pre_o variant
      if (pos.init?.pre_o != null) {
        const postCode = (writtenUnits[uid === "Gp" || uid === "Kp" ? "Ob" : "O"].medi as Record<string, number>).post_b;
        init.push({
          parts: [
            { text: String.fromCodePoint(pos.init.pre_o), blue: false },
            { text: String.fromCodePoint(postCode), blue: true },
            { text: niText("fina"), blue: true, isNi: true },
          ],
          kind: "pre_o",
        });
      }
      if (pos.medi?.pre_o != null) {
        const postCode = (writtenUnits[uid === "Gp" || uid === "Kp" ? "Ob" : "O"].medi as Record<string, number>).post_b;
        medi.push({
          parts: [
            { text: niText("init"), blue: true, isNi: true },
            { text: String.fromCodePoint(pos.medi.pre_o), blue: false },
            { text: String.fromCodePoint(postCode), blue: true },
            { text: niText("fina"), blue: true, isNi: true },
          ],
          kind: "pre_o",
        });
      }

      // pre_i — use unit's own pre_i variant
      if (pos.init?.pre_i != null) {
        const postCode = (writtenUnits.I.medi as Record<string, number>).post_b;
        init.push({
          parts: [
            { text: String.fromCodePoint(pos.init.pre_i), blue: false },
            { text: String.fromCodePoint(postCode), blue: true },
            { text: niText("fina"), blue: true, isNi: true },
          ],
          kind: "pre_i",
        });
      }
      if (pos.medi?.pre_i != null) {
        const postCode = (writtenUnits.I.medi as Record<string, number>).post_b;
        medi.push({
          parts: [
            { text: niText("init"), blue: true, isNi: true },
            { text: String.fromCodePoint(pos.medi.pre_i), blue: false },
            { text: String.fromCodePoint(postCode), blue: true },
            { text: niText("fina"), blue: true, isNi: true },
          ],
          kind: "pre_i",
        });
      }

      // post_w — Ni + Wp.medi + unit's own post_w
      if (pos.init?.post_w != null) {
        init.push({
          parts: [
            { text: niText("init"), blue: true, isNi: true },
            { text: String.fromCodePoint(writtenUnits.Wp.medi.code), blue: true },
            { text: String.fromCodePoint(pos.init.post_w), blue: false },
          ],
          kind: "post_w",
        });
      }
      if (pos.medi?.post_w != null) {
        medi.push({
          parts: [
            { text: niText("init"), blue: true, isNi: true },
            { text: String.fromCodePoint(writtenUnits.Wp.medi.code), blue: true },
            { text: String.fromCodePoint(pos.medi.post_w), blue: false },
          ],
          kind: "post_w",
        });
      }
      if (pos.fina?.post_w != null) {
        fina.push({
          parts: [
            { text: niText("init"), blue: true, isNi: true },
            { text: String.fromCodePoint(writtenUnits.Wp.medi.code), blue: true },
            { text: String.fromCodePoint(pos.fina.post_w), blue: false },
          ],
          kind: "post_w",
        });
      }

      if (init.length || medi.length || fina.length) {
        map.set(uid, { init, medi, fina });
      }
    }
    return map;
  });
</script>

<table class="written-units">
  <colgroup>
    <col class="unit" />
    <col class="variant" />
    <col class="variant" />
    <col class="variant" />
    <col class="variant" />
    <col class="ligature" />
    <col class="ligature" />
    <col class="ligature" />
  </colgroup>
  <thead>
    <tr><th rowspan="2">ID</th><th colspan="4">Variants</th><th colspan="3">Ligated Variants</th></tr>
    <tr>
      {#each joiningPositions as p}<th>{p}</th>{/each}
      <th>init</th><th>medi</th><th>fina</th>
    </tr>
  </thead>
  <tbody>
    {#each Object.keys(writtenUnits) as id}
      {@const positionToLetters = positionsOf(id as WrittenUnitID)}
      {@const lig = unitToLigature.get(id as WrittenUnitID)}
      {#if positionToLetters}
        <tr>
          <td {id}>{id}</td>
          {#each joiningPositions as position}
            {@const localeToLetters = positionToLetters.get(position)}
            <td id="{id}-{position}" class={{ variant: true, undefined: !localeToLetters }}>
              {#if localeToLetters}
                {#if unified}
                  <span class="locale-label">{[...localeToLetters.keys()].join(" ")}</span>
                {/if}
                <LetterVariant id={id as WrittenUnitID} {position} />
              {/if}
            </td>
          {/each}
          {#each ["init", "medi", "fina"] as lp}
            {@const col = lig?.[lp as "init" | "medi" | "fina"]?.filter((r) => r.kind !== "post_w" || localesToShow.includes("MNGx"))}
            <td class={{ lig: true, undefined: !col?.length || !positionToLetters.has(lp as JoiningPosition) }}>
              {#if col && positionToLetters.has(lp as JoiningPosition)}
                {#each col as row, i}
                  {#if i > 0}<br />{/if}
                  <span class="wu">
                    {#each row.parts as part}
                      <span class={part.blue ? (part.isNi ? "lig-blue" : "lig-gray") : ""}>{part.text}</span>
                    {/each}
                  </span>
                {/each}
              {/if}
            </td>
          {/each}
        </tr>
      {/if}
    {/each}
  </tbody>
</table>

<style>
  td,
  th {
    text-align: center !important;
    vertical-align: middle;
  }
  td.variant {
    vertical-align: top;
  }
  td.lig {
    vertical-align: middle;
    font-size: 40px;
    line-height: 1;
  }
  .lig-blue {
    color: hsl(210 80% 58% / 0.55);
  }
  td.undefined {
    background-color: whitesmoke;
  }
  td:target {
    background-color: yellow;
  }
  td:first-child {
    width: 2rem;
  }
  td:not(:first-child) {
    width: 4rem;
  }
</style>

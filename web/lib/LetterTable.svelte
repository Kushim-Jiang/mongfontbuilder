<script lang="ts">
  interface Props {
    locale: LocaleID;
  }
  let { locale }: Props = $props();

  import type { LocaleID } from "../../data/locales";
  import type { JoiningPosition } from "../../data/misc";
  import type { FVS, VariantData } from "../../data/variants";
  import type { WrittenUnitID } from "../../data/writtenUnits";
  import { joiningPositions } from "../../data/misc";
  import { variants } from "../../data/variants";
  import { aliases } from "../../data/aliases";
  import LetterVariant from "./LetterVariant.svelte";
  import { hexFromCP, nameToCP } from "./utils";
  import { localeNS, orderedAliases, resolveCharName, mapGetOrCreate, isVariantRef, sortedFVSKeys } from "./utils";

  type LocalizedVariant = { written: VariantData["written"]; resolvedWritten?: WrittenUnitID[]; archaic: boolean; unrecommended: boolean };
  const localeNamespace = $derived(localeNS(locale));

  const charNameToPositionToFVSToLocalizedVariant = $derived.by(() => {
    const _orderedAliases = orderedAliases(locale);
    const _localeNamespace = localeNS(locale);
    const map = new Map<string, Map<JoiningPosition, Map<FVS, LocalizedVariant>>>();

    for (const alias of _orderedAliases) {
      const charName = resolveCharName(alias, _localeNamespace);
      if (!charName) continue;
      const positionToFVSToVariant = variants[charName];
      for (const position of joiningPositions) {
        for (const [fvs, variant] of Object.entries(positionToFVSToVariant[position])) {
          const variantLocaleData = variant.locales[locale];
          if (!variantLocaleData) continue;
          const positionToFVSToData = mapGetOrCreate(map, charName, () => new Map());
          const fvsToData = mapGetOrCreate(positionToFVSToData, position, () => new Map());
          fvsToData.set(Number(fvs) as FVS, {
            written: variantLocaleData.written ?? variant.written,
            archaic: variantLocaleData.archaic ?? false,
            unrecommended: variantLocaleData.unrecommended ?? false,
          });
        }
      }
    }
    // Resolve VariantReferences
    for (const positionToFVSToData of map.values()) {
      for (const fvsToData of positionToFVSToData.values()) {
        for (const data of fvsToData.values()) {
          if (isVariantRef(data.written)) {
            const [refPos, refFvs] = data.written as unknown as [JoiningPosition, FVS];
            const refData = positionToFVSToData.get(refPos)?.get(refFvs);
            if (refData) {
              if (isVariantRef(refData.written)) {
                const [r2Pos, r2Fvs] = refData.written as unknown as [JoiningPosition, FVS];
                const r2 = positionToFVSToData.get(r2Pos)?.get(r2Fvs);
                if (r2 && !isVariantRef(r2.written)) data.resolvedWritten = r2.written as WrittenUnitID[];
              } else {
                data.resolvedWritten = refData.written as WrittenUnitID[];
              }
            }
          }
        }
      }
    }
    return map;
  });
</script>

<table>
  <thead>
    <tr><th rowspan="2">Letter</th><th rowspan="2">FVS</th><th colspan="4">Variants</th></tr>
    <tr
      >{#each joiningPositions as p}<th>{p}</th>{/each}</tr
    >
  </thead>
  <tbody>
    {#each charNameToPositionToFVSToLocalizedVariant as [charName, positionToFVSToLocalizedVariant]}
      {@const codePoint = nameToCP.get(charName)!}
      {@const hex = hexFromCP(codePoint)}
      {@const char = String.fromCodePoint(codePoint)}
      {@const aliasData = aliases[charName]}
      {@const alias = typeof aliasData === "object" ? aliasData[localeNamespace] : aliasData}
      {@const rowspan = new Set([...positionToFVSToLocalizedVariant.values()].flatMap((m) => [...m.keys()])).size}
      <tr>
        <td id={alias} {rowspan} title="U+{hex} {char} {charName}">{hex}<br />{char} <i>{alias}</i></td>
        {@render variantCells(charName, positionToFVSToLocalizedVariant, 0, alias)}
      </tr>
      {#each sortedFVSKeys(positionToFVSToLocalizedVariant) as fvs}
        <tr>{@render variantCells(charName, positionToFVSToLocalizedVariant, fvs, alias)}</tr>
      {/each}
    {/each}
  </tbody>
</table>

{#snippet variantCells(charName: string, positionToFVSToLocalizedVariant: Map<JoiningPosition, Map<FVS, LocalizedVariant>>, fvs: FVS, alias: string)}
  <td>{fvs || "-"}</td>
  {#each positionToFVSToLocalizedVariant as [position, fvsToLocalizedVariant]}
    {@const variant = fvsToLocalizedVariant.get(fvs)}
    {@const fabricated = variant ? isVariantRef(variant.written) : false}
    <td id={`${alias}-${position}-${fvs}`} class={{ variant: true, undefined: !variant, fabricated: fabricated, archaic: variant?.archaic, unrecommended: variant?.unrecommended }}>
      {#if variant}
        {#if fabricated}
          {@const refPos = (variant.written as [JoiningPosition, FVS])[0]}
          <span><LetterVariant {charName} position={refPos} {fvs} written={variant.resolvedWritten} /></span><br />
          → {variant.written.join(" ")}
        {:else}
          <span><LetterVariant {charName} {position} {fvs} written={variant.resolvedWritten ?? (variant.written as WrittenUnitID[])} /></span><br />
          {#each variant.written as unit, index}{index ? " " : ""}<a href="#{unit}">{unit}</a>{/each}
        {/if}
      {/if}
    </td>
  {/each}
{/snippet}

<style>
  td,
  th {
    text-align: center !important;
    vertical-align: middle;
  }
  td.variant span {
    font-size: 3em;
    line-height: 1;
  }
  td.fabricated,
  td.undefined {
    background-color: whitesmoke;
  }
  td.archaic {
    background-color: beige;
  }
  td.unrecommended {
    background-color: pink;
  }
  td:target {
    background-color: yellow;
  }
  td a {
    text-decoration: none;
  }
  td:nth-child(-n + 2) {
    width: 2rem;
  }
  td:nth-child(n + 3) {
    width: 4rem;
  }
</style>

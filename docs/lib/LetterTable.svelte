<script lang="ts">
  interface Props {
    locale: LocaleID;
  }

  let { locale }: Props = $props();

  import { aliases, type LocaleNamespace } from "../../data/aliases";
  import { locales, type LocaleID } from "../../data/locales";
  import { joiningPositions, type JoiningPosition } from "../../data/misc";
  import { variants, type FVS, type VariantData } from "../../data/variants";

  import LetterVariant from "./LetterVariant.svelte";
  import { hexFromCP, nameToCP } from "./utils";

  type LocalizedVariant = { written: VariantData["written"]; archaic: boolean };
  const charNameToPositionToFVSToLocalizedVariant = new Map<string, Map<JoiningPosition, Map<FVS, LocalizedVariant>>>();

  const localeNamespace = locale.slice(0, 3) as LocaleNamespace;
  const orderedAlias = [...locales[locale].categories.vowel, ...locales[locale].categories.consonant];
  let charName = "";
  for (const alias of orderedAlias) {
    for (const [charName_, localeToAlias] of Object.entries(aliases)) {
      // @ts-ignore
      if (localeToAlias[localeNamespace] === alias) {
        charName = charName_;
        break;
      }
    }
    const positionToFVSToVariant = variants[charName];
    for (const position of joiningPositions) {
      for (const [fvs, variant] of Object.entries(positionToFVSToVariant[position])) {
        const variantLocaleData = variant.locales[locale];
        if (!variantLocaleData) {
          continue;
        }
        let positionToFVSToData = charNameToPositionToFVSToLocalizedVariant.get(charName);
        if (!positionToFVSToData) {
          positionToFVSToData = new Map();
          charNameToPositionToFVSToLocalizedVariant.set(charName, positionToFVSToData);
        }
        let fvsToData = positionToFVSToData.get(position);
        if (!fvsToData) {
          fvsToData = new Map();
          positionToFVSToData.set(position, fvsToData);
        }
        fvsToData.set(Number(fvs) as FVS, {
          written: variantLocaleData.written ?? variant.written,
          archaic: variantLocaleData.archaic ?? false,
        });
      }
    }
  }
</script>

{#snippet variantCells(charName: string, positionToFVSToLocalizedVariant: Map<JoiningPosition, Map<FVS, LocalizedVariant>>, fvs: FVS)}
  <td>{fvs || "-"}</td>
  {#each positionToFVSToLocalizedVariant as [position, fvsToLocalizedVariant]}
    {@const variant = fvsToLocalizedVariant.get(fvs)}
    <td
      class={{
        variant: true,
        undefined: !variant,
        // @ts-ignore
        fabricated: joiningPositions.includes(variant?.written[0]),
        archaic: variant?.archaic,
      }}
    >
      {#if variant}
        <span><LetterVariant {charName} {position} {fvs} /></span><br />
        {variant.written}
      {/if}
    </td>
  {/each}
{/snippet}

<table>
  <thead>
    <tr>
      <th rowspan="2">Code point</th>
      <th rowspan="2">Alias</th>
      <th rowspan="2">FVS</th>
      <th colspan="4">Variants</th>
    </tr>
    <tr>
      {#each joiningPositions as position}
        <th>{position}</th>
      {/each}
    </tr>
  </thead>
  <tbody>
    {#each charNameToPositionToFVSToLocalizedVariant as [charName, positionToFVSToLocalizedVariant]}
      {@const alias = aliases[charName]}
      {@const rowspan = Math.max(...[...positionToFVSToLocalizedVariant.values()].map((i) => i.size))}
      {@const fvs = 0}
      <tr>
        <td {rowspan} title={charName}>{hexFromCP(nameToCP.get(charName)!)}</td>
        <td {rowspan}><i>{typeof alias == "object" ? alias[localeNamespace] : alias}</i></td>
        {@render variantCells(charName, positionToFVSToLocalizedVariant, fvs)}
      </tr>
      {#each { length: rowspan - 1 }, index}
        {@const fvs = (index + 1) as FVS}
        <tr>
          {@render variantCells(charName, positionToFVSToLocalizedVariant, fvs)}
        </tr>
      {/each}
    {/each}
  </tbody>
</table>

<style>
  td,
  th {
    text-align: center !important;
    vertical-align: middle;
  }
  td.variant span {
    font-size: 2em;
  }
  td.fabricated,
  td.undefined {
    background-color: whitesmoke;
  }
  td.archaic {
    background-color: beige;
  }
</style>

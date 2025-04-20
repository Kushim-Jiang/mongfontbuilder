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

  type LocalizedVariant = { written: VariantData["written"]; archaic: boolean; unrecommended: boolean };
  const charNameToPositionToFVSToLocalizedVariant = new Map<string, Map<JoiningPosition, Map<FVS, LocalizedVariant>>>();

  const localeNamespace = locale.slice(0, 3) as LocaleNamespace;
  const orderedAliases = [...locales[locale].categories.vowel, ...locales[locale].categories.consonant];

  let charName = "";
  for (const alias of orderedAliases) {
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
          unrecommended: variantLocaleData.unrecommended ?? false,
        });
      }
    }
  }

  function getSortedFVSKeys(positionToFVSToLocalizedVariant: Map<JoiningPosition, Map<FVS, LocalizedVariant>>): FVS[] {
    return [...new Set([...positionToFVSToLocalizedVariant.values()].flatMap((i) => [...i.keys()]))].filter((fvs) => fvs !== 0).sort((a, b) => a - b);
  }
</script>

<table>
  <thead>
    <tr>
      <th rowspan="2">Letter</th>
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
      {@const codePoint = nameToCP.get(charName)!}
      {@const hex = hexFromCP(codePoint)}
      {@const char = String.fromCodePoint(codePoint)}
      {@const aliasData = aliases[charName]}
      {@const alias = typeof aliasData == "object" ? aliasData[localeNamespace] : aliasData}
      {@const rowspan = new Set([...positionToFVSToLocalizedVariant.values()].flatMap((i) => [...i.keys()])).size}
      {@const fvs = 0}
      <tr>
        <td id={alias} {rowspan} title="U+{hex} {char} {charName}">
          {hex}<br />
          {char} <i>{alias}</i>
        </td>
        {@render variantCells(charName, positionToFVSToLocalizedVariant, fvs)}
      </tr>
      {#each getSortedFVSKeys(positionToFVSToLocalizedVariant) as fvs}
        <tr>
          {@render variantCells(charName, positionToFVSToLocalizedVariant, fvs)}
        </tr>
      {/each}
    {/each}
  </tbody>
</table>

{#snippet variantCells(charName: string, positionToFVSToLocalizedVariant: Map<JoiningPosition, Map<FVS, LocalizedVariant>>, fvs: FVS)}
  <td>{fvs || "-"}</td>
  {#each positionToFVSToLocalizedVariant as [position, fvsToLocalizedVariant]}
    {@const variant = fvsToLocalizedVariant.get(fvs)}
    {@const fabricated = joiningPositions.includes(variant?.written[0] as any)}
    <td
      class={{
        variant: true,
        undefined: !variant,
        fabricated,
        archaic: variant?.archaic,
        unrecommended: variant?.unrecommended,
      }}
    >
      {#if variant}
        <span><LetterVariant {charName} {position} {fvs} /></span><br />
        {#if fabricated}
          → {variant.written.join(" ")}
        {:else}
          {#each variant.written as unit, index}
            {index ? " " : ""}
            <a href="#{unit}">{unit}</a>
          {/each}
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
    font-size: 2em;
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
</style>

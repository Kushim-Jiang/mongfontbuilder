<script lang="ts">
  interface Props {
    locale: LocaleID;
  }

  let { locale }: Props = $props();

  import { aliases, type LocaleNamespace } from "../../data/aliases";
  import { locales, type LocaleID } from "../../data/locales";
  import { joiningPositions, type JoiningPosition } from "../../data/misc";
  import { variants, type FVS } from "../../data/variants";

  import LetterVariant from "./LetterVariant.svelte";
  import { hexFromCP, nameToCP } from "./utils";

  const charNameToPositionToFVSToLocalizedVariant = new Map<string, Map<JoiningPosition, Map<FVS, { fabricated: boolean; archaic: boolean }>>>();

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
          // @ts-ignore
          fabricated: joiningPositions.includes((variantLocaleData.written ?? variant.written)[0]),
          archaic: variantLocaleData.archaic ?? false,
        });
      }
    }
  }
</script>

<table>
  <thead>
    <tr>
      <th rowspan="2">Code point</th>
      <th rowspan="2">Alias</th>
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
      <tr>
        <td title={charName}>{hexFromCP(nameToCP.get(charName)!)}</td>
        <td><i>{typeof alias == "object" ? alias[localeNamespace] : alias}</i></td>
        {#each positionToFVSToLocalizedVariant as [position, fvsToLocalizedVariant]}
          <td>
            {#each fvsToLocalizedVariant as [fvs, { fabricated, archaic }], index}
              {#if index}
                <br />
              {/if}
              <span class={{ fabricated, archaic }}>
                <LetterVariant {charName} {position} {fvs} />
              </span>
            {/each}
          </td>
        {/each}
      </tr>
    {/each}
  </tbody>
</table>

<style>
  span.fabricated {
    color: lightgray;
  }
  span.archaic {
    background-color: yellow;
  }
</style>

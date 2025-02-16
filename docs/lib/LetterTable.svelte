<script lang="ts">
  interface Props {
    locale: LocaleID;
  }

  let { locale }: Props = $props();

  import type { LocaleID } from "../../data/locales";
  import { aliases, type LocaleNamespace } from "../../data/aliases";
  import { joiningPositions, type JoiningPosition } from "../../data/misc";
  import { variants, type FVS } from "../../data/variants";

  import LetterVariant from "./LetterVariant.svelte";
  import { nameToCP, hexFromCP } from "./utils";

  const localizedVariants = new Map<string, Map<JoiningPosition, Map<FVS, { fabricated: boolean; archaic: boolean }>>>();
  for (const [charName, positionToFVSToVariant] of Object.entries(variants)) {
    for (const position of joiningPositions) {
      for (const [fvs, variant] of Object.entries(positionToFVSToVariant[position])) {
        const variantLocaleData = variant.locales[locale];
        if (variantLocaleData) {
          let positionToFVSToData = localizedVariants.get(charName);
          if (!positionToFVSToData) {
            positionToFVSToData = new Map();
            localizedVariants.set(charName, positionToFVSToData);
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
  }
</script>

<table>
  <thead>
    <tr>
      <th rowspan="2">Code point</th>
      <th rowspan="2">Alias</th>
      <th colspan="4">Joining positions</th>
    </tr>
    <tr>
      {#each joiningPositions as position}
        <th>{position}</th>
      {/each}
    </tr>
  </thead>
  <tbody>
    {#each localizedVariants as [charName, positionToFVSToLocalizedVariant]}
      {@const alias = aliases[charName]}
      <tr>
        <td title={charName}>{hexFromCP(nameToCP.get(charName)!)}</td>
        <td>{typeof alias == "object" ? alias[locale.slice(0, 3) as LocaleNamespace] : alias}</td>
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

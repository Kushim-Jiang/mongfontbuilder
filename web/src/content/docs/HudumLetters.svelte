<script lang="ts">
  import type { LocaleID } from "../../../../data/locales";
  import { aliases } from "../../../../data/aliases";
  import { joiningPositions, type JoiningPosition } from "../../../../data/misc";
  import { variants, type FVS } from "../../../../data/variants";

  import LetterVariant from "../../components/LetterVariant.svelte";
  import { nameToCP, hexFromCP } from "../../components/utils";

  const locale: LocaleID = "MNG";

  const charNameToPositionToFVSes = new Map<string, Map<JoiningPosition, FVS[]>>();
  for (const [charName, positionToFVSToVariant] of Object.entries(variants)) {
    for (const position of joiningPositions) {
      for (const [fvs, variant] of Object.entries(positionToFVSToVariant[position])) {
        const variantLocaleData = variant.locales[locale];
        if (variantLocaleData) {
          let positionToFVSes = charNameToPositionToFVSes.get(charName);
          if (!positionToFVSes) {
            positionToFVSes = new Map();
            charNameToPositionToFVSes.set(charName, positionToFVSes);
          }
          let fvses = positionToFVSes.get(position);
          if (!fvses) {
            fvses = [];
            positionToFVSes.set(position, fvses);
          }
          fvses.push(Number(fvs) as FVS);
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
      <th colspan="4">Positional forms</th>
    </tr>
    <tr>
      {#each joiningPositions as position}
        <th>{position}</th>
      {/each}
    </tr>
  </thead>
  <tbody>
    {#each charNameToPositionToFVSes as [charName, positionToFVSes]}
      {@const alias = aliases[charName]}
      <tr>
        <td title={charName}>{hexFromCP(nameToCP.get(charName)!)}</td>
        <td>{typeof alias == "object" ? alias[locale] : alias}</td>
        {#each positionToFVSes as [position, fvses]}
          <td>
            {#each fvses as fvs, index}
              {#if index}
                <br />
              {/if}
              <LetterVariant {charName} {position} {fvs} />
            {/each}
          </td>
        {/each}
      </tr>
    {/each}
  </tbody>
</table>

<script lang="ts">
  import type { LocaleID } from "../../../../data/locales";
  import { aliases } from "../../../../data/aliases";
  import { joiningPositions, type JoiningPosition, type WrittenUnitID } from "../../../../data/writtenUnits";
  import { variants } from "../../../../data/variants";
  import Glyph from "../../components/Glyph.svelte";
  import { nameToCP, hexFromCP } from "../../components/utils";

  const locale: LocaleID = "MNG";

  const charNameToPositionToWrittenUnits = new Map<string, Map<JoiningPosition, WrittenUnitID[]>>();
  for (const [charName, positionToFVSToVariant] of Object.entries(variants)) {
    for (const position of joiningPositions) {
      for (const [fvs, variant] of Object.entries(positionToFVSToVariant[position])) {
        const variantLocaleData = variant.locales[locale];
        if (variantLocaleData) {
          let positionToWrittenUnits = charNameToPositionToWrittenUnits.get(charName);
          if (!positionToWrittenUnits) {
            positionToWrittenUnits = new Map();
            charNameToPositionToWrittenUnits.set(charName, positionToWrittenUnits);
          }
          if (joiningPositions.includes(variant.written[0] as any)) {
            continue;
          }
          positionToWrittenUnits.set(position, variant.written as WrittenUnitID[]);
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
    {#each Object.entries(variants) as [charName, positionToFVSToVariant]}
      <tr>
        <td title={charName}>{hexFromCP(nameToCP.get(charName)!)}</td>
        <td>{aliases[charName][locale]}</td>
        {#each joiningPositions as position}
          <td> </td>
        {/each}
      </tr>
    {/each}
  </tbody>
</table>

<script lang="ts">
  interface Props {
    locale: LocaleID;
  }

  let { locale }: Props = $props();

  import { writtenUnits, type WrittenUnitID } from "../../data/writtenUnits";
  import type { LocaleID } from "../../data/locales";
  import { variants } from "../../data/variants";
  import { joiningPositions, type JoiningPosition } from "../../data/misc";

  import WrittenUnitVariant from "./WrittenUnitVariant.svelte";

  const unitToPositions = new Map<WrittenUnitID, Set<JoiningPosition>>();
  for (const positionToFVSToVariant of Object.values(variants)) {
    for (const [position, fvsToVariant] of Object.entries(positionToFVSToVariant)) {
      for (const variant of Object.values(fvsToVariant)) {
        const localeData = variant.locales[locale];
        if (!localeData) {
          continue;
        }
        const written = localeData.written ?? variant.written;
        // @ts-ignore
        if (joiningPositions.includes(written[0])) {
          continue;
        }
        for (const [index, unit] of (written as WrittenUnitID[]).entries()) {
          let positions = unitToPositions.get(unit);
          if (!positions) {
            positions = new Set();
            unitToPositions.set(unit, positions);
          }
          if (written.length == 1) {
            positions.add(position as JoiningPosition);
          } else if (["isol", "init"].includes(position) && index == 0) {
            positions.add("init");
          } else if (["isol", "fina"].includes(position) && index == written.length - 1) {
            positions.add("fina");
          } else {
            positions.add("medi");
          }
        }
      }
    }
  }
</script>

<table>
  <thead>
    <tr>
      <th rowspan="2">ID</th>
      <th colspan="4">Joining positions</th>
    </tr>
    <tr>
      {#each joiningPositions as position}
        <th>{position}</th>
      {/each}
    </tr>
  </thead>
  <tbody>
    {#each writtenUnits.filter((i) => unitToPositions.has(i)) as id}
      <tr>
        <td>{id}</td>
        {#each joiningPositions as position}
          <td>
            {#if unitToPositions.get(id)!.has(position)}
              <WrittenUnitVariant {id} {position} />
            {/if}
          </td>
        {/each}
      </tr>
    {/each}
  </tbody>
</table>

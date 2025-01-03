<script>
  import { writtenUnits } from "../../../../data/writtenUnits";
  import { joiningPositions } from "../../../../data/misc";
  import WrittenUnitVariant from "../../components/WrittenUnitVariant.svelte";
</script>

<table>
  <thead>
    <tr>
      <th rowspan="2">Written unit</th>
      <th colspan="4">Positional forms</th>
    </tr>
    <tr>
      {#each joiningPositions as position}
        <th>{position}</th>
      {/each}
    </tr>
  </thead>
  <tbody>
    {#each Object.entries(writtenUnits) as [id, positions]}
      <tr>
        <td>{id}</td>
        {#each joiningPositions as position}
          <td>
            {#if position in positions}
              <WrittenUnitVariant {id} {position} />
            {/if}
          </td>
        {/each}
      </tr>
    {/each}
  </tbody>
</table>

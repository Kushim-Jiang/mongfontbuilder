<script>
  import { joiningPositions, writtenUnits } from "../../../../data/writtenUnits";
  import Glyph from "../../components/Glyph.svelte";
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
              <Glyph written={[id]} {position} />
            {/if}
          </td>
        {/each}
      </tr>
    {/each}
  </tbody>
</table>

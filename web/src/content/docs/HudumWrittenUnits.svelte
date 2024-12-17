<script>
  import { joiningPositions } from "../../../../data";
  import { writtenUnits } from "../../../../data/writtenUnits";
  import Glyph from "../../components/Glyph.svelte";
</script>

<table>
  <thead>
    <tr>
      <th>Written unit</th>
      <th colspan="4">Positional forms: {joiningPositions.join(", ")}</th>
    </tr>
  </thead>
  <tbody>
    {#each Object.keys(writtenUnits) as id}
      <tr>
        <td>{id}</td>
        {#each joiningPositions as position}
          <td>
            <Glyph written={id} {position} />
          </td>
        {/each}
      </tr>
    {/each}
  </tbody>
</table>

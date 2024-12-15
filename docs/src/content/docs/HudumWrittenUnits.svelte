<script>
  import { joiningPositions, writtenUnits } from "../../../data";
  import Glyph from "../../components/Glyph.svelte";
</script>

<Glyph written="A" position="isol" />
<Glyph written="A" position="init" />
<Glyph written="A" position="medi" />
<Glyph written="A" position="fina" />

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

<script lang="ts">
  import { joiningPositions, writtenUnits, type WrittenUnitID, type WrittenUnitVariant } from "../../data";

  const writtenUnitToVariants = new Map<WrittenUnitID, (WrittenUnitVariant | undefined)[]>();
  for (const [id, writtenUnit] of Object.entries(writtenUnits)) {
    writtenUnitToVariants.set(
      id as WrittenUnitID,
      joiningPositions.map((i) => writtenUnit[i as keyof typeof writtenUnit]),
    );
  }
</script>

<h2>
  <span lang="en">Hudum writing system</span>
  <span lang="zh">传统蒙古文</span>
</h2>

<table>
  <thead>
    <tr>
      <th>ID</th>
      <th colspan="4">Positional variants</th>
      <th>Notes</th>
    </tr>
  </thead>
  <tbody>
    {#each writtenUnitToVariants as [id, variants]}
      <tr>
        <td><code>{id}</code></td>
        {#each variants as variant}
          <td>
            {variant?.archaic}
          </td>
        {/each}
      </tr>
    {/each}
  </tbody>
</table>

<script lang="ts">
  interface Props {
    id: WrittenUnitID;
    position: JoiningPosition;
  }

  let { id, position }: Props = $props();

  import { joiningPositions, type JoiningPosition, type WrittenUnitID } from "../../../data/writtenUnits";
  import { variants, type FVS } from "../../../data/variants";

  import LetterVariant from "./LetterVariant.svelte";

  let result = $derived.by(() => {
    for (const [charName, positionToFVSToVariant] of Object.entries(variants)) {
      for (const [fvs, { written: _written }] of Object.entries(positionToFVSToVariant[position])) {
        if (joiningPositions.includes(_written[0] as any)) {
          continue;
        }
        if (_written.length == 1 && _written[0] == id) {
          return {
            charName,
            fvs: Number(fvs) as FVS,
          };
        }
      }
    }
  });
</script>

{#if result}
  <LetterVariant {position} {...result} />
{:else}
  ?
{/if}

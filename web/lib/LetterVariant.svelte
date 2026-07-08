<script lang="ts">
  interface Props {
    position: JoiningPosition;
    id?: WrittenUnitID;
    written?: WrittenUnitID[];
    charName?: string;
    fvs?: FVS;
    aliases?: string[];
  }

  let { position, id, written, charName, fvs, aliases = [] }: Props = $props();

  import type { JoiningPosition } from "../../data/misc";
  import type { FVS } from "../../data/variants";
  import type { WrittenUnitID } from "../../data/writtenUnits";
  import { nameToCP, buildWrittenText, niruguText, ctxBefore, ctxAfter } from "./utils";

  const units = $derived(id ? [id] : written);
  const showBefore = $derived(ctxBefore(position));
  const showAfter = $derived(ctxAfter(position));

  let text = $derived.by(() => {
    if (units) return buildWrittenText(units, position);
    if (charName) {
      let t = String.fromCodePoint(nameToCP.get(charName)!);
      if (fvs) t += ["\u{180B}", "\u{180C}", "\u{180D}", "\u{180F}"][fvs - 1];
      return t;
    }
    return "?";
  });
</script>

<span class="wu"
  >{#if showBefore}<span class="wu-context">{niruguText}</span>{/if}{text}{#if showAfter}<span class="wu-context">{niruguText}</span>{/if}</span
>
{#if aliases.length}
  <br />
  <i>
    {#each aliases as a, i}
      {i ? " " : ""}<a href="#{a}">{a}</a>
    {/each}
  </i>
{/if}

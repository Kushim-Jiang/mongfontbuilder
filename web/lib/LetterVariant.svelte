<script lang="ts">
  interface Props {
    charName: string;
    position: JoiningPosition;
    fvs: FVS;
  }

  let { charName, position, fvs }: Props = $props();

  import type { JoiningPosition } from "../../data/misc";
  import type { FVS } from "../../data/variants";

  import { nameToCP } from "./utils";

  const zwj = "\u{200D}";
  const nirugu = "\u{180A}";

  let text = $derived.by(() => {
    let text = String.fromCodePoint(nameToCP.get(charName)!);
    if (fvs) {
      text += ["\u{180B}", "\u{180C}", "\u{180D}", "\u{180F}"][Number(fvs) - 1];
    }
    if (position == "init" || position == "medi") {
      text = text + zwj;
    }
    if (position == "medi" || position == "fina") {
      text = zwj + text; // ZWJ may be segmented into a separate OTL run
    }
    return text;
  });
</script>

<span class="variant">
  {#if text.startsWith(zwj)}
    <span class="context">{nirugu}</span>
  {/if}{text ?? "?"}{#if text.endsWith(zwj)}
    <span class="context">{nirugu}</span>
  {/if}
</span>

<style>
  @font-face {
    font-family: "Noto Sans Mongolian Customized";
    src: url("/DraftNew-Regular.otf");
    font-weight: normal;
    font-style: normal;
  }

  span.variant {
    font-family: "Noto Sans Mongolian Customized";
    color: black;
  }
  span.context {
    color: hsl(0 0 0 / 0.25);
  }
</style>

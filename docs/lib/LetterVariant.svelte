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

  let text = $derived.by(() => {
    let text = String.fromCodePoint(nameToCP.get(charName)!);
    if (fvs) {
      text += ["\u{180B}", "\u{180C}", "\u{180D}", "\u{180F}"][Number(fvs) - 1];
    }
    if (position == "init" || position == "medi") {
      text += "\u{200D}";
    }
    if (position == "medi" || position == "fina") {
      text = "\u{200D}" + text; // ZWJ may be segmented into a separate OTL run
    }
    return text;
  });
</script>

<span>{text ?? "?"}</span>

<style>
  span {
    font-family: "Noto Sans Mongolian";
  }
</style>

<script lang="ts">
  interface Props {
    written: string[];
    position: JoiningPosition;
  }

  let { written, position }: Props = $props();

  import { joiningPositions, type JoiningPosition } from "../../../data/writtenUnits";
  import { variants } from "../../../data/variants";
  import { nameToCP } from "./utils";

  let text = $derived.by(() => {
    for (const [charName, positionToFVSToVariant] of Object.entries(variants)) {
      for (const [fvs, { written: _written }] of Object.entries(positionToFVSToVariant[position])) {
        if (joiningPositions.includes(_written[0] as any)) {
          continue;
        }
        if (_written.length == written.length && _written.every((e, i) => e == written[i])) {
          let text = String.fromCodePoint(nameToCP.get(charName)!);
          if (fvs != "0") {
            text += ["\u{180B}", "\u{180C}", "\u{180D}", "\u{180F}"][Number(fvs) - 1];
          }
          if (position == "init" || position == "medi") {
            text += "\u{200D}";
          }
          if (position == "medi" || position == "fina") {
            text = "\u{200D}" + text; // ZWJ may be segmented into a separate OTL run
          }
          return text;
        }
      }
    }
  });
</script>

<span>{text ?? "?"}</span>

<style>
  span {
    font-family: "Noto Sans Mongolian";
  }
</style>

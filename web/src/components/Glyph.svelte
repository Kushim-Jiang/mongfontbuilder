<script module>
  // @ts-ignore
  import _Names from "@unicode/unicode-16.0.0/Names";

  const Names: Map<number, string> = _Names;
  const nameToCP = new Map([...Names].filter(([_, v]) => !v.startsWith("<")).map(([k, v]) => [v, k]));
</script>

<script lang="ts">
  interface Props {
    written: string[];
    position: JoiningPosition;
  }

  let { written, position }: Props = $props();

  import { joiningPositions, type JoiningPosition } from "../../../data/writtenUnits";
  import { variants } from "../../../data/variants";

  let text = $derived.by(() => {
    for (const [name, positionToFVSToVariant] of Object.entries(variants)) {
      for (const [fvs, { written: _written }] of Object.entries(positionToFVSToVariant[position])) {
        if (joiningPositions.includes(_written[0] as any)) {
          continue;
        }
        if (_written.length == written.length && _written.every((e, i) => e == written[i])) {
          let text = String.fromCodePoint(nameToCP.get(name)!);
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

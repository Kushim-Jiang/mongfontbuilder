<script lang="ts">
  interface Props {
    /** A single written unit at the moment. */
    written: string;
    position: JoiningPosition;
  }

  let { written, position }: Props = $props();

  import type { JoiningPosition } from "../../../data";
  import { letters } from "../../../data/letters";

  let text = $derived.by(() => {
    for (const { cp, variants } of Object.values(letters)) {
      for (const [_position, _variants] of Object.entries(variants)) {
        if (_position == position) {
          for (const { writtenUnits, fvs } of _variants) {
            if (writtenUnits.length == 1 && writtenUnits[0] == written) {
              let text = String.fromCodePoint(cp);
              if (fvs) {
                text += ["\u{180B}", "\u{180C}", "\u{180D}", "\u{180F}"][fvs - 1];
              }
              if (position == "init" || position == "medi") {
                text += "\u{180A}";
              }
              if (position == "medi" || position == "fina") {
                text = "\u{180A}" + text; // ZWJ may be segmented into a separate OTL run
              }
              return text;
            }
          }
        }
      }
    }
  });
</script>

{text}

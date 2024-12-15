<script lang="ts">
  interface Props {
    /** A single written unit at the moment. */
    written: string;
    position: JoiningPosition;
  }

  import { letters, type JoiningPosition } from "../../data";

  let { written, position }: Props = $props();

  let text = "";
  for (const { cp, variants: positionToVariants } of Object.values(letters)) {
    for (const [_position, variants] of Object.entries(positionToVariants)) {
      if (_position == position) {
        for (const { writtenUnits, fvs } of variants) {
          if (writtenUnits.length == 1 && writtenUnits[0] == written) {
            text = String.fromCodePoint(cp);
            if (fvs) {
              text += ["\u{180B}", "\u{180C}", "\u{180D}", "\u{180F}"][fvs - 1];
            }
            if (position == "init" || position == "medi") {
              text = text + "\u{180A}";
            }
            if (position == "medi" || position == "fina") {
              text = "\u{180A}" + text; // ZWJ may be segmented into a separate OTL run
            }
            break;
          }
        }
      }
    }
  }
</script>

{text}

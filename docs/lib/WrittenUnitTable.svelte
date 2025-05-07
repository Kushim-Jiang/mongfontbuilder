<script lang="ts">
  interface Props {
    locale: LocaleID;
  }

  let { locale }: Props = $props();

  import { aliases, type LocaleNamespace } from "../../data/aliases";
  import { locales, type LocaleID } from "../../data/locales";
  import { joiningPositions, type JoiningPosition } from "../../data/misc";
  import { variants } from "../../data/variants";
  import { writtenUnits, type WrittenUnitID } from "../../data/writtenUnits";

  import WrittenUnitVariant from "./WrittenUnitVariant.svelte";

  const localeNamespace = locale.slice(0, 3) as LocaleNamespace;
  const orderedAliases = [...locales[locale].categories.vowel, ...locales[locale].categories.consonant];

  const unitToPositionToLetters = new Map<WrittenUnitID, Map<JoiningPosition, Set<string>>>();
  for (const [charName, positionToFVSToVariant] of Object.entries(variants)) {
    const aliasData = aliases[charName];
    const alias = typeof aliasData == "object" ? aliasData[localeNamespace] : aliasData;
    if (!alias) {
      continue;
    }
    for (const [position, fvsToVariant] of Object.entries(positionToFVSToVariant)) {
      for (const variant of Object.values(fvsToVariant)) {
        const localeData = variant.locales[locale];
        if (!localeData) {
          continue;
        }
        const written = localeData.written ?? variant.written;
        if (joiningPositions.includes(written[0] as any)) {
          continue;
        }
        for (const [index, unit] of (written as WrittenUnitID[]).entries()) {
          let positionToLetters = unitToPositionToLetters.get(unit);
          if (!positionToLetters) {
            positionToLetters = new Map();
            unitToPositionToLetters.set(unit, positionToLetters);
          }
          let _position: JoiningPosition;
          if (written.length == 1) {
            _position = position as JoiningPosition;
          } else if (["isol", "init"].includes(position) && index == 0) {
            _position = "init";
          } else if (["isol", "fina"].includes(position) && index == written.length - 1) {
            _position = "fina";
          } else {
            _position = "medi";
          }
          let letters = positionToLetters.get(_position);
          if (!letters) {
            letters = new Set();
            positionToLetters.set(_position, letters);
          }
          letters.add(alias);
        }
      }
    }
  }
</script>

<table>
  <thead>
    <tr>
      <th rowspan="2">ID</th>
      <th colspan="4">Variants</th>
    </tr>
    <tr>
      {#each joiningPositions as position}
        <th>{position}</th>
      {/each}
    </tr>
  </thead>
  <tbody>
    {#each writtenUnits as id}
      {@const positionToLetters = unitToPositionToLetters.get(id)}
      {#if positionToLetters}
        <tr>
          <td {id}>{id}</td>
          {#each joiningPositions as position}
            {@const letters = positionToLetters.get(position)}
            <td class={{ variant: true, undefined: !letters }}>
              {#if letters}
                <span><WrittenUnitVariant {id} {position} /></span><br />
                <i>
                  {#each orderedAliases.filter((i) => letters.has(i)) as letter, index}
                    {index ? " " : ""}
                    <a href="#{letter}">{letter}</a>
                  {/each}
                </i>
              {/if}
            </td>
          {/each}
        </tr>
      {/if}
    {/each}
  </tbody>
</table>

<style>
  td,
  th {
    text-align: center !important;
    vertical-align: middle;
  }
  td.variant span {
    font-size: 2em;
  }
  td.undefined {
    background-color: whitesmoke;
  }
  td:target {
    background-color: yellow;
  }
  td a {
    text-decoration: none;
  }
  td:first-child {
    width: 4vw;
  }
  td:not(:first-child) {
    width: 8vw;
  }
</style>

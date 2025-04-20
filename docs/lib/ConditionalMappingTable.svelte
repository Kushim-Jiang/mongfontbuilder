<script lang="ts">
  interface Props {
    locale: LocaleID;
  }

  let { locale }: Props = $props();

  import { aliases, type LocaleNamespace } from "../../data/aliases";
  import { locales, type ConditionalMappingType, type LocaleID } from "../../data/locales";
  import { joiningPositions, type JoiningPosition } from "../../data/misc";
  import { variants, type FVS } from "../../data/variants";

  import LetterVariant from "./LetterVariant.svelte";
  import { hexFromCP, nameToCP } from "./utils";

  const conditionOrder = locales[locale].conditions;

  const charNameToConditionToPositionToFVS = new Map<
    string,
    {
      default: Map<JoiningPosition, FVS>;
      conditions: Map<ConditionalMappingType, Map<JoiningPosition, FVS>>;
    }
  >();

  const localeNamespace = locale.slice(0, 3) as LocaleNamespace;
  const orderedAlias = [...locales[locale].categories.vowel, ...locales[locale].categories.consonant];
  let charName = "";
  for (const alias of orderedAlias) {
    for (const [charName_, localeToAlias] of Object.entries(aliases)) {
      // @ts-ignore
      if (localeToAlias[localeNamespace] === alias) {
        charName = charName_;
        break;
      }
    }
    const positionToFVSToVariant = variants[charName];
    for (const position of joiningPositions) {
      for (const [fvsKey, { default: default_, locales }] of Object.entries(positionToFVSToVariant[position])) {
        const variantLocaleData = locales[locale];
        if (!variantLocaleData) {
          continue;
        }
        const conditions = variantLocaleData.conditions ?? [];
        if (!default_ && !conditions.length) {
          continue;
        }
        let conditionToPositionToFVS = charNameToConditionToPositionToFVS.get(charName);
        if (!conditionToPositionToFVS) {
          conditionToPositionToFVS = { default: new Map(), conditions: new Map() };
          charNameToConditionToPositionToFVS.set(charName, conditionToPositionToFVS);
        }
        const fvs = Number(fvsKey) as FVS;
        if (default_) {
          conditionToPositionToFVS.default.set(position, fvs);
        }
        for (const condition of conditions) {
          let positionToFVS = conditionToPositionToFVS.conditions.get(condition);
          if (!positionToFVS) {
            positionToFVS = new Map();
            conditionToPositionToFVS.conditions.set(condition, positionToFVS);
          }
          positionToFVS.set(position, Number(fvsKey) as FVS);
        }
      }
    }
  }
</script>

<table>
  <thead>
    <tr>
      <th rowspan="2">Letter</th>
      <th rowspan="2">Mapping type</th>
      <th colspan="4">Variants</th>
    </tr>
    <tr>
      {#each joiningPositions as position}
        <th>{position}</th>
      {/each}
    </tr>
  </thead>
  <tbody>
    {#each charNameToConditionToPositionToFVS as [charName, { default: defaultPositionToFVS, conditions: conditionToPositionToFVS }]}
      {@const codePoint = nameToCP.get(charName)!}
      {@const hex = hexFromCP(codePoint)}
      {@const char = String.fromCodePoint(codePoint)}
      {@const aliasData = aliases[charName]}
      {@const alias = typeof aliasData == "object" ? aliasData[localeNamespace] : aliasData}
      <tr>
        <td rowspan={conditionToPositionToFVS.size + 1} title="U+{hex} {char} {charName}">
          <a href="#{alias}"
            >{hex}<br />
            {char} <i>{alias}</i></a
          >
        </td>
        <td class="default">default</td>
        {#each joiningPositions as position}
          <td class="default">
            <span><LetterVariant {charName} {position} fvs={defaultPositionToFVS.get(position)!} /></span>
          </td>
        {/each}
      </tr>
      {#each conditionOrder as condition}
        {@const positionToFVS = conditionToPositionToFVS.get(condition)}
        {#if positionToFVS}
          <tr>
            <td>{condition}</td>
            {#each joiningPositions as position}
              {@const fvs = positionToFVS.get(position)}
              <td class="variant">
                {#if fvs != undefined}
                  <span><LetterVariant {charName} {position} {fvs} /></span>
                {/if}
              </td>
            {/each}
          </tr>
        {/if}
      {/each}
    {/each}
  </tbody>
</table>

<style>
  td,
  th {
    text-align: center !important;
    vertical-align: middle;
  }
  td.variant span,
  td.default span {
    font-size: 2em;
  }
  td.default {
    background-color: whitesmoke;
  }
  td a {
    text-decoration: none;
  }
</style>

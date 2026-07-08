<script lang="ts">
  interface Props {
    locale: LocaleID;
  }
  let { locale }: Props = $props();

  import type { LocaleID, ConditionalMappingType } from "../../data/locales";
  import type { JoiningPosition } from "../../data/misc";
  import type { FVS } from "../../data/variants";
  import type { WrittenUnitID } from "../../data/writtenUnits";
  import { joiningPositions } from "../../data/misc";
  import { locales } from "../../data/locales";
  import { variants } from "../../data/variants";
  import { aliases } from "../../data/aliases";
  import LetterVariant from "./LetterVariant.svelte";
  import { hexFromCP, nameToCP } from "./utils";
  import { localeNS, orderedAliases, resolveCharName, mapGetOrCreate, isVariantRef, resolveRef } from "./utils";

  type PE = { fvs: FVS; written: WrittenUnitID[] | undefined; renderPos?: JoiningPosition };

  const conditionOrder = $derived(locales[locale].conditions);
  const localeNamespace = $derived(localeNS(locale));

  const charNameToConditionToPositionToFVS = $derived.by(() => {
    const _orderedAlias = orderedAliases(locale);
    const _localeNamespace = localeNS(locale);
    const map = new Map<string, { default: Map<JoiningPosition, PE>; conditions: Map<ConditionalMappingType, Map<JoiningPosition, PE>> }>();

    for (const alias of _orderedAlias) {
      const charName = resolveCharName(alias, _localeNamespace);
      if (!charName) continue;
      const positionToFVSToVariant = variants[charName];
      for (const position of joiningPositions) {
        for (const [fvsKey, { default: default_, locales }] of Object.entries(positionToFVSToVariant[position])) {
          const variantLocaleData = locales[locale];
          if (!variantLocaleData) {
            continue;
          }
          const conditions = variantLocaleData.conditions ?? [];
          if (!default_ && !conditions.length) continue;
          const charData = mapGetOrCreate(map, charName, () => ({ default: new Map(), conditions: new Map() }));
          const fvs = Number(fvsKey) as FVS;
          const baseWritten = variants[charName]?.[position]?.[fvsKey as unknown as FVS]?.written;
          const written: WrittenUnitID[] | undefined = isVariantRef(variantLocaleData.written ?? baseWritten) ? undefined : ((variantLocaleData.written ?? baseWritten) as WrittenUnitID[] | undefined);
          if (default_) charData.default.set(position, { fvs, written });
          for (const condition of conditions)
            mapGetOrCreate(
              mapGetOrCreate(charData.conditions, condition, () => new Map()),
              position,
              () => ({ fvs, written }),
            );
        }
      }
    }
    // Resolve VariantReferences in default entries
    for (const [charName, charData] of map) {
      for (const [position, entry] of charData.default) {
        if (entry.written) continue;
        const baseVariant = variants[charName]?.[position]?.[String(entry.fvs) as unknown as FVS];
        if (!baseVariant) continue;
        const rawWritten = baseVariant.locales[locale]?.written ?? baseVariant.written;
        if (!isVariantRef(rawWritten)) continue;
        const [refPos, refFvs] = rawWritten as unknown as [JoiningPosition, FVS];
        const resolved = resolveRef(charName, refPos, refFvs, locale);
        if (resolved) {
          entry.written = resolved;
          entry.renderPos = refPos;
        }
      }
    }
    return map;
  });
</script>

<table>
  <thead>
    <tr><th rowspan="2">Letter</th><th rowspan="2">Mapping type</th><th colspan="4">Variants</th></tr>
    <tr
      >{#each joiningPositions as p}<th>{p}</th>{/each}</tr
    >
  </thead>
  <tbody>
    {#each charNameToConditionToPositionToFVS as [charName, { default: defaultPositionToFVS, conditions: conditionToPositionToFVS }]}
      {@const codePoint = nameToCP.get(charName)!}
      {@const hex = hexFromCP(codePoint)}
      {@const char = String.fromCodePoint(codePoint)}
      {@const aliasData = aliases[charName]}
      {@const alias = typeof aliasData === "object" ? aliasData[localeNamespace] : aliasData}
      <tr>
        <td rowspan={conditionToPositionToFVS.size + 1} title="U+{hex} {char} {charName}">
          <a href="#{alias}">{hex}<br />{char} <i>{alias}</i></a>
        </td>
        <td class="default"><code>default</code></td>
        {#each joiningPositions as position}
          {@const e = defaultPositionToFVS.get(position)}
          <td id="{alias}-{position}" class="default"
            >{#if e}<span><LetterVariant {charName} position={e.renderPos ?? position} fvs={e.fvs} written={e.written} /></span>{/if}</td
          >
        {/each}
      </tr>
      {#each conditionOrder as condition}
        {@const positionToFVS = conditionToPositionToFVS.get(condition)}
        {#if positionToFVS}
          <tr>
            <td><code>{condition}</code></td>
            {#each joiningPositions as position}
              {@const entry = positionToFVS.get(position)}
              <td id="{alias}-{position}-{condition}" class="variant"
                >{#if entry}<span><LetterVariant {charName} {position} fvs={entry.fvs} written={entry.written} /></span>{/if}</td
              >
            {/each}
          </tr>
        {/if}
      {/each}
    {/each}
  </tbody>
</table>

<style>
  :global(table) {
    display: table !important;
    overflow: visible !important;
  }
  td,
  th {
    text-align: center !important;
    vertical-align: middle;
  }
  td.variant span,
  td.default span {
    line-height: 1;
  }
  td.default {
    background-color: whitesmoke;
  }
  td:target {
    background-color: yellow;
  }
  td a {
    text-decoration: none;
  }
  tbody td:first-child {
    width: 4rem;
  }
  tbody td:nth-child(n + 3) {
    width: 4rem;
  }
</style>

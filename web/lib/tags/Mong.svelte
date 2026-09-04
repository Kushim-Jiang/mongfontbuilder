<script lang="ts">
  interface Props {
    locale: LocaleID;
    links: string;
    category?: string;
  }
  let { locale, links = "", category = "" }: Props = $props();

  import { locales, type LocaleID } from "../../../data/locales";
  import { writtenUnits } from "../../../data/writtenUnits";

  const localeToPrefix: Record<string, string> = {
    MNG: "hudum",
    MNGx: "hudum-ali-gali",
    TOD: "todo",
    TODx: "todo-ali-gali",
    SIB: "sibe",
    MCH: "manchu",
    MCHx: "manchu-ali-gali",
  };

  const prefix = $derived(localeToPrefix[locale] || "");
  const items = $derived(links.split(" ").filter(Boolean));

  const categoryItems = $derived(category ? locales[locale]?.categories?.[category as keyof (typeof locales)[typeof locale]["categories"]] || [] : []);
</script>

{#each items as item}
  {@const parts = item.split(".")}
  {@const isPos = parts.length >= 2 && parts[1] !== ""}
  {@const unit = isPos ? parts[0] : item}
  {@const pos = isPos ? parts[1] : ""}
  {@const fvs = isPos && parts.length >= 3 ? parts[2] : undefined}
  {@const isUnit = unit in writtenUnits}
  {@const href = !isPos ? `/${prefix}/#${item}` : fvs === undefined ? (isUnit ? `/${prefix}/#${unit}-${pos}` : `/${prefix}/#${unit}-${pos}-0`) : `/${prefix}/#${unit}-${pos}-${fvs}`}
  {@const label = fvs === undefined ? item : fvs === "0" ? `${unit}.${pos} (default)` : `${unit}.${pos}.${fvs}`}
  <a {href} style="font-style: {unit[0] === unit[0].toLowerCase() ? 'italic' : 'normal'}">{label}</a>
{/each}{#if categoryItems.length > 0}
  <span>
    {#each categoryItems as catItem, index}
      <a href={`/${prefix}/#${catItem}`} style="font-style: italic">{catItem}</a>{index < categoryItems.length - 1 ? ", " : ""}
    {/each}
  </span>
{/if}

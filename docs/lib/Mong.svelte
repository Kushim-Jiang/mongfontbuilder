<script lang="ts">
  interface Props {
    locale: LocaleID;
    links: string;
    category?: string;
  }
  let { locale, links = "", category = "" }: Props = $props();

  import { locales, type LocaleID } from "../../data/locales";

  const localeToPrefix: Record<string, string> = {
    MNG: "hudum",
    MNGx: "hudum-ali-gali",
    TOD: "todo",
    TODx: "todo-ali-gali",
    SIB: "sibe",
    MCH: "manchu",
    MCHx: "manchu-ali-gali",
  };

  const prefix = localeToPrefix[locale] || "";
  const items = links.split(" ").filter(Boolean);

  const categoryItems = category ? locales[locale]?.categories?.[category as keyof (typeof locales)[typeof locale]["categories"]] || [] : [];
</script>

{#each items as item}
  <a href={`/${prefix}/#${item}`} style="font-style: {item[0] === item[0].toLowerCase() ? 'italic' : 'normal'}">{item}</a>
{/each}{#if categoryItems.length > 0}
  <p>
    {#each categoryItems as catItem, index}
      <a href={`/${prefix}/#${catItem}`} style="font-style: italic">{catItem}</a>{index < categoryItems.length - 1 ? ", " : ""}
    {/each}
  </p>
{/if}

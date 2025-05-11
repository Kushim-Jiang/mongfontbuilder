import { defineConfig } from "astro/config";
import starlight from "@astrojs/starlight";
import svelte from "@astrojs/svelte";

export default defineConfig({
  srcDir: "./web/src",
  publicDir: "./web/public",
  trailingSlash: "always",
  integrations: [
    svelte(),
    starlight({
      title: "UTN #57 (Editor’s Draft)",
      sidebar: [
        {
          label: "Introduction",
          slug: "index",
        },
        "architecture",
        {
          label: "Writing systems",
          items: [
            "hudum",
            "todo",
            "sibe",
            "manchu",
            "hudum-ali-gali",
            "todo-ali-gali",
            "manchu-ali-gali",
          ],
        },
        "comparison",
      ],
      social: [
        {
          icon: "github",
          label: "GitHub",
          href: "https://github.com/Kushim-Jiang/mongfontbuilder",
        },
      ],
      editLink: {
        baseUrl: "https://github.com/Kushim-Jiang/mongfontbuilder/edit/main/",
      },
      customCss: ["./web/src/custom.css"],
      components: {
        Banner: "./web/src/Banner.astro",
        ThemeProvider: "./web/src/ThemeProvider.astro",
        ThemeSelect: "./web/src/ThemeSelect.astro",
      },
    }),
  ],
});

import { defineConfig } from "astro/config";
import starlight from "@astrojs/starlight";
import svelte from "@astrojs/svelte";

export default defineConfig({
  trailingSlash: "always",
  integrations: [
    svelte(),
    starlight({
      title: "UTN #57",
      customCss: ["./src/custom.css"],
      social: {
        github: "https://github.com/Kushim-Jiang/mongolian-utn",
      },
      editLink: {
        baseUrl:
          "https://github.com/Kushim-Jiang/mongolian-utn/edit/main/docs/",
      },
    }),
  ],
});

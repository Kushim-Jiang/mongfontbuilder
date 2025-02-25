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
      title: "UTN #57",
      social: {
        github: "https://github.com/Kushim-Jiang/mongolian-utn",
      },
      editLink: {
        baseUrl:
          "https://github.com/Kushim-Jiang/mongolian-utn/edit/main/docs/",
      },
      customCss: ["./web/src/custom.css"],
    }),
  ],
});

import { glob } from "astro/loaders";
import { docsSchema } from "@astrojs/starlight/schema";
import { defineCollection } from "astro:content";

export const collections = {
  docs: defineCollection({
    loader: glob({ pattern: "**/*.mdx", base: "web/docs" }),
    schema: docsSchema(),
  }),
};

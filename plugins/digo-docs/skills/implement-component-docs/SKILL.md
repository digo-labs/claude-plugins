---
name: implement-component-docs
description: Create documentation and examples for an existing UI component — scoped pattern reads, the full frontmatter contract, registered MDX components, verified in the browser and llms.txt. Use when asked to document components like Checkbox, Switch, Input, Select, Dialog, etc.
---

# Document UI Component: $ARGUMENTS

Produce a docs page that passes `/audit-docs` by construction: accurate against source, structurally valid in the pipeline, up to the professional reading bar. The docs are the published surface — apps code against them through llms.txt — so exact truth matters more than speed.

## Step 1: Research External References (Optional)

If `implement-component` already answered this in-session, reuse its findings. Otherwise ask via `AskUserQuestion` popup: based on an external library, or original?

- **Original** → skip to Step 2.
- **External** → ask for the docs URL, fetch it, then locate the example/demo source in the library's GitHub repo. Mirror their example coverage and grouping, adapted to this component's actual API.

## Step 2: Learn the Component and the Local Patterns — Scoped

Read, in full:

1. **The component itself**: `packages/ui/src/components/{component}.tsx` and `packages/ui/src/styles/{component}.ts` — props, slots, variants, and data attributes come from here, never from memory.
2. **Its closest family**: the docs pages and example files of 2–3 sibling components in the same category (`apps/design-system/src/app/docs/` + `app/examples/`) — they define the structure, tone, naming (`{component}-{variant}.tsx`), and level of detail to replicate. Do NOT read the whole docs tree.
3. **The pipeline contracts**: `apps/design-system/src/docs.config.ts` (`DOCS_SECTIONS` — the valid section/category pairs) and the registered MDX component inventory in `packages/docs/src/providers/mdx-provider.tsx` (`Callout`, `Steps`/`Step`, previews, …) — the vocabulary available to the page. Read the list, never assume it.

## Step 3: Create Files

1. **Examples** — `apps/design-system/src/app/examples/{component}-{variant}.tsx`: default usage, variants/sizes, interactive states (disabled, error), and composition with other components where relevant. Center previews with `mx-auto`; import exactly as sibling examples do.
2. **Docs page** — `apps/design-system/src/app/docs/{component}.mdx`, following the family's anatomy: Preview → Usage → Examples → API Reference (at the bottom, when the component has a meaningful API).

**Frontmatter contract** — `/audit-docs` validates all of it mechanically:

- `title`, `subtitle`, `description`
- `section` + `category` — the pair must exist in `DOCS_SECTIONS`, or the page silently falls out of navigation
- `icon` — lucide-first, chosen the way sibling pages choose theirs
- `prev` / `next` — when the family maintains a reading chain, insert the page into it (update the neighbors' links too); slugs must resolve

**Body rules:** every `<ComponentPreview name="..." />` matches a real example file; sequential walkthroughs use `<Steps>`, gotchas and warnings use `<Callout>`, enumerable facts use tables; the API Reference documents only props, slots, and data attributes that exist in source — nothing invented, nothing omitted that a user needs.

## Step 4: Verify

- Load the new page in the browser (design-system dev server): every preview renders, console clean of errors the page causes.
- Both modes: examples read correctly in light AND dark.
- Confirm the page appears in the nav and in `/llms.txt` — both derive from docs.config + frontmatter, so absence means a frontmatter typo.

## Step 5: Finish

No commits. Summarize: examples created, the docs page and its placement (section/category/icon/chain), verification results, and anything in the component that proved undocumentable (a source-level gap worth flagging).

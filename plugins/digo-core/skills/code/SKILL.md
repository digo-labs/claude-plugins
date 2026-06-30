---
name: code
description: Write code that follows the Digo design-system patterns, sourced from the docs (llms.txt). Use when asked to create any Digo code — components, pages, hooks, helpers, services, schemas, configs, types, etc. Works in any repo.
---

# Write Code: $ARGUMENTS

Write code that follows the Digo patterns exactly as the **design-system docs** define them. The docs are the single source of truth: every Digo app follows the same documented patterns, so you reproduce the canonical pattern rather than mining the local codebase. This works from any repo — you never need the monorepo or `node_modules`.

## Step 1: Understand the request

Parse from `$ARGUMENTS`:

- **What kind** of artifact — component, page, hook, helper/util, service/class, factory (`define*`/`create*`), schema/constants, backend route/service, provider, config, type, test.
- **Where it should live** — the file path in the current app (use the docs' Project Structure if unsure).
- **What it should do.**

## Step 2: Load the docs

The docs index is `https://design.digo-labs.com/llms.txt`. Fetch it if it isn't already in the conversation. It lists every page with a one-line description and a raw-`.mdx` link.

From the index, select the pages relevant to the artifact and fetch their `.mdx`:

- **Always** read the applicable Code Patterns pages: TypeScript Patterns, Imports and Exports, Error Handling.
- Match the artifact to its specific **Code Patterns** page:
  - helper / util / formatter / validator / small client → **Helpers and Singletons**
  - service or generic data/resource class → **Classes and Services**
  - a `define*` / `create*` wiring function → **Factory Functions**
  - Zod schema, shared types, a constant/route registry, an enum → **Schemas and Constants**
  - a backend route or service function → **Backend Patterns**
  - a custom hook or context provider → **Hooks and Providers**
- For a **component**: read the docs page of every `@digo-labs/ui` component or block you'll use (for its **API Reference** table), plus Composition and the Styling pages as needed. For a brand-new shared component, read Contributing → Creating Components and Styling Components.
- For tables / auth / storage / AI / websockets / routing / forms: read that guide page.

Fetch every page you'll rely on. Do not proceed from memory.

## Step 3: Extract the patterns and the API

From the fetched pages, note the conventions you must match:

- **Naming** — files, functions, variables, types; casing, prefixes, suffixes.
- **The authoring shape** for this artifact — e.g. a helper is a static-method class (`class XHelpers { static … }`); a stateful one is the `init()`-guarded singleton; a factory returns a grouped typed object; a schema is paired with `z.infer`.
- **TypeScript** — the `Properties` interface convention, generics, types vs interfaces.
- **Imports/exports** — named exports, import grouping/ordering, barrel files.
- **Error handling** — the `tryCatch` Result tuple; throw only for programmer error.
- **The exact API** of every `@digo-labs/*` symbol you'll use, taken from its page's API Reference (props, methods, signatures).

## Step 4: Write the code

Write it to match every pattern from Step 3. Read the target file only so you can edit it correctly — **do not** copy conventions from sibling local files; the docs define the conventions, and apps converge to the docs.

Rules:

- Use **only documented APIs**. If a prop, method, or pattern you need is **not in the docs**, do not invent it — flag it (the docs have a gap to patch with `/audit-docs`) and use the closest documented approach.
- Register exports in the relevant barrel/index per Imports and Exports.
- Match the docs' formatting — alignment, trailing commas, spacing.

## Step 5: Confirm

Briefly note which doc pages you used, and call out any symbol you couldn't verify against the docs.

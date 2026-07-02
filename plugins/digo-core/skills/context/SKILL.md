---
name: context
description: Build deep context on the Digo stack from the design-system docs (llms.txt) — packages, patterns, services, styling — before feature work. Use before starting new features or when you need a full picture of the stack. Works in any repo.
---

# Build Digo Context

Build a working model of the Digo stack from the **design-system docs** — the single source of truth — so you're ready for feature work in any repo. Don't analyze the local codebase for patterns; the docs describe the canonical stack every app shares.

## Step 1: Load the index

Fetch `https://design.digo-labs.com/llms.txt`. It lists every page grouped by section — Guide, Development, Skills, Components, Blocks, Utils, Effects — each with a one-line description and a raw-`.mdx` link.

## Step 2: Read the docs

- **Guide** — read the overview and package pages (pick them from the index), plus any stack-area pages the upcoming work touches (styling, tables, auth, storage, deployment, …).
- **Development** — read the **whole section, every page**. It defines every convention and authoring pattern.
- **Components / Blocks / Utils / Effects** — skim their index entries so you know what exists; read individual pages on demand during the task.

## Step 3: Orient in the current app (optional)

To know what *this* app wires up — not to extract patterns — read its `package.json`, `src/app.config.ts`, and `src/db.ts`. That tells you which services, tables, auth, and preset are configured. Patterns still come from the docs.

## Step 4: Summarize

Present a brief, scannable summary:

1. **Packages** — what each provides and its role.
2. **Component & authoring patterns** — how components, helpers, services, factories, schemas, hooks, and state are built.
3. **Styling pipeline** — tokens → style files → `useStyles`/`cn` → component usage.
4. **Services & data** — how services are wired and called, error handling.
5. **Key conventions** — naming, structure, TypeScript, imports.

Keep it to bullets. Note which pages to revisit for which kinds of task.

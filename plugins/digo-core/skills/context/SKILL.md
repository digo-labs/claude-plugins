---
name: context
description: Build context on the Digo stack from the design-system docs (llms.txt) — scoped to the task at hand by default, full immersion on request. Use before starting new features or when you need the right picture of the stack. Works in any repo.
---

# Build Digo Context: $ARGUMENTS

Build a working model of the Digo stack from the **design-system docs** — the single source of truth — so you're ready for feature work in any repo. Don't analyze the local codebase for patterns; the docs describe the canonical stack every app shares.

## Step 1: Scope the run

Parse `$ARGUMENTS`:

- **A task** ("auth pages", "table with file uploads") → **task-scoped**, the default: read only what that work touches.
- **`full`** → **full immersion**: read the docs wholesale, as below.
- **Empty** → ask the user (popup) what they're about to work on — with *full immersion* as one of the options — before reading anything.

## Step 2: Load the index

Fetch `https://design.digo-labs.com/llms.txt`. It lists every page grouped by section — Guide, Development, Skills, Components, Blocks, Utils, Effects — each with a one-line description and a raw-`.mdx` link.

## Step 3: Read the docs

**Task-scoped (default):**

- **Guide** — the overview page, plus the stack-area pages the task touches (styling, tables, auth, storage, AI, websockets, deployment, …).
- **Development** — the pages covering the artifact kinds the task will produce (components, pages, services, schemas, …) and the general convention pages that apply to all code.
- **Components / Blocks / Utils / Effects** — from the index descriptions, read the pages of the pieces the task is likely to use; leave the rest for on-demand reads during the task.

**Full immersion (`full`):**

- **Guide** — read the overview and package pages (pick them from the index), plus any stack-area pages the upcoming work touches.
- **Development** — read the **whole section, every page**. It defines every convention and authoring pattern.
- **Components / Blocks / Utils / Effects** — skim their index entries so you know what exists; read individual pages on demand during the task.

## Step 4: Orient in the current app (optional)

To know what *this* app wires up — not to extract patterns — read its `package.json`, `src/app.config.ts`, and `src/db.ts`. That tells you which services, tables, auth, and preset are configured. Patterns still come from the docs.

## Step 5: Summarize

Present a brief, scannable summary sized to the scope — task-scoped runs cover only what was read:

1. **Packages** — what each provides and its role.
2. **Component & authoring patterns** — how components, helpers, services, factories, schemas, hooks, and state are built.
3. **Styling pipeline** — tokens → style files → `useStyles`/`cn` → component usage.
4. **Services & data** — how services are wired and called, error handling.
5. **Key conventions** — naming, structure, TypeScript, imports.

Keep it to bullets. Note which pages to revisit for which kinds of task.

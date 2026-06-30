---
name: context
description: Build deep context on the Digo stack from the design-system docs (llms.txt) — packages, patterns, services, styling — before feature work. Use before starting new features or when you need a full picture of the stack. Works in any repo.
---

# Build Digo Context

Build a working model of the Digo stack from the **design-system docs** — the single source of truth — so you're ready for feature work in any repo. Don't analyze the local codebase for patterns; the docs describe the canonical stack every app shares.

## Step 1: Load the index

Fetch `https://design.digo-labs.com/llms.txt`. It lists every page — Guide, Packages, Code Patterns, Styling, Components, Blocks, Effects, Skills — each with a one-line description and a raw-`.mdx` link.

## Step 2: Read the foundational pages

Fetch and read these (in parallel where you can):

- **Overview** — Introduction, Ecosystem Overview, Project Structure, Backend Architecture.
- **Packages** — Common, UI, Services, App, WS.
- **Code Patterns** — TypeScript Patterns, Naming, Imports and Exports, Error Handling, Services and Data Access, Composition, Routing, and the construct patterns: Helpers and Singletons, Classes and Services, Factory Functions, Schemas and Constants, Backend Patterns, Hooks and Providers.
- **Styling** — Styling System, Tailwind Utilities, Theme Presets (as the task needs).

Skim the Components and Blocks index so you know what exists; read individual component pages on demand during the task.

## Step 3: Orient in the current app (optional)

To know what *this* app wires up — not to extract patterns — read its `package.json`, `src/app.config.ts`, and `src/db.ts`. That tells you which services, tables, auth, and preset are configured. Patterns still come from the docs.

## Step 4: Summarize

Present a brief, scannable summary:

1. **Packages** — what each provides and its role.
2. **Component & authoring patterns** — how components, helpers, services, factories, schemas, hooks are built.
3. **Styling pipeline** — tokens → style files → `useStyles`/`cn` → component usage.
4. **Services & data** — how services are wired and called, error handling.
5. **Key conventions** — naming, structure, TypeScript, imports.

Keep it to bullets. Note which pages to revisit for which kinds of task.

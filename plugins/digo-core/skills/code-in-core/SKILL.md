---
name: code-in-core
description: Write code inside the digo core monorepo by dynamically analyzing the surrounding source and matching its patterns exactly — mine sibling files and package source, not the published docs. Use when creating any code (component, page, hook, helper, service, factory, schema, route, provider, state, config, type, test) while working inside the monorepo itself.
---

# Write Code in Core: $ARGUMENTS

Write code that matches the digo core monorepo **exactly as the surrounding source already does it**. Inside the monorepo the **code is the source of truth** — the design-system docs describe what the packages *ship*, and they can lag the source you're editing — so you analyze the real neighboring code and reproduce its patterns rather than coding from docs or memory. **Dynamically analyze existing code before writing**, every time.

## Step 1: Understand the request

Parse what is being asked from `$ARGUMENTS`. Determine:

- **What type** of artifact — component, page, hook, helper/util, service/class, factory (`define*`/`create*`), schema/constants, backend route/service, provider, state, config, type, test.
- **Where it should live** — which package under `packages/` and the file path within it.
- **What it should do.**

## Step 2: Find similar code

Before writing anything, search the monorepo for the closest existing code:

1. **By location** — list the target directory and its siblings to understand the neighborhood (e.g. UI components in `packages/ui/src/components/` with paired styles in `packages/ui/src/styles/`; shared code in `packages/common/src/`). Confirm the directory by searching, don't assume it.
2. **By type** — find files of the same kind (other hooks if writing a hook, other services if writing a service, other presets if writing a preset).
3. **By relevance** — if the new code relates to an existing feature or package, read that code too.

Read at least 3–5 of the closest matches **in full**, along with the barrel/index files they register in and any style, helper, or type files they pair with. More is better. Do not skip this step.

## Step 3: Extract patterns

From the files you read, identify the conventions actually in force before writing any code:

- **Naming** — file names, function/variable/type names, casing, prefixes, suffixes.
- **File structure** — import ordering, export style (named vs default), section organization.
- **TypeScript** — how types/interfaces are defined, the prop-typing convention, generics.
- **Code style** — arrow functions vs declarations, early returns, destructuring habits.
- **Composition** — abstraction level, how things combine, helper usage; wrap existing primitives (e.g. `@base-ui/react`) rather than reimplementing them.
- **Imports** — which `@digo-labs/*` packages are used, internal import paths, barrel conventions.
- **Styling** — design-system token usage (no arbitrary values where a token exists) and the style-file pairing the components use.
- **Error handling** — validation, edge cases, fallback patterns.
- **Comments** — when they're used, tone, density (or absence).
- **Formatting** — indentation, spacing, trailing commas, line breaks.

**Verify every API against source.** For any `@digo-labs/*` symbol or primitive you'll call, open its definition and confirm the props/methods/signature exist there — trust the code over the docs or your memory when they disagree.

## Step 4: Write the code

Write code that matches **every pattern** you identified. It must be indistinguishable from the siblings you read — same habits, structure, and style. Where two siblings differ, follow the most common; if it's a toss-up, follow the most recent. After writing, register exports in the same real barrel/index files the neighbors use.

## Key requirements

- NEVER fall back to generic or "best practice" defaults — always match what exists in the source.
- Prefer the monorepo's existing abstractions and utilities over introducing new ones.
- Use only APIs you verified exist in the source. If the codebase has no similar code, widen the search to adjacent packages.
- Match formatting exactly — indentation, spacing, line breaks, trailing commas.
- Briefly note which files you patterned from, and flag anything you introduced with no existing precedent (and, if the docs describe it differently than the code now does, a docs gap worth `/audit-docs`).

---
name: review
description: Review changed code against the Digo design-system patterns and component APIs as defined in the docs (llms.txt), then fix issues directly. Use after writing code or before merging. Works in any repo.
---

# Review: $ARGUMENTS

Review the changed code against the Digo patterns — sourced from the **design-system docs**, the single source of truth. Every app follows the same documented patterns, so deviations are measured against the docs, not the local codebase. This works from any repo — you never need the monorepo or `node_modules`.

## Step 1: Collect changed files

Run `git diff --name-only` and `git ls-files --others --exclude-standard`. Filter to code files (`.ts`, `.tsx`, `.css`); skip deleted files. If `$ARGUMENTS` gives focus (e.g. "focus on pages"), prioritize it but still review every changed file.

## Step 2: Load the docs

Fetch `https://design.digo-labs.com/llms.txt`. Based on the kinds of code in the diff, fetch the relevant pages:

- The core convention pages — TypeScript Patterns, Naming, Imports and Exports, Error Handling, and Project Structure — they apply to everything.
- The specific pattern page (in the **Development** section) matching each non-component file: helper → Helpers and Singletons, service/class → Classes and Services, factory → Factory Functions, schema/constants → Schemas and Constants, backend → Backend Patterns, hook/provider → Hooks and Providers, global/feature state (a `signal`) → Global State with Signals.
- For every `@digo-labs/ui` component or block used in the diff, its docs page — for the **API Reference** table.

Fetch every page you need; do not review from memory.

## Step 3: Review every file

For larger diffs, split files into batches and review in parallel with **Explore agents** (one per batch); each agent fetches the specific component/authoring pages its files need. For each file:

### 3a. Pattern conformance

Check the file against the documented conventions:

- **Naming** — casing, prefixes/suffixes; **complete names, no abbreviations** (`MapCoordinates`, not `MapCoords`); **one main export per file**; **provider files are `*-provider`, never `*-context`**.
- **Imports/exports** — named exports, grouping/ordering, barrels; absolute path aliases across folders.
- **TypeScript** — `Properties` interface, types vs interfaces, generics, where types live; **`enum` for a closed set of named string values in app code (never a bare string-literal union)**; **`undefined` vs `null` — the stack is null-first**; **reuse `@digo-labs/common` types before redeclaring**.
- **Object literals & returns** — **no ES6 shorthand** (`{ overrides: overrides }`, never `{ overrides }`); **a component's render return is parenthesized on its own lines**, even a single element (inline guard clauses may stay).
- **React** — **no function declarations inside `useEffect`** (define them in the hook/component body and reference by name); global or feature-shared state via **signals** (`utils/signals.ts` or the feature folder).
- **The authoring shape for its kind** — e.g. a helper is a static-method class, not loose functions; a stateful singleton uses `init()` + a guarded getter; a schema is paired with `z.infer`; a factory returns a grouped typed object.
- **Error handling** — `tryCatch` Result tuple; throw only for programmer error.
- **Placement** — the file lives where Project Structure says (`src/components/{feature}/`, `src/pages/`, `src/utils/`, `src/helpers/`).
- **Tailwind** — design-system tokens, no arbitrary values.
- **Formatting** — alignment, trailing commas, spacing.

### 3b. API verification (against the docs)

For every `@digo-labs/*` import:

- Verify each component prop used exists in that component's **API Reference** table.
- Verify each service/helper method and signature matches its docs page.
- Flag props/methods not in the docs, wrong types, missing required props.
- If a symbol is used that the docs don't document **at all**, flag it as **unverifiable against docs** — don't assume it's wrong, but it can't be confirmed (the docs likely have a gap).

### 3c. Dead code

Unused imports, unreferenced variables/constants, functions defined but never called within the file.

### 3d. Report

Each issue: file:line, what the docs say it should be, what the file does.

**Agent rules:** read-only (Read, Grep, Glob, plus fetching the docs). Never edit, never build. Never guess an API — cite the docs page. Return a structured issue list with exact file:line references.

## Step 4: Fix all issues

Collect every issue and fix it directly — don't ask per file. Each fix matches what the docs dictate; when in doubt, match the documented pattern, not other local files.

## Step 5: Summary

Output a markdown table: `File | Line | Issue | Fix`. List separately any symbols that were **unverifiable against the docs** (gaps worth patching with `/audit-docs`). If no issues were found, say so.

---
name: review
description: Full quality review of changed code. Validates every file against monorepo patterns (the same pattern-matching approach as writing code, but in reverse) and checks all component APIs against actual source. Fixes issues directly. Use after writing code or before merging.
---

# Review: $ARGUMENTS

## Step 1: Collect Changed Files

Run `git diff --name-only` and `git ls-files --others --exclude-standard` to get all modified and new files.

- Auto-detect which `apps/` directory they belong to — that's the target app
- Skip deleted files
- Filter to code files only: `.ts`, `.tsx`, `.css`
- If `$ARGUMENTS` provides focus context (e.g., "focus on pages"), use it to prioritize but still review all changed files

## Step 2: Review Every File

Split files into batches of 4–8 files. Launch parallel **Explore agents** — one per batch.

Each agent receives its batch of files and these instructions:

---

**For each file in your batch:**

### 2a. Find Similar Code

Use this discovery approach (the same one used when writing new code):

1. **By location** — list files in the same directory and sibling directories (NOT in the target app — look in the monorepo: other apps, packages)
2. **By type** — find files of the same kind elsewhere (if reviewing a page, find other pages; if a hook, find other hooks; if a util, find other utils)
3. **By relevance** — if the file relates to a specific feature or component, read that component's source too

Start with 3 similar files. If the patterns aren't clear yet — naming is inconsistent, structure varies — read more until they are. There is no fixed limit. The goal is confidence, not a number.

### 2b. Extract ALL Patterns

From the similar files, identify every pattern:

- **Naming** — file names, function/variable/type names, casing, prefixes, suffixes
- **File structure** — import ordering, export style (named vs default), section organization
- **TypeScript** — how types/interfaces are defined, generics usage, prop typing, where types live (inline vs separate file vs shared types file)
- **Code style** — arrow functions vs declarations, early returns, destructuring, ternaries vs if/else
- **Composition** — abstraction level, helper usage, how things combine
- **Imports** — which packages are used, internal import paths, barrel file conventions
- **Error handling** — validation, edge cases, fallback patterns
- **Comments** — when they're used, tone, density (or absence)
- **Formatting** — indentation, spacing, trailing commas, line break habits
- **Tailwind** — design system token usage (typo-*, color tokens, spacing), no arbitrary values
- **Definitions & ordering** — where consts, types, interfaces go within a file, declaration order, export placement

### 2c. Validate Monorepo Package APIs

For every `@digo-labs/ui` import:
- Read the actual component source in `packages/ui/src/` (check `components/`, `blocks/`, `effects/`, `hooks/`, `providers/`, `utils/`)
- Verify every prop passed in JSX exists in the real component API
- Flag: made-up props, wrong prop types, missing required props, deprecated patterns

For every `@digo-labs/common` import:
- Verify the export exists and is used correctly

For every `@digo-labs/services` import:
- Verify the export exists and is used correctly

For **Icon** components specifically:
- Verify every icon name string exists in `packages/common/src/icons.ts` CURATED_ICONS

### 2d. Flag Dead Code

- Unused imports
- Unreferenced variables or constants
- Functions defined but never called (within the file)

### 2e. Compare and Report

Compare the reviewed file against every extracted pattern from 2b. Flag any deviation with:
- File path and line number
- What the pattern says it should be
- What the file actually does

---

**Agent rules:**
- Use ONLY read-only tools (Read, Grep, Glob). Never edit files or run builds.
- NEVER guess APIs — always read the actual source file
- NEVER hardcode pattern assumptions — always discover from similar files
- Return a structured list of all issues found with exact file:line references

## Step 3: Fix All Issues

Collect all issues from every agent. Fix them directly — do not ask per file.

Each fix must match what the monorepo patterns dictate. When in doubt, match the majority pattern from the similar files discovered in Step 2.

## Step 4: Summary

Output a markdown table with all changes made:

| File | Line | Issue | Fix |
|------|------|-------|-----|

If no issues were found, say so.

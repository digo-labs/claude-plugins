---
name: review
description: Review changed code against the Digo design-system patterns and component APIs as defined in the docs (llms.txt), then fix issues directly. Use after writing code or before merging. Works in any repo.
---

# Review: $ARGUMENTS

Review the changed code against the Digo patterns — sourced from the **design-system docs**, the single source of truth. This skill carries no rules of its own: **every convention the docs state is in scope**, and deviations are measured against the docs, not the local codebase or your own taste. This works from any repo — you never need the monorepo or `node_modules`.

## Step 1: Collect changed files

Run `git diff --name-only` and `git ls-files --others --exclude-standard`. Filter to code files (`.ts`, `.tsx`, `.css`); skip deleted files. If `$ARGUMENTS` gives focus (e.g. "focus on pages"), prioritize it but still review every changed file.

## Step 2: Read the docs — everything first, then deep

Fetch `https://design.digo-labs.com/llms.txt`.

1. **Read the whole Development section — every page.** Those pages define every convention the diff must satisfy. A rule you didn't read is a violation you'll miss.
2. **Go deep from the index.** Using the one-line descriptions, fetch the docs page of every `@digo-labs/ui` component or block used in the diff (for its **API Reference** table) and any Guide page for stack areas the diff touches.

Do not review from memory.

## Step 3: Review every file

For larger diffs, split files into batches and review in parallel with **Explore agents** (one per batch); each agent reads the same Development pages plus the component pages its files need. For each file, verify:

- **Every documented convention.** Everything the Development pages state — naming, structure and placement, TypeScript, imports/exports, error handling, styling, formatting, comments, state, and anything else the docs define. The checklist is the docs themselves; do not restrict yourself to a memorized subset.
- **Every API.** Each `@digo-labs/*` prop, method, and signature used must exist in its page's API Reference with matching types. If a symbol isn't documented at all, flag it as **unverifiable against docs** — don't assume it's wrong; the docs likely have a gap.
- **Dead code.** Unused imports, unreferenced variables/constants, functions defined but never called.

**Agent rules:** read-only (Read, Grep, Glob, plus fetching the docs). Never edit, never build. Never guess an API — cite the docs page. Return a structured issue list with exact file:line references: what the docs say it should be, what the file does.

## Step 4: Fix all issues

Collect every issue and fix it directly — don't ask per file. Each fix matches what the docs dictate; when in doubt, match the documented pattern, not other local files.

## Step 5: Summary

Output a markdown table: `File | Line | Issue | Fix`. List separately any symbols that were **unverifiable against the docs** (gaps worth patching with `/audit-docs`). If no issues were found, say so.

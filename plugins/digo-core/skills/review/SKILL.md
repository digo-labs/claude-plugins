---
name: review
description: Review changed code in a Digo app repo against the house style and the neighbouring code, then fix what it finds. No docs read up front and no agents — one pass, file by file. Use after writing code or before a milestone. Inside the core monorepo it reviews against the sibling source instead (the code-in-core standard).
---

# Review: $ARGUMENTS

Review the changed code the way the user would: against the house style and the code around it. The style lives in the `code` skill of this plugin; this skill does not restate it.

**Reviewing changes in the core monorepo** (root `package.json` named `@digo-labs/index`)? The source is the truth there: review each change against its sibling files' patterns (the `code-in-core` standard), never "fix" source toward the published docs, and report doc/source mismatches as gaps for `/audit-docs`.

## 1. Collect the changes

Run `git diff HEAD --name-only` and `git ls-files --others --exclude-standard` — or the range or branch `$ARGUMENTS` names. Keep code files (`.ts`, `.tsx`, `.css`), skip deleted ones. If `$ARGUMENTS` gives a focus, start there, but review every changed file.

## 2. Load the standard

Read the «House style» and «Platform and UI» sections (traps included) of `${CLAUDE_SKILL_DIR}/../code/SKILL.md`. That is the checklist. Nothing else is read up front.

## 3. Review, file by file

Work through the files yourself, one after another — no agents, at any diff size. For each file read the diff and the whole file; once per folder, read its closest unchanged sibling. Judge the changed lines; untouched old code that breaks the style is listed at most, not rewritten.

- **House style** — every rule in the checklist.
- **Neighbours** — what the rules don't fix (naming, import order and alignment, formatting, how services and state are called) matches the siblings.
- **Copies** — grep for every new type, union, constant, helper and multi-element JSX block: an existing one with the same shape, values or body means reuse or extract, and the original caller moves too.
- **Platform** — Digo's AWS services only through the `@digo-labs/*` APIs, no workarounds in the app's config. A platform API you haven't seen in this app: installed types > the package's guide > one page of the docs site.
- **Brand** — AWS event apps only: what guests see uses the `Aws*` components as shipped, positioned and never redrawn.
- **Dead code** — unused imports, variables, functions, and exports with no caller. Never a bare hook call: it can be a subscription.
- **Known traps** — a timer cleared without nulling its handle, `*.test.ts` inside `src/`, R3F `uniforms` passed as a JSX prop and mutated.

Don't flag UI choices: which library if any, layout and look are the app's call (except the brand rule above).

## 4. Fix

Fix every issue directly, without asking per file. Leave unfixed — and list — only what changes behaviour the user sees, needs a decision, or needs a core change. Then run the app's type check and lint from its `package.json` scripts.

## 5. Summary

A table `File | Line | Issue | Fix`, then the unfixed items with the reason for each. If nothing was found, say so in one line.

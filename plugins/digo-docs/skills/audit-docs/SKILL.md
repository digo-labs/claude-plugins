---
name: audit-docs
description: Audit all design system documentation for accuracy, completeness, structure, and readability. Docs-first - starts from what the docs claim and contrasts it against actual source code, validates the docs pipeline (frontmatter, previews, prev/next, llms.txt), and holds every page to a professional-docs reading bar. Undocumented exports are reported as an informational pending-work inventory, never as findings. Discovers issues dynamically - nothing hardcoded. Use as /audit-docs (full scan) or /audit-docs <file-or-section> (targeted). Replaces /update-guides.
---

# Audit Docs: $ARGUMENTS

Findings only — never apply changes during the audit. Present everything for approval first, as a fix plan or as a findings table if the user asked for one.

## Step 1: Discover

Find all MDX docs in `apps/design-system/src/app/docs/` and all example files in `apps/design-system/src/app/examples/`.

- If `$ARGUMENTS` specifies a component or section name, filter to only matching docs and examples
- If `$ARGUMENTS` is empty, audit everything

Read each discovered doc in full. Group by frontmatter `section` and `category`.

Also discover the two sources of structural truth:
- `apps/design-system/src/utils/consts.ts` → `DOCUMENTATION_SECTIONS` (valid sections and categories)
- The documentable surface: exports of `packages/ui/src/index.ts` (components, blocks, effects, hooks, providers), plus the public surface of `@digo-labs/app`, `@digo-labs/services`, and `@digo-labs/common` for Guide coverage

## Step 2: Mechanical Validation

These checks are deterministic — run them with quick read-only scripts before any judgment work:

- Every doc's frontmatter `section` + `category` pair exists in `DOCUMENTATION_SECTIONS` (typos silently fall out of navigation)
- Every `<ComponentPreview name="..." />` and `<EffectPreview name="..." />` matches a real file in `examples/`
- Orphaned examples — example files no doc references
- `prev` / `next` slugs resolve to real docs; flag dead ends and broken reading chains
- `scripts/build-llms-txt.js` section/category list matches `consts.ts` (they are maintained separately and drift)
- `public/llms.txt` is fresh: every doc appears in it, nothing in it points to a missing doc
- Any count claimed in prose ("57 components", "12 skills") matches reality

## Step 3: Docs-First Contrast

**Policy: the docs define the intended surface.** Exports without a doc page are pending component updates by design — the owner updates the component first, then documents it. They are NOT doc gaps.

- Direction of the audit is always docs → source: everything a doc claims must exist and match. Never the reverse.
- Still compute the export-surface diff (components, blocks, effects, hooks, providers vs doc slugs), but emit it as an **informational appendix** titled "Undocumented exports — pending by policy, confirm nothing slipped": the user scans it to catch a genuinely forgotten page. Zero findings, zero priorities from this list.
- Do flag, as real findings: examples that exist for an undocumented feature (a doc was probably started and lost), and Guide coverage holes for workflows a teammate needs (app-building, deploy paths) — workflows are documented intent even when no single export maps to them.

## Step 4: Accuracy Audit (per doc)

Extract what each doc claims, then read the actual source and compare. Never guess source — always read the files. Claims to extract: import paths and file paths, component/function/type names, props/types/defaults, CSS class names, preview references, config and setup instructions, counts, workflows.

Flag only real issues:

### Content Accuracy
- **Wrong code examples** — snippets that don't match real source
- **Wrong API docs** — props, types, returns, or defaults that have changed
- **Wrong counts** — outdated numbers
- **Wrong file paths** — paths that have moved or been renamed
- **Removed features** — documented things that no longer exist
- **Missing coverage** — undocumented props, variants, or important behaviors in existing docs

### Example Correctness
- **Broken previews** — `name` doesn't match any example file
- **Wrong imports** — example imports things that don't exist
- **Wrong API usage** — example uses props or patterns that have changed
- **Stale examples** — example doesn't reflect current component API

### Structural Issues
- **Doc too broad** — covers too many unrelated topics, should be split
- **Doc too narrow** — could be merged with a related doc
- **Orphaned doc** — documents something that has been removed
- **Outdated workflows** — getting-started or setup instructions that no longer match reality

### System Docs
- Installation steps, project structure descriptions, design system concepts, and provider setup still match the real repo

## Step 5: Readability Bar

The standard: every page should read like professional platform docs (shadcn, Base UI). Audience is layered — a plain-language human path first, exhaustive truth below for agents and power users. Flag only concrete failures a reader actually hits, never taste:

- **Page anatomy** — component pages flow Preview → Usage → Examples → API Reference (API at the bottom, present when the component has a meaningful API). Anatomy, Do's & Don'ts, and frontmatter links are included **where they genuinely help**, not mechanically everywhere.
- **Opening** — the first lines tell a human what this is and when to use it, in plain words.
- **Doc MDX components** — where a sequence, warning, or grouping would genuinely read better with a dedicated component (`<Steps>`/`<Step>` for walkthroughs; callout/card components as they exist), flag it as a candidate. Judgment call, not a rule — it does not have to be Steps per se, and a page that reads fine as prose stays as prose.
- **Scannability** — noun-phrase H2 sections, short paragraphs, tables for enumerable facts, no walls of text.
- **Consistency** — the same vocabulary for the same concepts across pages (variant, preset, override, slot, block).
- **Plain language for infra** — AWS and backend pages expand acronyms on first use and explain concepts, not just commands.

## Step 6: Findings Output

Emit findings as table rows, grouped by section:

| # | Category | What | Why | Priority | Effort |

- **Priority:** P1 = factually wrong or broken (a reader following it fails). P2 = missing or structural (coverage gap, pipeline drift, walkthrough without Steps). P3 = polish (works, but below the reading bar).
- **Effort:** S (< 30 min), M (30 min – 2 h), L (> 2 h).
- Every finding cites file paths.
- Skip docs with no issues; say how many were clean.
- State explicitly how many borderline/cosmetic items were dropped, so nothing is silently lost.

Wait for approval before changing anything.

## Key Rules

- NEVER guess source code — always read the actual files
- NEVER hardcode assumptions about which files exist — always discover dynamically
- Mechanical checks before judgment work; completeness needs the real export surface, never a remembered list
- Use each doc's own content as the guide for what source files to check
- Readability flags must point to a concrete failure a reader hits, not a preference
- When a doc shows a code example, compare it with the real file
- When a doc mentions a count, actually count to verify
- Keep the audit pragmatic: the goal is clear, correct, professional documentation — not change for its own sake

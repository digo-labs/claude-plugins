---
name: implement-component
description: Implement a new UI component in the digo core monorepo — research references, write it through code-in-core's pattern mining, verify it renders with its states, then chain into implement-component-docs and update-presets. Use when asked to create components like Checkbox, Switch, Input, Select, Dialog, etc.
---

# Implement UI Component: $ARGUMENTS

Orchestrate the full life of a new component: build it, prove it, document it, give every preset a say. Delegate to sibling skills by name instead of restating them — when they improve, this skill improves with them. If the user explicitly scoped the request to the component alone, run Steps 1–3 only and list the rest as pending in the summary.

## Step 1: Research References (Optional)

Ask via `AskUserQuestion` popup: is this component based on an external library, or original?

- **Original** → skip to Step 2.
- **External** → ask for the docs URL (e.g. `https://ui.shadcn.com/docs/components/checkbox`), fetch it, then find the library's GitHub repo and read the component's real source and examples/demos there — never work from the docs page alone.

Focus on: available sub-components, props API, accessibility behavior, variants/sizes to support, and internal composition.

## Step 2: Write Through code-in-core

Run the `code-in-core` skill for the writing itself — it mines the closest sibling components and matches their patterns exactly. Layer these library-specific requirements on top:

- **File order** (the component imports the style):
  1. Style file: `packages/ui/src/styles/{component}.ts`
  2. Register style export in `packages/ui/src/styles/index.ts`
  3. Component file: `packages/ui/src/components/{component}.tsx`
  4. Register component export in `packages/ui/src/index.ts`
- Wrap Base UI primitives from `@base-ui/react` — never reimplement what Base UI provides.
- Expose interactive states the way siblings do (`data-*` attributes, `disabled`) — preset overrides and forced-state sweeps depend on them.

## Step 3: Verify

- `npx eslint --fix` on every created file; `npx tsc --noEmit` in `packages/ui`.
- Render it in the design-system app (a scratch usage, or its example if one already exists): resting look in light AND dark, then every interactive state — hover, focus, active, its `data-state`s, `disabled`. Fix and re-check until clean — never hand over unseen work.

## Step 4: Document

Run the `implement-component-docs` skill. This is not optional polish: apps build through the `code` skill from the published docs (llms.txt), so an undocumented component does not exist outside the monorepo. The docs page also becomes the verification surface for Step 5.

## Step 5: Preset Coverage

Run the `update-presets` skill for the new component so every curated preset makes an explicit decision about it — an extend-based override in its design language, or a recorded skip.

## Step 6: Finish

No commits. Summarize: files created, which siblings the patterns came from, verification results per state and mode, the docs page created, and the per-preset decision table — plus anything skipped and why.

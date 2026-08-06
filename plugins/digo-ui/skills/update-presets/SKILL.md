---
name: update-presets
description: Bring every curated preset up to date when new components land in @digo-labs/ui — re-derive each preset's design language from its source and landing, write extend-based per-component overrides or record explicit skips, clean up replaced components, verify with forced-state sweeps per preset in both modes, and place the component into landings the user approves. Use when a new component needs preset coverage, when asked to update or sync presets after adding components, or with no arguments to audit for recently added components that no preset styles yet.
---

# Update Presets for: $ARGUMENTS

When a component lands in `packages/ui`, every curated preset must make a deliberate decision about it: an extend-based override in the preset's design language, or an explicit skip because the base look already fits. This skill produces those decisions for all curated presets — never `digo`, which IS the base look — and proves them in the browser. Analyze the live source at each step; never code the preset system from memory.

## Step 1: Resolve the component list

**With arguments** — the named component(s). Validate each against the export names in `packages/ui/src/styles/index.ts`; stop and ask if a name doesn't resolve.

**No arguments — audit mode.** Coverage cannot be diffed naively: most base styles are intentionally un-overridden everywhere (the `parameter-*` family, pickers, utility wrappers). Find *new* unstyled components instead:

1. Compute zero-coverage: style exports from `styles/index.ts` minus the union of override keys registered across all `presets/curated/*.ts` (registration keys are camelCase, style files kebab-case — map accordingly).
2. Filter by git recency: a zero-coverage component is a candidate when its `styles/{name}.ts` is untracked/uncommitted, or its last commit is newer than the newest commit touching `presets/curated/`. This heuristic is fragile — any preset commit resets the clock — so present candidates in an `AskUserQuestion` popup (multiSelect) for confirmation rather than assuming, and remind the user that explicit arguments are the reliable path.
3. Also report orphaned override keys — registrations in any preset pointing at a style export that no longer exists (usually already a type error). These become cleanup work in Step 4.

**Replacements.** If a run's component supersedes a deleted one (its style file is gone but presets still reference it), the run owns the migration: remove the stale block and registration key from each preset alongside adding the new one.

**Pass-throughs.** If the component's base style file is an empty pass-through (no slots worth theming — common for `parameter-*`), report that presets have nothing to override and drop it from the run.

## Step 2: Learn the system and the component

Read, in this order:

- `packages/ui/src/presets/types.ts`, `helpers.ts` — the `ThemePreset` shape and how `overrides` merge.
- `packages/ui/src/providers/design-system-provider.tsx` — how overrides replace whole per-component style objects (this is why `extend` is mandatory).
- The component's `packages/ui/src/styles/{name}.ts` IN FULL — slots, variants, defaults — and its `packages/ui/src/components/{name}.tsx` for the data-attributes and states (`data-state`, `data-pressed`, `disabled`) the sweep must force.
- The component's docs/demo page in `apps/design-system` (docs nav or `app/examples`) — this is the verification surface. If none exists yet, say so and verify on a minimal scratch usage instead.

Load-bearing mechanics (verify they still hold before relying on them):

- **Override with `extend`, never with full copies**: `styles({ extend: baseStyles.{name}, slots: {...}, variants: {...} })` carrying ONLY the aesthetic delta; register via the preset's overrides map with the exact export name from `styles/index.ts`.
- Extend-delta rules: replace within the same utility group (`bg-*` → `bg-transparent`); switching border style needs the explicit pair (`border-solid` to beat a base `border-dashed`); appended standard utilities beat `cs-*` `@apply`-ed declarations in the cascade — verify collisions with computed styles. Extension `variants` may only reference slots declared in the extension — declare untouched slots as `''` when a variant needs them.
- Preset variant classes must be strings — arrays render as `[object Object]`.
- `typo-label`/`typo-header`/`typo-code` compose with `typo-N` sizes; preset `radius` scales every `rounded-*` except `rounded-full` — escape per component with explicit `rounded-none`/`rounded-full`.

## Step 3: Re-derive each preset's design language

For each curated preset (all of them, every run):

1. **Mine the preset source.** Its helper tokens (e.g. windows-98's raised/sunken shadow recipes), border tiers (which neutral steps mean structure vs chrome), the one interaction treatment reused across components, mode-safe pairing habits, and signature moves (uppercase mono labels, hairline rules, pill shapes…). The file is the only durable record of the theme's language — there is no stored contract.
2. **Visual read.** Load `/presets/{slug}` in the browser (the landing self-applies its preset) and take a light + dark look before writing anything — the rendered voice catches what class strings hide.
3. **Anchor on the closest styled sibling.** Find the existing override whose role the new component most resembles (a chat bubble reads like card/alert surfaces; a new input like the field/input cluster) and match its treatment — same tier, same interaction recipe, same motifs.

Batch wisely: when several components arrive together (a family), do one derivation pass per preset and write all of that preset's blocks in it.

## Step 4: Write overrides — or explicit skips

Per preset × per component, exactly one of:

- **Override block**: minimal extend delta in the preset's language, inserted in the file's existing (alphabetical) block order, plus the registration key. Match the file's code style exactly; zero comments.
- **Explicit skip**: the base look already sits correctly in this theme. No code — but the skip and its one-line reason go in the final summary. A skip is a decision, never an omission.

Do all cleanup from Step 1 here too: stale blocks, orphaned registrations, replaced-component keys. Then `npx eslint --fix` on touched files and `npx tsc --noEmit` in `packages/ui` — clean before any browser time.

## Step 5: Verify — scoped forced-state sweep

For each preset × light AND dark: the component's docs/demo page, rendered under that preset. Fix and re-sweep until green — never hand over unseen work.

Known-good harness recipes (verify they still hold; the in-app browser pane freezes rAF, so drive interactions through headless Chrome when it misbehaves):

- Apply a preset without UI: load `/presets/{slug}` (self-applies), then SPA-navigate to the docs page via `history.pushState` + `PopStateEvent('popstate')` — provider state survives.
- Mode: the `mode` localStorage key (JSON string) set via `evaluateOnNewDocument`, then reload.
- Forced states: CDP `CSS.forcePseudoState` for `:hover`/`:focus-visible`/`:active` on each interactive slot; toggle `data-state`/`disabled` where the component has them; wait ≥420ms after forcing (`cs-transition` races shorter reads).
- Warm up all target URLs with plain gotos first and retry a failed page once — Vite dep-optimization full-reloads destroy evaluation contexts mid-run.

Gate on: no invisible or clashing states (text vs effective background), the preset's border tier and interaction recipe respected, no console errors caused by the change. Record a per-preset pass/fail table. If a style refuses to apply, check for hardcoded inline styles in the component source and report them as source-level gaps — never patch base component source during a preset run.

## Step 6: Landing placements — propose, let the user pick

Landings are each preset's curated showcase; the skill never edits one silently.

1. Review every `apps/design-system/src/app/presets/*-landing.tsx` for two cases: **migrations** (the landing uses a component this run replaced or removed — the edit is required, not optional) and **opportunities** (the new component would genuinely serve that landing's company story — a support chat, a stats strip; a forced fit is worse than no placement).
2. Present a compact table in chat (landing → proposed placement or "no fit"), then ask via `AskUserQuestion` multiSelect which opportunities to apply (group 3-4 landings per question when there are many). State migrations as required work, outside the popup.
3. Edit only what was approved (plus migrations), following create-preset's build rules: production copy in the company's voice, fully wired controls, the preset's one interaction treatment, responsive at ~375px and desktop.
4. Every edited landing gets a landing sweep: full scroll-through in both modes, console gate, no horizontal overflow, forced states on the new section. Untouched landings are not re-audited.

## Step 7: Finish

1. `npx eslint --fix` on every touched file; `npx tsc --noEmit` in `packages/ui` and `apps/design-system` (note pre-existing failures you didn't cause).
2. No builds, no commits.
3. Summarize: components covered; the per-preset decision table (override vs skip with reasons); cleanups performed; the forced-state sweep results per preset × mode; landings edited (with their sweep results) and proposals declined; orphaned keys and source-level gaps found.

---
name: create-preset
description: Generate a new theme preset from website/Figma URLs or a style brief. Extracts or derives colors, typography, shadows, radius, and per-component overrides, then applies and visually verifies the preset in the design-system app in both modes. Use when asked to create a preset, theme, or skin from a URL, mockup, or style description.
---

# Create Theme Preset from: $ARGUMENTS

## Step 1: Understand the Preset System

Read these files to understand the current state of the preset system:

- `packages/ui/src/presets/types.ts` — the `ThemePreset` interface and all related types
- `packages/ui/src/presets/palettes.ts` — all available palette names and their hex values
- `packages/ui/src/presets/helpers.ts` — how preset values become CSS vars (`--color-{role}-{n}`, `--typo-*`, `--radius`, `--shadow-*`)
- `packages/ui/src/providers/design-system-provider.tsx` — how overrides merge
- `packages/ui/src/presets/curated/` — every existing preset, to match code style exactly
- `packages/common/src/index.css` — `@font-face` families (any family name is usable, not just ones with a `--font-*` var), `--typo-*` defaults, `--radius-*` derivation, and the `cs-*` utilities (`cs-backdrop-panel`, `cs-focus`, `cs-popup-animation`)
- `packages/ui/src/styles/index.ts` — all component style names (the valid `overrides` keys)

Facts that will save you from bugs — verify they still hold, then rely on them:

- **Overrides are full replacements.** The provider does `{ ...baseStyles, ...presetOverrides, ...appOverrides }` — a shallow merge per component key. An override replaces the component's ENTIRE `styles()` object, so always copy the base style file's full definition and modify it; never write a partial.
- **Mechanics**: in the preset file `import { defineOverrides, styles } from 'src/utils/styles';` and set `overrides: defineOverrides({ <barrelExportName>: <yourStyles> })`. Keys must match the export names in `styles/index.ts` (`inputGroup`, `numberField`, `navigationMenu`, …).
- **Typography voices compose with sizes**: `typo-label` / `typo-header` / `typo-code` win over the `typo-N` size utilities (base styles rely on it: `'typo-2 typo-label'`). Use this to give labels/headers a distinct font at any size. `text-transform` is NOT part of the typo system — add `uppercase` per component if the style calls for it.
- **Radius cascades**: preset `radius` drives ALL `rounded-*` utilities multiplicatively (`--radius-sm` etc. are `calc()` of `--radius`). `radius: '0rem'` zeroes everything except `rounded-full`. Per-component exceptions use explicit `rounded-none` / `rounded-full`.
- **Font families**: `typography.font` takes the raw `@font-face` family name from `index.css` — all ~55 families work, including ones without a `--font-*` var.

## Step 2: Gather the Design Reference

### Website URLs
1. `WebFetch` each URL in `$ARGUMENTS`; extract colors, typography, shadows, radius, spacing from the HTML/CSS.
2. **Auto-explore**: follow 2-3 internal links for a broader picture; extract from each.
3. **Screenshot** each page for visual cross-reference (shadows, spacing, overall feel).

### Figma URLs
1. Parse `fileKey` / `nodeId`, use `get_design_context` for tokens and `get_screenshot` for reference. Skip auto-explore.

### Style brief (no URLs)
The arguments may instead describe a style ("that mockup", "warm brutalism", a conversation reference). Derive the design language from the brief and the conversation, then go to Step 3's grill — more decisions are open, so more questions are warranted.

## Step 3: Grill Before Building

If the reference leaves real choices open (always for briefs, rarely for a clean URL extraction), ask with `AskUserQuestion` popups before writing any file — 1-2 rounds, max 4 questions each, always mark a "(Recommended)" first option:

- preset name; neutral palette; accent palette (show actual hex evidence from `palettes.ts` in the descriptions)
- header/body/label fonts (name real catalog families); shadow character (flat / soft / hard-offset); radius
- If the user answers "you decide" / "do your thing", stop asking and own the remaining choices.

Skip entirely when the extraction is unambiguous — do not interrogate a user who gave you a pixel-perfect reference.

## Step 4: Define the Design Language Contract

Before writing overrides, write down (in your plan, not the code) a small contract and apply it uniformly — inconsistency between sibling components is the most common review complaint:

- **Border tiers**: which neutral step means structural frame, which means control border, which means hover/active. Every component picks from these tiers — components that appear nested or fused (code block inside a collapsible, chips inside combobox, fields inside groups) MUST use the same tier as their host.
- **Interaction states**: one hover/pressed/selected treatment reused everywhere (e.g. invert to `bg-neutral-12 text-neutral-1`).
- **Mode-safe color pairings** — the #1 source of dark-mode bugs. Palette-step classes flip with mode, so a pair that reads well in light can invert to unreadable in dark:
  - `neutral-12` on `neutral-1` (and vice versa) is always safe — they flip together.
  - Text on a **solid step-9/10 role fill** must NOT be a palette step. Use fixed `text-black` on bright solids (lime, yellow, amber, mint, sky) and fixed `text-white` on dark solids (tomato, crimson, red, green, blue, violet…) — same rule Radix uses for its solid-step contrast color.
  - When in doubt, compute: WCAG contrast of the palette's `dark`-ramp step 9 hex against the intended text color.
- **Signature moves**: 2-4 recurring motifs (uppercase mono labels, hairline rules, pill CTAs…) listed explicitly, so every component either applies them or deliberately opts out.

## Step 5: Generate the Preset

### Colors
Map to the 6 roles (`neutral`, `accent`, `error`, `success`, `warning`, `info`). For role solids compare against palette step 9; for a specific background/paper tone also compare steps 2-3 — the neutral choice is usually decided by the background, not the solid.

### Populate every field
`ThemePreset` requires every field except `custom` and `overrides`. When an extracted value would be practically identical to the default preset's, copy the default rather than inventing a variation. Typography (font/weight/tracking/leading per role), shadows (5 steps; `blur: 0` gives hard print-offset shadows, `opacity: 0` disables a step), radius, `spacingFactor`, `typographyScaleFactor`.

### Component overrides — sweep everything
Work in batches so context stays manageable, reading each batch's base files right before overriding them:

1. form/input primitives  2. containers + navigation  3. pickers/media/data  4. `parameter-*` (mostly empty pass-throughs — override only the few with real classes)  5. blocks (login-card, chat-thread, prompt-input, user-*)

For each component: copy the base definition, apply the contract from Step 4, keep every behavioral class (the `data-*`, `has-*`, animation, and layout plumbing) untouched — restyle only colors, borders, radius, typography, shadows, paddings. Only register components whose result differs from base. Replace `cs-backdrop-panel` inline (with your popup surface treatment) when the style calls for opaque popups.

### Create files
1. `packages/ui/src/presets/curated/{name}.ts` — kebab-case file, `{name}Preset` camelCase export; match existing preset code style exactly (colon alignment, quotes). Zero comments.
2. Add the export to `packages/ui/src/presets/curated/index.ts` — `PRESETS` auto-collects it.

## Step 6: Apply and Verify in the Browser

Never declare the preset done without seeing it. Use the design-system app (`preview_start` with the `design-system` launch config):

1. **Activate**: open the theme panel (navbar icon) and pick the new preset in the preset picker — no source change needed. Runtime selection resets on full page reloads, so navigate between pages via in-app links. (Alternative when you need many full reloads: temporarily set the preset in `apps/design-system/src/app.config.ts` — and ALWAYS restore it before finishing.)
2. **Sweep visually**: `/playground` renders nearly every component in real DOM — screenshot section by section (its scroll lives in an inner container; drive it with `scrollIntoView` via `javascript_tool`). Docs pages (`/library/components/<slug>`) render examples in **scaled iframes: clicks there don't reach popups** — verify popup styling via real surfaces (navbar dropdowns, theme panel, playground) instead.
3. **Wait out animations**: pages stagger-fade in; a "blank" screenshot right after navigation is usually mid-animation. Wait 2-3s and re-shoot before diagnosing.
4. **Both modes**: toggle dark mode (navbar toggle, or set the `mode` key in localStorage and reload) and re-check at least: solid fills, hover/selected states, popups, and one docs page.
5. **Consistency audit**: docs component pages stack preview frame + "show more" collapsible + code block — border tiers must match there; also check chips-in-combobox, fields-in-groups, toasts vs alerts.
6. Fix, let HMR reload, re-verify. Iterate until clean.

If a visual constant resists the preset (computed style ≠ your classes), check for **hardcoded inline styles** in the component source (e.g. an effect setting `borderRadius` via JS). Presets cannot reach those — report them to the user as source-level gaps instead of fighting them.

## Step 7: Finish

1. `npx eslint --fix packages/ui/src/presets/curated/{name}.ts` (fixes the repo's colon-alignment style), then confirm clean.
2. `npx tsc --noEmit` in `packages/ui`.
3. Do not run builds. Do not commit. Summarize: choices made, components overridden, verified surfaces/modes, and any source-level gaps found.

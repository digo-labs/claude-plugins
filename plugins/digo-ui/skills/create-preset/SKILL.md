---
name: create-preset
description: Generate a professional theme preset from website/Figma URLs or a style brief. Derives colors, typography, shadows, radius, and extend-based per-component style overrides, then applies and visually verifies the preset — component by component and on a generated landing page — in both modes. Use when asked to create a preset, theme, or skin from a URL, mockup, or style description.
---

# Create Theme Preset from: $ARGUMENTS

Deliver a preset that is production-ready on the first review: every component checked, both modes verified, consistent by construction. Analyze the live source at each step — read the actual files, never code the preset system from memory.

## Step 1: Learn the system from source

Read, in this order:

- `packages/ui/src/presets/types.ts`, `helpers.ts`, `palettes.ts` — the `ThemePreset` shape, how fields become CSS vars, the palette catalog with hex values.
- `packages/ui/src/providers/design-system-provider.tsx` — how overrides merge into `baseStyles`.
- Every file in `packages/ui/src/presets/curated/` — current presets are the style guide for your file.
- `packages/common/src/index.css` — `@font-face` catalog (any family name is usable in `typography`), `--typo-*`/`--radius-*` derivations, and the `cs-*` utilities components lean on.
- `packages/ui/src/styles/index.ts` — the component style names; these are the valid `overrides` keys.

Load-bearing mechanics (verify they still hold before relying on them):

- **Override with `extend`, never with full copies.** The provider swaps whole per-component style objects, so a copied definition freezes the base and silently drops future base edits. Instead: `styles({ extend: baseStyles.button, slots: {...}, variants: {...} })` with ONLY the aesthetic delta classes — base structure, layout, and behavior keep flowing through, and `tailwind-merge` resolves your utilities against the base's per group. Register with `defineOverrides({ key: value })` using the exact export names from `styles/index.ts`.
- Extend-delta rules of thumb: replace within the same utility group (`bg-*` → `bg-transparent`, `shadow-*` → `shadow-none`); switching border style needs the explicit pair (`border-solid` to beat a base `border-dashed`); custom `cs-*` utilities can't be twMerge-removed, but appended standard utilities beat their `@apply`-ed declarations in the cascade — verify each such collision with computed styles in the browser. TypeScript quirk: extension `variants` may only reference slots declared in the extension — declare untouched slots as `''` when a variant needs them.
- `typo-label` / `typo-header` / `typo-code` win over `typo-N` size utilities, so voice + size compose (`typo-2 typo-label`). `uppercase` is not part of the typo system — add it per component.
- Preset `radius` scales every `rounded-*` token; `0rem` zeroes all except `rounded-full`. Escape per component with explicit `rounded-none` / `rounded-full`.

## Step 2: Gather the design reference

- **Website URLs**: `WebFetch` each; extract colors, type, shadows, radius, spacing. Follow 2-3 internal links for breadth; screenshot for visual feel.
- **Figma URLs**: parse `fileKey`/`nodeId`, use `get_design_context` + `get_screenshot`.
- **Style brief** (no URL — a description, mockup, or conversation reference): derive the language from the brief; expect to grill more in Step 3.

## Step 3: Grill open decisions

When real choices remain (always for briefs), ask 1-2 rounds of `AskUserQuestion` popups — max 4 questions, first option marked "(Recommended)", descriptions citing actual palette hexes and font names from Step 1. Cover: preset name, neutral, accent, typography voices, shadow character, radius. If the user answers "you decide", stop asking and own the rest. Skip the grill entirely for an unambiguous extraction.

## Step 4: Write the design-language contract

Before any override, write down (in the plan, not the code):

- **Border tiers** — name 2-3 neutral steps and what each means (e.g. ink `12` = standalone structure: cards, popups, primary controls; mid `8` = form controls and fused/secondary chrome: collapsibles, tabs rows, code blocks, chips, media frames). Components nested or fused inside another surface take their HOST's tier — when a pairing looks off, lighten the nested piece toward the host, don't darken siblings.
- **One interaction treatment** — a single hover/pressed/selected recipe reused everywhere.
- **Mode-safe pairings** — palette-step classes flip with mode. `neutral-12`-on-`neutral-1` pairs are always safe (they flip together). Text on solid role fills must be fixed: `text-black` on bright solids (lime, yellow, amber, mint, sky), `text-white` on dark solids (tomato, red, green, blue, violet). When unsure, compute WCAG contrast against the palette's dark-ramp hex.
- **Signature moves** — the few recurring motifs (uppercase mono labels, hairline rules, one pill shape…) each component applies or deliberately skips.

## Step 5: Generate

- **Colors**: map the 6 roles; match role solids against palette step 9, backgrounds against steps 2-3.
- **Every `ThemePreset` field**: copy the default preset's value wherever the reference doesn't clearly differ.
- **Overrides**: sweep ALL of `styles/` in batches, reading each base file right before writing its delta. Override only components whose look must change; keep each delta minimal so the base keeps showing through. Skip empty pass-through styles (many `parameter-*` files).
- **Files**: `presets/curated/{name}.ts` (kebab-case, `{name}Preset` export, existing code style, zero comments) + export in `curated/index.ts`.

## Step 6: Generate the preset landing page

Create a permanent, self-applying showcase at `/presets/{name}` in `apps/design-system`:

- Add `app/presets/{name}-landing.tsx`: a full landing page in the preset's voice — hero with display type and the accent CTA, a ruled stats band, feature cards, a real form (inputs, select, textarea, checkbox, switch), a data section (chart, progress, slider), a chat thread, alerts, footer. Compose only `@digo-labs/ui` components; write copy that fits the aesthetic. Mimic the structure of an existing `*-landing.tsx` if one exists; otherwise pattern from `app/pages` + `app/examples` (verify every component API against an example or its source).
- The page applies its own preset: `useDesignSystem().setPreset({name}Preset)` in a mount effect — it renders correctly no matter the app default.
- Root element needs its own scroll: the app shell is a fixed viewport, so use `h-dvh overflow-y-auto`. The docs app nowraps bare `h1`s — add `whitespace-normal text-balance` to hero headlines.
- Register the shared route once if missing (`/presets/:slug` lazy-loading `../presets/${slug}-landing.tsx`, patterned on ViewPage) and add `presets` to `PATHS`.

## Step 7: Verify in the browser

Use `preview_start` with the `design-system` config. Verify, fix, and re-check until clean — never hand over unseen work:

1. `/presets/{name}` — the landing is the fastest whole-style read and self-applies the preset.
2. `/playground` — near-every component in real DOM; drive its inner scroll container via `javascript_tool`. For popups (menus, selects, tooltips) check computed styles or use real navbar/panel surfaces — docs example iframes are scaled and swallow clicks.
3. A docs component page — checks the preset against docs chrome (preview frame + collapsible + code block border stack).
4. Both modes (mode toggle, or set the `mode` localStorage key and reload) — re-check solid fills, hover/selected states, popups.
5. Consistency audit against the Step 4 contract: fused surfaces on one tier, one interaction recipe, no palette-step text on solid fills.
6. Screenshots after animations settle (pages stagger-fade; a blank shot right after navigation is usually mid-animation — wait 2-3s and re-shoot). If a style refuses to apply, check for hardcoded inline styles in the component source and report them as source-level gaps rather than fighting them.

## Step 8: Finish

1. `npx eslint --fix` on every file you created, then confirm clean.
2. `npx tsc --noEmit` in `packages/ui` and `apps/design-system` (ignore pre-existing failures you didn't cause — but say so).
3. No builds, no commits. Summarize: contract, components overridden, verified surfaces and modes, gaps found, and the `/presets/{name}` URL.

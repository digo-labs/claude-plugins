---
name: create-preset
description: Generate a new theme preset from website or Figma URLs. Extracts colors, typography, shadows, radius, spacing, and component overrides, then maps them to the design system's palette and token system. Use when asked to create a preset, theme, or skin from a URL.
---

# Create Theme Preset from: $ARGUMENTS

## Step 1: Understand the Preset System

Read these files to understand the current state of the preset system:

- `packages/ui/src/presets/types.ts` — the `ThemePreset` interface and all related types
- `packages/ui/src/presets/palettes.ts` — all available palette names and their hex values (use step 9 for matching)
- `packages/ui/src/presets/index.ts` — barrel exports and how `PRESETS` array is auto-built from `curated/`
- `packages/ui/src/presets/curated/index.ts` — curated preset exports (add new ones here)
- All existing preset files in `packages/ui/src/presets/curated/` — to match code style exactly
- `packages/common/src/index.css` — available `--font-*` CSS variables and default `--typo-*` values
- `packages/ui/src/styles/index.ts` — all component style names
- Read **all** style files in `packages/ui/src/styles/` to understand their slot names and variant structures — you will need this for component overrides

## Step 2: Extract Design References

### Website URLs
1. Use `WebFetch` to load each URL in `$ARGUMENTS`. Extract colors, typography, shadows, radius, and spacing from the HTML/CSS.
2. **Auto-explore**: Follow 2-3 internal links from the page to gather a broader picture of the design system (e.g., a subpage, a pricing page, a docs page). Extract design data from each.
3. **Screenshot**: Take a screenshot of each fetched page for visual cross-reference. Use the screenshot to verify and supplement what you extracted from HTML/CSS — especially for shadows, spacing, and overall visual feel.

### Figma URLs
If any URL in `$ARGUMENTS` is a Figma URL (`figma.com/design/...`, `figma.com/make/...`):
1. Parse the `fileKey` and `nodeId` from the URL
2. Use `get_design_context` to extract design tokens (colors, typography, shadows, spacing, radius)
3. Use `get_screenshot` for visual reference
4. Skip the auto-explore step for Figma URLs

## Step 3: Map and Generate

### Colors
Map extracted colors to the 6 required roles (`neutral`, `accent`, `error`, `success`, `warning`, `info`) by comparing extracted hex values against the palette step 9 values from `palettes.ts`. Pick the closest palette for each role.

### Populate every field
`ThemePreset` requires every field except `custom` and `overrides` — the interface enforces it, so populate them all. When an extracted value would be practically identical to the default preset's, copy the default rather than inventing a variation. Specifically:

- **Typography**: Extract font, weight, tracking, leading for header, label, body, and code roles. If the website uses a font not available as a `--font-*` var in `index.css`, map it to the **closest available** `--font-*` var (e.g., a geometric sans → `geist`, a display font → `clash-grotesk`, a monospace → `geist-mono` or `kode-mono`).
- **Shadows**: Extract shadow levels from the website's box-shadows. Map to the 5-level named shadow system (`ShadowProperties` with color, offsetX, offsetY, blur, spread, opacity). Steps are `xs`, `s`, `m`, `l`, `xl`.
- **Radius**: Extract the dominant border-radius value.
- **Spacing**: Set `spacingFactor` — `1` unless the spacing rhythm differs from the default `0.25rem` base.
- **Typography scale**: Set `typographyScaleFactor` — `1` unless the type scale ratio differs from the default.

### Component Overrides
This is critical — understand the website's **design language** from the components visible on the page, then **extrapolate** that language across all design system components:

1. Identify the styling patterns from visible components (border treatments, hover states, focus rings, padding ratios, color usage, transition styles)
2. Read the style files in `packages/ui/src/styles/` to understand each component's slots and variants
3. Generate `overrides` that apply the website's design language consistently across all components — including ones not visible on the source page
4. Only include overrides for components where the result would differ from the base styles

## Step 4: Create Files

1. Create `packages/ui/src/presets/curated/{name}.ts` — match the exact code style (colon alignment, quotes, imports) of the existing presets you read in Step 1
2. Add export to `packages/ui/src/presets/curated/index.ts` — the `PRESETS` array in `index.ts` auto-collects all curated exports

Use kebab-case for filename, camelCase + `Preset` suffix for export name. Do not run any build commands.

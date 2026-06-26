---
name: implement-component
description: Implement a new UI component following the monorepo patterns. Use when asked to create components like Checkbox, Switch, Input, Select, Dialog, etc.
---

# Implement UI Component: $ARGUMENTS

## Step 1: Research External References (Optional)

**Ask the user:** "Is this component based on an external library, or is it an original component?"

- **If original** → skip this step entirely, go to Step 2.
- **If based on an external library** → ask the user for the **docs URL** of the external component (e.g., `https://ui.shadcn.com/docs/components/checkbox`).

Fetch that page, then find the library's GitHub repo and locate the component's source code and examples/demos from there.

Focus on: available sub-components, props API, accessibility behavior, variants/sizes to support, and internal composition.

## Step 2: Learn Project Patterns

Before writing any code, study existing patterns and match them exactly — don't rely on any other skill being installed:

1. **Find similar code** — read 3–5 existing components in `packages/ui/src/components/` and their style files in `packages/ui/src/styles/` *in full*. More is better.
2. **Extract patterns** — naming, file/section structure, import ordering, export style, TypeScript conventions (types vs interfaces, prop typing, generics), composition and helper usage, Tailwind design-system token usage (no arbitrary values), comments, and formatting (indentation, spacing, trailing commas).
3. **Match every pattern** — the new component must look like the existing ones, never generic "best practice" defaults.

## Step 3: Create Files

Create files in this order (component imports the style):

1. **Style file:** `packages/ui/src/styles/{component}.ts`
2. **Register style export in:** `packages/ui/src/styles/index.ts`
3. **Component file:** `packages/ui/src/components/{component}.tsx`
4. **Register component export in:** `packages/ui/src/index.ts`

## Key Requirements

- Wrap Base UI primitives from `@base-ui/react` — never reimplement what Base UI provides
- Follow **exactly** the same patterns as existing components — never do something differently from how they are already done

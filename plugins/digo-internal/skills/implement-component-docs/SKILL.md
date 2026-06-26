---
name: implement-component-docs
description: Create documentation and examples for an existing UI component. Use when asked to document components like Checkbox, Switch, Input, Select, Dialog, etc.
---

# Document UI Component: $ARGUMENTS

## Step 1: Research External References (Optional)

**Ask the user:** "Is this component based on an external library, or is it an original component?"

- **If original** → skip this step entirely, go to Step 2.
- **If based on an external library** → ask the user for the **docs URL** of the external component (e.g., `https://ui.shadcn.com/docs/components/checkbox`).

Fetch that page, then find the library's GitHub repo and locate the component's source code and examples/demos from there.

Focus on:
- Which examples the external library includes and how they group variants
- The actual example source code in the repo (demos, stories, etc.)
- Mirror their example coverage, adapted to your component's actual API

## Step 2: Learn Project Patterns

This is the most important step. Read the **existing documented components** — they define the standard to follow.

1. **Read the component to document:** `packages/ui/src/components/$ARGUMENTS.tsx`
2. **Read the component styles:** `packages/ui/src/styles/$ARGUMENTS.ts`
3. **Read all existing examples:** `apps/design-system/src/app/examples/*.tsx`
4. **Read all existing docs:** `apps/design-system/src/app/docs/*.mdx`

Pay close attention to and replicate exactly:
- How MDX files are structured (headings, prose, `<ComponentPreview>` usage)
- How example files are named (`{component}-{variant}.tsx`)
- How examples import components and apply styles
- The level of detail in descriptions and prop documentation

## Step 3: Create Files

1. **Example files:** `apps/design-system/src/app/examples/{component}-*.tsx`
   - Create examples covering: default usage, variants/sizes, interactive states (disabled, error), and composition with other components where relevant
2. **MDX documentation:** `apps/design-system/src/app/docs/{component}.mdx`

## Key Requirements

- Reference the actual component API (props, slots, data attributes) — don't document props that don't exist
- Create multiple examples when useful covering different use cases, not just the default
- Center examples with `mx-auto` in previews
- Match the formatting, structure, and tone of the existing documented components

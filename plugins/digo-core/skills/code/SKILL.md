---
name: code
description: Write code that follows the Digo design-system patterns, sourced from the docs (llms.txt). Use when asked to create any Digo code — components, pages, hooks, helpers, services, schemas, configs, types, etc. Works in any repo.
---

# Write Code: $ARGUMENTS

Write code that follows the Digo patterns exactly as the **design-system docs** define them. The docs are the single source of truth, and this skill carries no rules of its own — what the docs state is what you apply. Every Digo app follows the same documented patterns, so you reproduce the canonical pattern rather than mining the local codebase. This works from any repo — you never need the monorepo or `node_modules`.

## Step 1: Understand the request

Parse from `$ARGUMENTS`:

- **What kind** of artifact — component, page, hook, helper, service, factory, schema, backend route, provider, state, config, type, test.
- **Where it should live** — the file path in the current app.
- **What it should do.**

## Step 2: Read the docs — everything first, then deep

The docs index is `https://design.digo-labs.com/llms.txt`. Fetch it if it isn't already in the conversation. It lists every page with a one-line description and a raw-`.mdx` link.

1. **Read the whole Development section — every page.** Those pages define every convention and authoring pattern, and all of them apply to all code. Do not skim for the parts that look relevant: a rule you didn't read is a rule you'll break.
2. **Go deep from the index.** Using the one-line descriptions, fetch every page this task specifically touches: the Guide page for any stack area involved (tables, auth, storage, AI, websockets, deployment, …) and the docs page of every `@digo-labs/ui` component or block you'll use — its **API Reference** table is the only source for props, methods, and signatures.

Do not proceed from memory. If it isn't in a page you fetched, you don't know it.

## Step 3: Write the code

Apply **every** convention the docs state — not a subset you judge important. The docs decide; you follow.

- Read the target file only so you can edit it correctly — **do not** copy conventions from sibling local files; the docs define the conventions, and apps converge to the docs.
- Use **only documented APIs**. If a prop, method, or pattern you need is not in the docs, do not invent it — flag it (the docs have a gap to patch with `/audit-docs`) and use the closest documented approach.
- Register exports in the relevant barrel/index as the docs prescribe.

## Step 4: Confirm

Briefly note which doc pages you used, and call out any symbol you couldn't verify against the docs.

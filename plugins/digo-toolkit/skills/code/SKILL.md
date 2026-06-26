---
name: code
description: Write code that matches your personal coding patterns. Use when asked to create any code — components, utilities, hooks, helpers, configs, scripts, types, etc. Dynamically analyzes existing code before writing.
---

# Write Code: $ARGUMENTS

## Step 1: Understand the Request

Parse what is being asked from: `$ARGUMENTS`

Determine:
- **What type** of artifact:component, utility, hook, helper, config, script, type, test, etc.
- **Where it should live** in the project
- **What it should do**

## Step 2: Find Similar Code

Before writing anything, search the codebase for the most similar existing code:

1. **By location** — list files in the target directory and its siblings to understand the neighborhood

2. **By type** — find files of the same kind (e.g., other hooks if writing a hook, other utils if writing a util, other configs if writing a config)

3. **By relevance** — if the new code relates to an existing feature, read that feature's code too

Read at least 3–5 of the closest matches **in full**. More is better. Do not skip this step.

## Step 3: Extract Patterns

From the files you read, identify and document these patterns before writing any code:

- **Naming** — file names, function/variable/type names, casing, prefixes, suffixes
- **File structure** — import ordering, export style (named vs default), section organization
- **TypeScript** — how types/interfaces are defined, generics usage, prop typing conventions
- **Code style** — arrow functions vs declarations, early returns, destructuring habits, ternaries vs if/else
- **Composition** — abstraction level, how things are combined, helper usage
- **Imports** — which packages are used, internal import paths, barrel file conventions
- **Error handling** — validation, edge cases, fallback patterns
- **Comments** — when they're used, tone, density (or absence)
- **Formatting** — indentation, spacing, trailing commas, line break habits

## Step 4: Write the Code

Write code that matches **every pattern** you identified. The output must look like the user wrote it — same habits, same structure, same style.

After writing, register exports in any relevant barrel/index files following the same conventions as existing entries.

## Key Requirements

- NEVER fall back to generic or "best practice" defaults — always match what exists
- Prefer the user's existing abstractions and utilities over introducing new ones
- If the codebase has no similar code, widen the search to adjacent areas
- Match formatting exactly — indentation, spacing, line breaks, trailing commas
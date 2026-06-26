---
name: context
description: Build deep codebase context before feature work. Dynamically analyzes the entire monorepo — packages, styling, services, and how apps consume them. Use before starting new features, or when you need full understanding of the codebase.
---

# Build Codebase Context

Analyze the entire monorepo from scratch to build a deep understanding before feature work begins. Never hardcode anything — discover everything dynamically.

## Step 1: Discover the Monorepo

Read the root `package.json` to find all workspaces. Then read each workspace's `package.json` to understand:
- Package name, entry point, dependencies (internal and external)
- What each package/app is for based on its structure

List the directory contents of each package/app `src/` to understand what's inside.

## Step 2: Deep Dive in Parallel

Launch **3 Explore agents simultaneously**, each with a specific focus. All agents must be **read-only** — no builds, no writes, no installs.

### Agent 1: Shared Packages

Analyze the shared packages (the ones under the packages workspace that are NOT dev-dependencies):

- Read each package's **entry point / index file** to understand what it exports
- Read **representative files** from each major directory within the package to understand patterns
- For each package, understand: what it provides, how it's structured, what conventions it follows
- Pay special attention to: component composition patterns, hook patterns, utility patterns, type/model definitions, service patterns

### Agent 2: Styling System

Analyze the complete styling pipeline:

- Find and read the **global CSS file** with shared utilities (look for utility classes, CSS custom properties, reusable patterns)
- Find and read **style files** (files matching `<name>.ts` in `packages/ui/src/styles/`) — understand how styles are defined
- Find and read the **useStyles hook** and **cn utility** — understand how styles are consumed
- Find and read the **StylesProvider** and any style registration patterns
- Find and read the **Tailwind config** and any **presets**
- Read 3-5 component files to see how the styling pipeline is used end-to-end in practice

### Agent 3: Cross-Package Consumption

Analyze how apps use the shared packages:

- Search app source directories for imports from internal packages (e.g., `@digo-labs/*` or relative paths to packages)
- Identify **which components, hooks, utilities, and services** are most commonly used
- Understand the **patterns of consumption**: how components are composed in pages, how services are initialized and called, how common utilities are used
- Read 3-5 representative app files (pages, layouts, or feature files) to see real usage patterns
- Note any **app-level providers, wrappers, or configuration** that sits between packages and app code

## Step 3: Summarize

Present a **brief, structured summary** of what was learned. Organize by:

1. **Packages overview** — what each package provides and its role in the ecosystem
2. **Component patterns** — how components are built, composed, and exported
3. **Styling pipeline** — the full flow from CSS utilities → style files → useStyles/cn → component usage
4. **Services & data** — how services, API calls, and data flow work
5. **Cross-package connections** — how apps consume shared code, common import patterns
6. **Key conventions** — naming, file structure, TypeScript patterns, anything notable

Keep the summary scannable — use bullet points, not paragraphs. Focus on patterns and connections, not exhaustive file lists.

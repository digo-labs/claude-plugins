---
name: vibe
description: Plan and build complex projects or features inside the monorepo through structured vibe coding. Interviews the user relentlessly, creates a tracked plan, then builds feature-by-feature — always asking, never assuming. Use when user wants to start a new project, vibe code, build something complex, or continue an existing /vibe project.
---

# Vibe Code: $ARGUMENTS

Co-pilot for building projects in this monorepo. You NEVER make decisions alone — every choice goes through the user. The monorepo is a read-only resource library; all project code lives in the target app.

## Resuming Check

First, check if the target app already has a `PLAN.md`. If it does, skip to **Resuming** at the bottom.

## Phase 0: Discovery

Before any questions, build a catalog of what the monorepo offers:

1. Scan ALL MDX files in `apps/design-system/src/app/docs/` — read frontmatter (title, subtitle, section, category) to build a full catalog
2. Read in full any docs whose category is about foundations, styling, or architecture (these teach HOW to build in this monorepo)
3. Keep this catalog in mind for Phase 1 — you'll use it to proactively suggest existing resources

## Phase 1: Grill

Interview the user relentlessly about every aspect of the project. Walk down each branch of the decision tree, resolving dependencies one by one.

**Topics to cover:**
- Project purpose and goals
- Features and functionality
- Pages, views, and navigation
- Data model and state management
- External APIs, services, and backend needs
- User interactions and flows
- Design and look-and-feel
- Tech choices within the monorepo ecosystem
- Target app — existing one or create new?

**Rules:**
- Each answer must trigger follow-up questions — branch deeper until crystal clear
- Decide dynamically when to batch questions (2-3 related) vs go one at a time based on complexity
- Use the popup question format (AskUserQuestion) so the user selects answers
- When the user can't answer: help brainstorm and suggest approaches. If still unclear, flag as TBD
- Provide your recommended answer for each question
- Proactively suggest existing components, effects, and motion presets from the Discovery catalog when relevant to the discussion
- NO important decision left unresolved — the idea must be TOTALLY clear before moving on

## Phase 2: Plan

Once the Grill is complete:

1. Write `PLAN.md` at the root of the target app with all features organized by section
2. Each task gets a status marker: `done` | `in-progress` | `pending`
3. Enter plan mode and present the full plan for approval

## Phase 3: Confirm

Before building, present a checklist of ALL decisions made during the Grill:
- List every decision as a checklist item
- Ask: "Anything missing, wrong, or unclear?"
- Only proceed to Build after explicit approval via plan mode

## Phase 4: Build

Execute the plan feature by feature.

**Before each feature:** explain your approach and ask for confirmation.

**While building:**
- Design choices to make → stop and ask
- Plan needs to change → stop, explain why, ask whether to update the plan or adapt
- Feature complete → start the dev server and visually preview the result
- After preview → run a **quick API check** on that feature's files (see Phase 5 for how, but API validation only — skip pattern analysis)

**Writing code:**
- Before writing ANY code, use Explore agents to find similar code in the monorepo
- Extract patterns: naming, structure, TypeScript conventions, composition, imports, formatting
- Match every pattern — the output must look like the user wrote it
- Primary reference: source code in `packages/ui/src/`. If unclear, check the MDX doc and one demo example from the design-system app
- Use components from `@digo-labs/ui` as-is; create project-local wrappers only if needed
- All project code lives in the target app
- NEVER write to monorepo shared packages without asking the user first

**Never do:**
- Git commits — all git operations belong to the user
- Write to shared packages without explicit permission
- Take design decisions without asking
- Continue building when something is unclear

## Phase 5: Review

Full quality pass after all features are built. Checks every changed file for pattern compliance and correct component API usage.

**1. Collect changed files:**
- Run `git diff --name-only` and `git ls-files --others --exclude-standard` scoped to the target app directory
- Include both modified and new files — skip deleted files
- Filter to code files only (.ts, .tsx, .css, etc.)

**2. Validate component APIs (every changed file):**
- For each file, find every `@digo-labs/ui` component used (imports + JSX)
- Read the actual component source in `packages/ui/src/components/` to get its exported props/types
- Check every prop passed in the changed file exists in the real component API
- Flag: made-up props, wrong prop types, missing required props, deprecated patterns

**3. Check patterns against monorepo code (every changed file):**

For each changed file, follow the same approach as the `/code` skill:
- Find 3–5 similar files in the monorepo (by location, type, and relevance)
- Read them in full and extract patterns: naming, file structure, TypeScript conventions, code style, composition, imports, error handling, comments, formatting
- Compare the changed file against every extracted pattern
- Flag any deviations

This applies to ALL file types — components, hooks, utils, services, types, configs.

**4. Fix issues:**
- Fix all issues found directly — no need to ask per-file
- After fixing, re-run the dev server preview to confirm nothing broke

## Resuming (Existing Project)

When `PLAN.md` already exists:

1. Read `PLAN.md` from the target app
2. Use Explore agents to understand what's been built so far
3. Compare code state to plan progress markers
4. Present current status and ask what to work on next

## Monorepo Resources

Shared packages the project can consume — explore dynamically when needed:
- `packages/ui` — UI components (buttons, inputs, forms, layouts, etc.)
- `packages/common` — Shared utilities, types, constants, CSS, fonts, images
- `packages/services` — API clients, database, storage, realtime, WebSocket services
- `apps/` — Application workspaces (the target project lives here)

Never hardcode patterns from these packages — always discover them fresh from the code.

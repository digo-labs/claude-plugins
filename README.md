# digo-labs Claude Code plugins

A Claude Code plugin **marketplace** for the digo-labs team. It distributes our shared
skills so they work in **any repo**, not just one checkout.

Marketplace name: `digo-labs`

## Plugins

Skills are split by audience and subsystem:

| Plugin | Use it for | Skills |
| --- | --- | --- |
| **digo-base** | any repo, any project | `brainstorm`, `grill-me` |
| **digo-core** | coding in digo core and digo apps | `code`, `code-in-core`, `review`, `context` |
| **digo-ui** | authoring the `@digo-labs/ui` library | `implement-component`, `create-preset` |
| **digo-docs** | the design-system docs site | `implement-component-docs`, `audit-docs` |
| **digo-app** | building apps on `@digo-labs/*` packages | `create-digo-app`, `destroy-digo-app` |

## Install

```shell
/plugin marketplace add digo-labs/claude-plugins
/plugin install digo-base@digo-labs
/plugin install digo-core@digo-labs
/plugin install digo-ui@digo-labs
/plugin install digo-docs@digo-labs
/plugin install digo-app@digo-labs
```

Inside the `digo-labs/core` monorepo every plugin is registered and auto-enabled via that
repo's `.claude/settings.json` — just trust the workspace when prompted. In other repos,
install the ones you need (`digo-base` and `digo-app` are the usual picks outside `core`).

## Invoking skills

Plugin skills are **namespaced by plugin name**:

```shell
/digo-base:brainstorm
/digo-core:code
/digo-ui:implement-component
/digo-docs:audit-docs
/digo-app:create-digo-app
```

## Updates

Plugins track the **latest commit** on `main` (no pinned versions). With
`"autoUpdate": true` set for this marketplace, teammates pick up new pushes on the next
Claude Code startup. To pull manually:

```shell
/plugin marketplace update digo-labs
```

## Contributing

Each skill lives at `plugins/<plugin>/skills/<skill-name>/SKILL.md`. Edit it, commit, push
to `main` — that's the release. To add a skill, create a new folder under the relevant
plugin's `skills/` directory. Keep skills **self-contained**: don't reference another
skill by filesystem path, since plugins are cached independently.

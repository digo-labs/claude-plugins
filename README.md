# digo-labs Claude Code plugins

A Claude Code plugin **marketplace** for the digo-labs team. It distributes our shared
skills so they work in **any repo**, not just one checkout.

Marketplace name: `digo-labs`

## Plugins

| Plugin | Use it in | Skills |
| --- | --- | --- |
| **digo-toolkit** | any repo | `brainstorm`, `grill-me`, `code`, `review`, `vibe`, `audit-docs` |
| **digo-internal** | digo repos (monorepo + design system) | `create-digo-app`, `destroy-digo-app`, `context`, `create-preset`, `implement-component`, `implement-component-docs` |

## Install

```shell
/plugin marketplace add digo-labs/claude-plugins
/plugin install digo-toolkit@digo-labs
/plugin install digo-internal@digo-labs
```

If you work inside the `digo-labs/core` monorepo, both plugins are registered and
auto-enabled for you via that repo's `.claude/settings.json` — just trust the
workspace when prompted.

## Invoking skills

Plugin skills are **namespaced by plugin name**:

```shell
/digo-toolkit:brainstorm
/digo-internal:create-digo-app
```

## Updates

Plugins track the **latest commit** on `main` (no pinned versions). With
`"autoUpdate": true` set for this marketplace, teammates pick up new pushes on the
next Claude Code startup. To pull manually:

```shell
/plugin marketplace update digo-labs
```

## Contributing

Each skill lives at `plugins/<plugin>/skills/<skill-name>/SKILL.md`. Edit it, commit,
push to `main` — that's the release. To add a skill, create a new folder under the
relevant plugin's `skills/` directory.

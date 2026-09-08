---
name: replicate
description: Run any model on Replicate (image, video, audio, 3D) with the shared Digo team token. Use when the user asks to "use replicate", "run a replicate model", "run owner/model on replicate", or names a Replicate model to generate something with. Finds the model, reads its live schema, runs the prediction, saves the outputs.
---

# Replicate

```bash
HELPER="${CLAUDE_SKILL_DIR}/scripts/replicate_run.py"
python3 "$HELPER" setup-check | recommend KIND | schema OWNER/NAME | run OWNER/NAME ... | embed TEMPLATE --out FILE
```

Any system `python3` works. Outputs go under `~/Pictures/image-generations/`; Replicate's own links expire after one hour.

## Token

The token lives only in AWS, as the SSM parameter `/digo/replicate/api-token` in us-east-1. The helper reads it through the AWS CLI with the user's SSO session on every run and never writes it anywhere. Anyone who can log in to the Digo AWS account can generate; billing lands on the company Replicate account.

Run `setup-check` first. When `token.ok` is false, act on the error text and stop:

| Error says | Tell the user |
| --- | --- |
| `Not logged in to AWS` | Run `aws sso login --sso-session productionclub` in your terminal, then ask again. |
| `AWS CLI not found` | `brew install awscli`, then log in as above. |
| `cannot read /digo/replicate/api-token` | That role lacks the read policy; an Identity Center admin follows `references/setup.md` § 3. |
| `does not exist` | The parameter was never created; an admin follows `references/setup.md`. |

Never log in for the user, never print the token, never accept one pasted in chat.

## Pick the model

- A full `owner/name` slug is used as is.
- Otherwise `recommend <kind>` (`image`, `image-edit`, `video`, `image-to-video`, `video-edit`, `music`, `speech`, `3d`, `upscale`) returns Replicate's current recommendation list for that kind, `default` first, each with a one-line purpose. Use the default unless the user's purpose matches another entry; say which model you picked. `requires_key: true` means the provider key must be set on the Replicate account.

## Build the input

`schema owner/name` prints `required`, `choices` (every enum, e.g. `aspect_ratio`, `duration`) and `file_inputs`. Stay inside those. Local files go in as `"@/absolute/path.jpg"` (or a list); the helper uploads them.

## Run

```bash
python3 "$HELPER" run google/nano-banana-2 \
  --input '{"prompt":"…","aspect_ratio":"3:2"}' \
  --out-dir "$HOME/Pictures/image-generations/<project>/round-01" \
  --id 7 --label "Neon sign, rain" --manifest "$HOME/Pictures/image-generations/<project>/round-01/manifest.json"
```

`--id` numbers the result (file `7.webp`, manifest entry `id: 7`); `--parent` records which result it edits; `--manifest` appends id, label, model, input, saved paths, prediction link and any error. Without `--out-dir` files land in `_replicate/<owner>__<model>/` with a timestamp name. The helper polls until done, retries rate limits, and exits with the prediction's error and logs on failure.

`embed page.html --out final.html` replaces every `{{/absolute/path}}` in an HTML file with a data URI (images shrunk to webp, other files as is) and keeps the page under the 16 MB artifact limit. Artifacts cannot load local or remote files, so this is how generated media gets onto a page.

## Rules

- One prediction at a time; a low-credit Replicate account is throttled to one.
- Before video, or more than 10 images in one go, tell the user the count and wait for a yes.
- Never rerun a failed prediction without showing the error first.
- Never change the user's `output_format`.

Admin setup and troubleshooting: `references/setup.md`.

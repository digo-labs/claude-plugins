---
name: create-media
description: Generate images (or video, audio, 3D) on Replicate from a short brief and show every result, numbered, in one artifact per project; iterate or edit by number ("change #12, red background"). Use when the user wants an image, picture, video, clip, sound or 3D asset generated, says "create an image", "make me a", "generate variants", or invokes /create-media.
---

# Create Media

Brief → results on Replicate → one artifact showing every result with its number → the user answers with numbers → next round. Images unless the request says otherwise.

```bash
HELPER="${CLAUDE_SKILL_DIR}/../replicate/scripts/replicate_run.py"
```

The `digo-media:replicate` skill documents the helper (token, `recommend`, `schema`, `run`, `embed`). Load it if anything about running a model is unclear.

## 1. Preflight, no questions

1. `python3 "$HELPER" setup-check`. If `token.ok` is false, relay the fix in one sentence and stop. Usually: run `aws sso login --sso-session productionclub` in your terminal, then ask again.
2. Kind from the request: `image` (default), `video`, `image-to-video` (animate #N), `music`, `speech`, `3d`, `image-edit` (change an existing result).
3. Project folder: `~/Pictures/image-generations/<slug>/`, slug from the request (`tattoo studio hero` → `tattoo-studio-hero`). If `brief.json` exists there, this is a continuation: load it and go to § Iterate. If the request is only feedback and several projects exist, offer the folders in a popup.
4. Reference images must be files on disk. Pasted chat images are not; ask the user to drop them in a folder and name them. `sips -s format jpeg in.heic --out out.jpg` converts HEIC.

## 2. Brief, one popup round

Never ask what the request already says. Recommended option first, marked `(Recommended)`.

1. **Model.** `python3 "$HELPER" recommend <kind>`: offer `default` first, then two or three others with their purpose, then Other. Add "(needs the provider key on the Replicate account)" when `requires_key` is true.
2. **Aspect ratio.** From `schema <model>` → `choices.aspect_ratio` (or the size field the model uses). Preselect `1:1` for images, `16:9` for video. Skip if the model has none.
3. **How many.** 2 · 4 (Recommended) · 6 · 8.
4. **Video only:** duration from `choices.duration`, shortest preselected; resolution when the schema has one.

Before a video round, fetch `https://replicate.com/<owner>/<name>` with WebFetch, read the price, and ask with one line: `4 clips × 8 s on runwayml/gen-4.5 ≈ $19 · Run 4 · Run 2 · Run 1 · Cancel`. If no price is shown, say so and still ask.

## 3. Prompts

One base prompt shared by all results: subject, style, palette, light, camera, what must not appear, and how the frame is filled for the chosen ratio. Then one short direction per result saying what differs: pose, backdrop, composition, mood, camera move. Directions are concrete and distinct; the same prompt is never run N times. When the user gives references, say in the prompt what each image is for. Show the base prompt and the numbered directions in one message before running.

## 4. Generate

Folder `PROJECT/round-NN/` (next free number). Numbers come from `next_id` in `brief.json` (1 for a new project). One call per result, sequential:

```bash
python3 "$HELPER" run <model> --input '{"prompt":"<base + direction>","aspect_ratio":"3:2"}' \
  --out-dir "PROJECT/round-02" --id 7 --label "Neon sign, rain" --manifest "PROJECT/round-02/manifest.json"
```

A failure is retried once; a second failure stays in the manifest as an error and is shown on the page. Then update `brief.json`:

```json
{"title": "Tattoo studio hero", "kind": "image", "model": "google/nano-banana-2", "aspect_ratio": "3:2",
 "base_prompt": "…", "next_id": 9, "finals": [], "artifact": null}
```

## 5. The artifact

Load `artifact-design` the first time in a session, then design the page for this project: whatever layout shows these results best. Not every project looks the same; a set of 4 squares, a run of 16:9 hero candidates, two rounds of edits, or three video clips each call for a different page. Keep it simple and put in only what helps the user choose.

Non-negotiable content: every result with its `#N` and label, the prompt reachable (e.g. in a `<details>`), failed results marked with their error, edits saying which number they came from, finals marked, and when there is more than one round, which round each result belongs to (newest first). Nothing else is required.

Write the HTML to `PROJECT/page.html` with placeholders for media, `<img src="{{/Users/…/round-02/7.webp}}">` or `<video controls src="{{…/4.mp4}}">`, then:

```bash
python3 "$HELPER" embed PROJECT/page.html --out PROJECT/review.html
```

Publish `PROJECT/review.html` with the Artifact tool: first time with `favicon` `🎨` and a one-sentence `description`, store the URL in `brief.json` → `artifact`; later rounds pass that URL as `url` so the same link updates.

## 6. Report

Three lines: the artifact link, the new numbers (`#5–#8`), the folder. Then "tell me the numbers you like and what to change".

## Iterate

- **More of something** (`more like #3`, `#3 and #6 but darker`): fold the liked traits into the base prompt in words, drop what was rejected, write new directions, run § 3–6 as a new round. Pass the liked files as reference inputs when the model has a file input.
- **Edit a result** (`change #12, red background`): find #12 in the manifests. If the current model has a file input (`schema` → `file_inputs`), send `"@<path of #12>"` there with the instruction as prompt. Otherwise use the default of `recommend image-edit` (or `image-to-video` to animate) and say so. New number, `--parent 12`, new round.
- **Finals** (`final: #12 and #15`): one popup for the destination: `~/Pictures/image-generations/<slug>/final/` (Recommended) · `~/Desktop` · `~/Downloads` · Other. Copy as `<slug>-<id>.<ext>`, add the ids to `finals`, republish, say where the files are.

Keep model, ratio and format stable between rounds unless the user asks, so differences come from the prompt.

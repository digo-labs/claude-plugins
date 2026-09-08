#!/usr/bin/env python3
"""Replicate helper for the digo-media plugin.

  setup-check          Verify AWS login and the Replicate token
  recommend KIND       Replicate's currently recommended models for a media kind
  schema OWNER/NAME    Live input schema of a model (choices and file inputs resolved)
  run OWNER/NAME       Run a prediction and save the outputs
  embed TEMPLATE       Replace {{/path/to/file}} placeholders in an HTML file with data URIs

The token lives only in AWS SSM Parameter Store (/digo/replicate/api-token,
us-east-1) and is read through the AWS CLI with the caller's SSO session.
Talks to the Replicate HTTP API with the standard library. A virtualenv with
Pillow is created on first use at ~/.cache/digo-media/venv for `embed`.
"""

from __future__ import annotations

import argparse
import base64
import datetime as _dt
import io
import json
import mimetypes
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
import venv
from pathlib import Path
from typing import Any

OUT_ROOT = Path(os.path.expanduser(os.environ.get("DIGO_MEDIA_OUT", "~/Pictures/image-generations")))
VENV_DIR = Path(os.path.expanduser(os.environ.get("DIGO_MEDIA_HOME", "~/.cache/digo-media"))) / "venv"
API = "https://api.replicate.com"
USER_AGENT = "digo-media-replicate/2.0"
SSM_PARAMETER = os.environ.get("REPLICATE_SSM_PARAMETER", "/digo/replicate/api-token")
SSM_REGION = os.environ.get("REPLICATE_SSM_REGION", "us-east-1")
LOGIN_HINT = "aws sso login --sso-session productionclub"
SETUP_DOC = "references/setup.md"
TERMINAL = ("succeeded", "failed", "canceled")
PAGE_LIMIT = 15 * 1024 * 1024
IMAGE_EXT = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp", ".tif", ".tiff"}

COLLECTIONS = {
    "image": "text-to-image",
    "image-edit": "image-editing",
    "video": "text-to-video",
    "image-to-video": "image-to-video",
    "video-edit": "video-editing",
    "music": "ai-music-generation",
    "speech": "text-to-speech",
    "3d": "3d-models",
    "upscale": "super-resolution",
}

_TOKEN: str | None = None


def ensure_runtime() -> None:
    python = VENV_DIR / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    inside = Path(sys.prefix).resolve() == VENV_DIR.resolve()
    if inside:
        try:
            import PIL  # type: ignore  # noqa: F401
            return
        except ImportError:
            subprocess.run([str(python), "-m", "pip", "install", "--quiet", "--disable-pip-version-check", "pillow>=10"], check=True)
            return
    if not python.exists():
        print(f"[digo-media] creating virtualenv at {VENV_DIR} ...", file=sys.stderr)
        VENV_DIR.parent.mkdir(parents=True, exist_ok=True)
        venv.create(str(VENV_DIR), with_pip=True, clear=True)
        subprocess.run([str(python), "-m", "pip", "install", "--quiet", "--disable-pip-version-check", "pillow>=10"], check=True)
    os.execv(str(python), [str(python), str(Path(__file__).resolve()), *sys.argv[1:]])


def _fail(message: str) -> None:
    raise SystemExit(f"[digo-media] {message}")


def get_token() -> str:
    global _TOKEN
    if _TOKEN:
        return _TOKEN
    aws = shutil.which("aws")
    if not aws:
        _fail(f"AWS CLI not found. Install it (brew install awscli), then run: {LOGIN_HINT}")
    proc = subprocess.run(
        [aws, "ssm", "get-parameter", "--name", SSM_PARAMETER, "--with-decryption",
         "--query", "Parameter.Value", "--output", "text", "--region", SSM_REGION],
        capture_output=True, text=True,
    )
    if proc.returncode == 0 and proc.stdout.strip():
        _TOKEN = proc.stdout.strip()
        return _TOKEN
    lines = proc.stderr.strip().splitlines()
    err = lines[-1] if lines else "unknown error"
    low = err.lower()
    if "accessdenied" in low or "not authorized" in low:
        role = re.search(r"assumed-role/AWSReservedSSO_([A-Za-z0-9]+)_", err)
        who = f"the {role.group(1)} role" if role else "your AWS role"
        _fail(f"{who} cannot read {SSM_PARAMETER}: it lacks ssm:GetParameter. An Identity Center admin adds the policy in {SETUP_DOC}.")
    if "parameternotfound" in low:
        _fail(f"SSM parameter {SSM_PARAMETER} does not exist in {SSM_REGION}. An admin creates it once, see {SETUP_DOC}.")
    if "token has expired" in low or "expired" in low or "unable to locate credentials" in low or "invalidclienttokenid" in low or "error when retrieving token" in low:
        _fail(f"Not logged in to AWS ({err}). Run: {LOGIN_HINT}  and retry.")
    _fail(f"Could not read {SSM_PARAMETER} from SSM: {err}")
    return ""


def _api(method: str, path_or_url: str, body: bytes | None = None, content_type: str | None = None) -> Any:
    url = path_or_url if path_or_url.startswith("http") else API + path_or_url
    headers = {"Authorization": f"Bearer {get_token()}", "Accept": "application/json", "User-Agent": USER_AGENT}
    if content_type:
        headers["Content-Type"] = content_type
    for attempt in range(6):
        req = urllib.request.Request(url, data=body, method=method, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                text = resp.read().decode("utf-8")
                return json.loads(text) if text else {}
        except urllib.error.HTTPError as e:
            text = e.read().decode("utf-8", errors="replace")
            if e.code == 429 and attempt < 5:
                wait = 12 * (attempt + 1)
                print(f"[digo-media] rate limited, retrying in {wait}s ...", file=sys.stderr)
                time.sleep(wait)
                continue
            try:
                payload: Any = json.loads(text)
            except json.JSONDecodeError:
                payload = {"raw": text}
            if isinstance(payload, dict):
                payload.setdefault("http_status", e.code)
            raise SystemExit(json.dumps(payload, ensure_ascii=False, indent=2))
    raise SystemExit(json.dumps({"error": "rate limited 6 times", "http_status": 429}, indent=2))


def _api_json(method: str, path_or_url: str, payload: dict[str, Any] | None = None) -> Any:
    body = json.dumps(payload).encode("utf-8") if payload is not None else None
    return _api(method, path_or_url, body, "application/json" if body else None)


def _download(url: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=600) as resp, dest.open("wb") as f:
        shutil.copyfileobj(resp, f)


def _upload(path: Path) -> str:
    boundary = "----digo-media-" + uuid.uuid4().hex
    mime = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
    head = (f"--{boundary}\r\nContent-Disposition: form-data; name=\"content\"; filename=\"{path.name}\"\r\n"
            f"Content-Type: {mime}\r\n\r\n").encode("utf-8")
    body = head + path.read_bytes() + f"\r\n--{boundary}--\r\n".encode("utf-8")
    result = _api("POST", "/v1/files", body, f"multipart/form-data; boundary={boundary}")
    url = ((result or {}).get("urls") or {}).get("get")
    if not url:
        raise SystemExit(json.dumps({"error": f"upload of {path} returned no URL", "response": result}, indent=2))
    return url


# ---- setup-check -----------------------------------------------------------


def cmd_setup_check(_: argparse.Namespace) -> None:
    result: dict[str, Any] = {"out_root": str(OUT_ROOT)}
    aws = shutil.which("aws")
    if aws:
        proc = subprocess.run([aws, "sts", "get-caller-identity", "--output", "json"], capture_output=True, text=True)
        if proc.returncode == 0:
            ident = json.loads(proc.stdout)
            result["aws"] = {"ok": True, "account": ident.get("Account"), "arn": ident.get("Arn")}
        else:
            lines = proc.stderr.strip().splitlines()
            result["aws"] = {"ok": False, "error": lines[-1] if lines else "unknown", "hint": LOGIN_HINT}
    else:
        result["aws"] = {"ok": False, "error": "AWS CLI not installed", "hint": "brew install awscli"}
    try:
        account = _api_json("GET", "/v1/account")
        result["token"] = {"ok": True, "source": f"ssm:{SSM_PARAMETER} ({SSM_REGION})", "replicate_account": account.get("username")}
    except SystemExit as e:
        result["token"] = {"ok": False, "error": str(e)}
    print(json.dumps(result, indent=2, ensure_ascii=False))
    if not result["token"]["ok"]:
        sys.exit(1)


# ---- recommend -------------------------------------------------------------

_LINK = re.compile(r"\[([^\]]+)\]\(https://replicate\.com/([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)/?\)")


def cmd_recommend(args: argparse.Namespace) -> None:
    slug = COLLECTIONS.get(args.kind.lower(), args.kind)
    collection = _api_json("GET", f"/v1/collections/{slug}")
    description = collection.get("full_description") or ""
    section = ""
    if "## Models we recommend" in description:
        section = description.split("## Models we recommend", 1)[1].split("\n## ", 1)[0]
    recommended: list[dict[str, Any]] = []
    seen: set[str] = set()
    purpose = ""
    for line in section.splitlines():
        text = line.strip()
        if text.startswith("### "):
            purpose = re.sub(r"^For\s+", "", text[4:]).strip()
            continue
        for name, owner_model in _LINK.findall(text):
            if owner_model in seen:
                continue
            seen.add(owner_model)
            low = text.lower()
            recommended.append({"slug": owner_model, "name": name, "purpose": purpose,
                                "requires_key": "api key" in low and "requires" in low})
    if not recommended:
        models = sorted(collection.get("models", []), key=lambda m: m.get("run_count") or 0, reverse=True)
        recommended = [{"slug": f"{m['owner']}/{m['name']}", "name": m["name"], "purpose": "most used", "requires_key": False}
                       for m in models[: args.limit]]
    print(json.dumps({
        "kind": args.kind,
        "collection": slug,
        "default": recommended[0]["slug"] if recommended else None,
        "recommended": recommended[: args.limit],
    }, indent=2, ensure_ascii=False))


# ---- schema ----------------------------------------------------------------


def _inline_refs(node: Any, schemas: dict[str, Any], depth: int = 0) -> Any:
    if depth > 6:
        return node
    if isinstance(node, dict):
        ref = node.get("$ref")
        if isinstance(ref, str) and ref.startswith("#/components/schemas/"):
            target = schemas.get(ref.rsplit("/", 1)[1], {})
            merged = {k: v for k, v in target.items() if k != "title"}
            merged.update({k: v for k, v in node.items() if k != "$ref"})
            return _inline_refs(merged, schemas, depth + 1)
        if isinstance(node.get("allOf"), list):
            merged = {}
            for part in node["allOf"]:
                resolved = _inline_refs(part, schemas, depth + 1)
                if isinstance(resolved, dict):
                    merged.update(resolved)
            merged.update({k: v for k, v in node.items() if k != "allOf"})
            return merged
        return {k: _inline_refs(v, schemas, depth + 1) for k, v in node.items()}
    if isinstance(node, list):
        return [_inline_refs(v, schemas, depth + 1) for v in node]
    return node


def cmd_schema(args: argparse.Namespace) -> None:
    slug = args.slug.strip()
    if ":" in slug:
        owner_model, version = slug.split(":", 1)
        payload = _api_json("GET", f"/v1/models/{owner_model}/versions/{version}")
    else:
        payload = (_api_json("GET", f"/v1/models/{slug}").get("latest_version") or {})
    schemas = payload.get("openapi_schema", {}).get("components", {}).get("schemas", {})
    inputs = _inline_refs(schemas.get("Input", {}), schemas)
    props = inputs.get("properties", {}) if isinstance(inputs, dict) else {}
    choices = {k: v.get("enum") for k, v in props.items() if isinstance(v, dict) and v.get("enum")}
    file_inputs = [k for k, v in props.items() if isinstance(v, dict) and (
        v.get("format") == "uri" or (v.get("type") == "array" and isinstance(v.get("items"), dict) and v["items"].get("format") == "uri"))]
    print(json.dumps({
        "slug": slug,
        "required": inputs.get("required", []) if isinstance(inputs, dict) else [],
        "choices": choices,
        "file_inputs": file_inputs,
        "input": inputs,
    }, indent=2, ensure_ascii=False))


# ---- run -------------------------------------------------------------------


def _is_file_ref(value: Any) -> bool:
    return isinstance(value, str) and value.startswith("@") and Path(os.path.expanduser(value[1:])).is_file()


def _resolve_files(input_dict: dict[str, Any]) -> dict[str, Any]:
    resolved: dict[str, Any] = {}
    for key, value in input_dict.items():
        if _is_file_ref(value):
            resolved[key] = _upload(Path(os.path.expanduser(value[1:])))
        elif isinstance(value, list) and value and all(_is_file_ref(v) for v in value):
            resolved[key] = [_upload(Path(os.path.expanduser(v[1:]))) for v in value]
        else:
            resolved[key] = value
    return resolved


def _flatten(output: Any) -> list[Any]:
    if output is None:
        return []
    if isinstance(output, (list, tuple)):
        return [x for item in output for x in _flatten(item)]
    return [output]


def _save(item: Any, dest: Path, default_ext: str) -> Path:
    if isinstance(item, str) and item.startswith(("http://", "https://")):
        name = os.path.basename(urllib.parse.urlparse(item).path)
        ext = name.rsplit(".", 1)[1].lower() if "." in name else default_ext
        final = dest.with_suffix(f".{ext}")
        _download(item, final)
        return final
    final = dest.with_suffix(".json" if isinstance(item, (dict, list)) else ".txt")
    final.parent.mkdir(parents=True, exist_ok=True)
    final.write_text(json.dumps(item, ensure_ascii=False, indent=2) if isinstance(item, (dict, list)) else str(item), encoding="utf-8")
    return final


def _append_manifest(path: Path, entry: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    entries: list[dict[str, Any]] = []
    if path.is_file():
        try:
            loaded = json.loads(path.read_text(encoding="utf-8"))
            entries = loaded if isinstance(loaded, list) else []
        except json.JSONDecodeError:
            entries = []
    key = "id" if entry.get("id") is not None else "name"
    entries = [e for e in entries if e.get(key) != entry[key]]
    entries.append(entry)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(entries, indent=2, ensure_ascii=False), encoding="utf-8")
    tmp.replace(path)


def cmd_run(args: argparse.Namespace) -> None:
    slug = args.slug.strip()
    if not re.match(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+(:[A-Za-z0-9]+)?$", slug):
        raise SystemExit(f"Use the full owner/model slug, got {slug!r}. Run `recommend <kind>` to find one.")
    raw = args.input or "{}"
    raw_input = json.loads(Path(os.path.expanduser(raw[1:])).read_text(encoding="utf-8")) if raw.startswith("@") else json.loads(raw)
    if not isinstance(raw_input, dict):
        raise SystemExit("--input must be a JSON object")

    owner, name = slug.split(":", 1)[0].split("/", 1)
    out_dir = Path(os.path.expanduser(args.out_dir)) if args.out_dir else OUT_ROOT / "_replicate" / f"{owner}__{name}"
    base = str(args.id) if args.id is not None else _dt.datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
    started = time.monotonic()

    if ":" in slug:
        pred = _api_json("POST", "/v1/predictions", {"version": slug.split(":", 1)[1], "input": _resolve_files(raw_input)})
    else:
        pred = _api_json("POST", f"/v1/models/{slug}/predictions", {"input": _resolve_files(raw_input)})
    get_url = (pred.get("urls") or {}).get("get") or f"/v1/predictions/{pred['id']}"
    deadline = time.monotonic() + args.timeout
    while pred.get("status") not in TERMINAL:
        if time.monotonic() > deadline:
            raise SystemExit(json.dumps({"error": f"prediction {pred.get('id')} still {pred.get('status')} after {int(args.timeout)}s",
                                         "web": (pred.get("urls") or {}).get("web")}, indent=2))
        time.sleep(3)
        pred = _api_json("GET", get_url)

    web = (pred.get("urls") or {}).get("web")
    entry: dict[str, Any] = {
        "id": args.id, "name": base, "label": args.label or base, "slug": slug, "input": raw_input,
        "parent": args.parent, "saved": [], "web": web, "created": _dt.datetime.now().isoformat(timespec="seconds"),
    }
    if pred.get("status") != "succeeded":
        entry["error"] = str(pred.get("error") or pred.get("status"))
        if args.manifest:
            _append_manifest(Path(os.path.expanduser(args.manifest)), entry)
        raise SystemExit(json.dumps({"error": entry["error"], "prediction": pred.get("id"), "web": web,
                                     "logs": (pred.get("logs") or "")[-2000:]}, indent=2, ensure_ascii=False))

    items = _flatten(pred.get("output"))
    default_ext = str(raw_input.get("output_format") or "png").lower()
    for idx, item in enumerate(items):
        stem = base if len(items) == 1 else f"{base}-{idx + 1}"
        entry["saved"].append(str(_save(item, out_dir / stem, default_ext)))
    if args.manifest:
        _append_manifest(Path(os.path.expanduser(args.manifest)), entry)
    print(json.dumps({**entry, "prediction": pred.get("id"), "metrics": pred.get("metrics"),
                      "seconds": round(time.monotonic() - started, 1)}, indent=2, ensure_ascii=False))


# ---- embed -----------------------------------------------------------------

_PLACEHOLDER = re.compile(r"\{\{\s*(/[^}]+?|~/[^}]+?)\s*\}\}")


def _data_uri(path: Path, max_px: int, quality: int) -> str:
    if path.suffix.lower() in IMAGE_EXT:
        from PIL import Image

        im = Image.open(path)
        alpha = im.mode in ("RGBA", "LA") or (im.mode == "P" and "transparency" in im.info)
        im = im.convert("RGBA" if alpha else "RGB")
        im.thumbnail((max_px, max_px), Image.LANCZOS)
        buf = io.BytesIO()
        im.save(buf, "WEBP", quality=quality, method=4)
        return "data:image/webp;base64," + base64.b64encode(buf.getvalue()).decode()
    mime = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
    return f"data:{mime};base64," + base64.b64encode(path.read_bytes()).decode()


def cmd_embed(args: argparse.Namespace) -> None:
    template = Path(os.path.expanduser(args.template)).read_text(encoding="utf-8")
    paths = sorted({Path(os.path.expanduser(m.group(1))) for m in _PLACEHOLDER.finditer(template)})
    missing = [str(p) for p in paths if not p.is_file()]
    if missing:
        raise SystemExit(json.dumps({"error": "placeholder files not found", "missing": missing}, indent=2))
    page = template
    used = (args.max_px, args.quality)
    for max_px, quality in [(args.max_px, args.quality), (720, 78), (560, 74), (420, 70)]:
        if max_px > args.max_px:
            continue
        uris = {str(p): _data_uri(p, max_px, quality) for p in paths}
        page = _PLACEHOLDER.sub(lambda m: uris[str(Path(os.path.expanduser(m.group(1))))], template)
        used = (max_px, quality)
        if len(page.encode("utf-8")) <= PAGE_LIMIT:
            break
    out = Path(os.path.expanduser(args.out))
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(page, encoding="utf-8")
    size = len(page.encode("utf-8"))
    print(json.dumps({"out": str(out), "bytes": size, "files": len(paths), "images_max_px": used[0],
                      "webp_quality": used[1], "over_limit": size > PAGE_LIMIT}, indent=2))


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Replicate helper for the digo-media plugin")
    sub = p.add_subparsers(dest="command", required=True)

    s = sub.add_parser("setup-check", help="Verify AWS login and the Replicate token")
    s.set_defaults(func=cmd_setup_check)

    s = sub.add_parser("recommend", help="Replicate's currently recommended models for a media kind")
    s.add_argument("kind", help=" | ".join(COLLECTIONS) + ", or a collection slug")
    s.add_argument("--limit", type=int, default=6)
    s.set_defaults(func=cmd_recommend)

    s = sub.add_parser("schema", help="Live input schema of a model")
    s.add_argument("slug", help="owner/name or owner/name:version")
    s.set_defaults(func=cmd_schema)

    s = sub.add_parser("run", help="Run a prediction and save the outputs")
    s.add_argument("slug", help="owner/name or owner/name:version")
    s.add_argument("--input", help='JSON object or @file.json; string values "@/path/file" are uploaded', default=None)
    s.add_argument("--out-dir", help="Destination folder (default ~/Pictures/image-generations/_replicate/<owner>__<model>/)", default=None)
    s.add_argument("--id", type=int, help="Result number: names the file and the manifest entry", default=None)
    s.add_argument("--label", help="Short human label for the manifest", default=None)
    s.add_argument("--parent", type=int, help="Id of the result this one edits", default=None)
    s.add_argument("--manifest", help="Append the entry to this manifest.json", default=None)
    s.add_argument("--timeout", type=float, default=1800)
    s.set_defaults(func=cmd_run)

    s = sub.add_parser("embed", help="Replace {{/path/to/file}} placeholders in an HTML file with data URIs")
    s.add_argument("template", help="HTML file with {{/absolute/path}} placeholders")
    s.add_argument("--out", required=True, help="Where to write the final HTML")
    s.add_argument("--max-px", type=int, default=900, help="Longest image side (default 900)")
    s.add_argument("--quality", type=int, default=82, help="WebP quality (default 82)")
    s.set_defaults(func=cmd_embed)
    return p


def main() -> None:
    ensure_runtime()
    args = build_parser().parse_args()
    args.func(args)


if __name__ == "__main__":
    main()

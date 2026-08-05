"""Fill arabic_house_dataset_v2 slots from Freesound (Creative Commons previews).

This automates *free legal* stems. It cannot log into Splice/Loopmasters.

Setup (once) — preferred: repo-local ``.env`` (gitignored):
  1. Create account + API key: https://freesound.org/apiv2/apply
  2. In repo root create ``.env`` with:
       FREESOUND_API_KEY=your_client_secret
  3. Run the commands below (no global Windows env needed)

Usage (repo root):
  PYTHONPATH=. python -m batch_deephouse.datasets.fetch_freesound_stems --dry-run
  PYTHONPATH=. python -m batch_deephouse.datasets.fetch_freesound_stems
  PYTHONPATH=. python -m batch_deephouse.datasets.fetch_freesound_stems --limit 20
"""

from __future__ import annotations

import argparse
import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

DEFAULT_OUT = Path(__file__).resolve().parent / "arabic_house_dataset_v2"
REPO_ROOT = Path(__file__).resolve().parents[2]

# slot basename prefix → Freesound search query (instrument-focused)
SEARCH_FOR_PREFIX: list[tuple[str, str]] = [
    ("oud_", "oud lute solo -song -mix"),
    ("qanun_", "qanun kanun zither arabic -song"),
    ("violin_", "arabic violin middle eastern violin solo"),
    ("ney_", "ney flute arabic nay flute"),
    ("santur_", "santur santoor hammered dulcimer"),
    ("darbuka_", "darbuka doumbek goblet drum loop"),
    ("riq_", "riq frame drum arabic percussion"),
    ("tabla_", "tabla loop percussion"),
    ("kick_", "four on the floor kick drum loop house"),
    ("sub_bass_", "sub bass sine loop deep house"),
    ("hats_", "hihat swing loop closed house"),
    ("pad_", "synth pad warm ambient loop"),
    ("pluck_", "synth pluck loop soft"),
    ("epiano_", "electric piano stab chord house"),
    ("guitar_", "acoustic guitar phrase dry fingerstyle"),
    ("buzuq_", "buzuq bouzouki middle eastern lute"),
]


def load_repo_dotenv(repo_root: Path | None = None) -> Path | None:
    """Load KEY=VALUE pairs from repo ``.env`` into ``os.environ``.

    Overwrites empty existing values. Searches repo root and current working dir.

    Returns:
        Path to ``.env`` if found, else None.
    """
    candidates: list[Path] = []
    root = repo_root or REPO_ROOT
    candidates.append(root / ".env")
    cwd_env = Path.cwd() / ".env"
    if cwd_env.resolve() != candidates[0].resolve():
        candidates.append(cwd_env)

    env_path: Path | None = None
    for path in candidates:
        if path.is_file():
            env_path = path
            break
    if env_path is None:
        return None

    for raw in env_path.read_text(encoding="utf-8-sig").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        if line.startswith("export "):
            line = line[len("export ") :].strip()
        key, _, val = line.partition("=")
        key = key.strip()
        val = val.strip().strip("'").strip('"')
        if not key:
            continue
        # Fill missing or empty env vars from .env
        if key not in os.environ or not str(os.environ.get(key, "")).strip():
            os.environ[key] = val
    return env_path


def _api_key() -> str:
    loaded = load_repo_dotenv()
    key = (os.environ.get("FREESOUND_API_KEY") or "").strip()
    if not key:
        hint = f"Looked for .env at {REPO_ROOT / '.env'} and {Path.cwd() / '.env'}"
        if loaded:
            hint = f"Found {loaded} but FREESOUND_API_KEY was empty"
        raise SystemExit(
            "Missing FREESOUND_API_KEY.\n"
            f"{hint}\n"
            "Create a repo-local .env file (gitignored) with:\n"
            "  FREESOUND_API_KEY=your_client_secret\n"
            "Or export FREESOUND_API_KEY in the shell."
        )
    return key


def _get_json(url: str, key: str) -> dict:
    req = urllib.request.Request(
        url,
        headers={"Authorization": f"Token {key}"},
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _download(url: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(url, headers={"User-Agent": "ACE-Step-stem-fetch/1.0"})
    with urllib.request.urlopen(req, timeout=120) as resp:
        dest.write_bytes(resp.read())


def _search_previews(query: str, key: str, *, page: int = 1) -> list[tuple[str, str]]:
    """Return list of (preview_hq_mp3_url, sound_id)."""
    params = urllib.parse.urlencode(
        {
            "query": query,
            "page": page,
            "page_size": 15,
            "fields": "id,name,previews,license,duration",
            # Allow short one-shots (kicks) and longer phrases
            "filter": "duration:[1 TO 180]",
        }
    )
    url = f"https://freesound.org/apiv2/search/text/?{params}"
    data = _get_json(url, key)
    hits: list[tuple[str, str]] = []
    for item in data.get("results") or []:
        previews = item.get("previews") or {}
        hq = previews.get("preview-hq-mp3") or previews.get("preview-lq-mp3")
        if hq:
            hits.append((str(hq), str(item.get("id"))))
    return hits


def _queries_for(stem_id: str) -> list[str]:
    """Primary + fallback search strings for a slot id."""
    primary = _query_for(stem_id)
    prefix = _prefix_for(stem_id) or ""
    fallbacks: dict[str, list[str]] = {
        "oud_": ["oud", "middle eastern lute", "arabic lute"],
        "qanun_": ["qanun", "kanun", "arabic zither"],
        "violin_": ["violin solo", "fiddle folk", "middle eastern violin"],
        "ney_": ["ney", "nay flute", "arabic flute"],
        "santur_": ["santur", "santoor", "hammered dulcimer"],
        "darbuka_": ["darbuka", "doumbek", "goblet drum"],
        "riq_": ["riq", "frame drum", "tambourine middle eastern"],
        "tabla_": ["tabla", "indian percussion"],
        "kick_": ["kick drum", "house kick", "bass drum one shot"],
        "sub_bass_": ["sub bass", "bass sine", "808 sine"],
        "hats_": ["hihat", "closed hat loop", "house hats"],
        "pad_": ["synth pad", "ambient pad", "warm pad"],
        "pluck_": ["pluck synth", "plucked synth"],
        "epiano_": ["electric piano", "rhodes", "epiano"],
        "guitar_": ["acoustic guitar", "fingerstyle guitar"],
        "buzuq_": ["buzuq", "bouzouki", "saz"],
    }
    out: list[str] = []
    if primary:
        out.append(primary)
    out.extend(fallbacks.get(prefix, []))
    # de-dupe preserve order
    seen: set[str] = set()
    uniq: list[str] = []
    for q in out:
        if q not in seen:
            seen.add(q)
            uniq.append(q)
    return uniq


def _prefix_for(stem_id: str) -> str | None:
    for prefix, _ in SEARCH_FOR_PREFIX:
        if stem_id.startswith(prefix):
            return prefix
    return None


def _query_for(stem_id: str) -> str | None:
    prefix = _prefix_for(stem_id)
    if not prefix:
        return None
    for p, q in SEARCH_FOR_PREFIX:
        if p == prefix:
            return q
    return None


def list_empty_slots(out_dir: Path) -> list[str]:
    """Return stem ids that have .json but no .mp3/.wav."""
    ids: list[str] = []
    for jp in sorted(out_dir.glob("*.json")):
        stem = jp.stem
        if (out_dir / f"{stem}.mp3").exists() or (out_dir / f"{stem}.wav").exists():
            continue
        ids.append(stem)
    return ids


def main() -> int:
    """Fetch CC previews into empty v2 slots."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--limit", type=int, default=0, help="Max downloads (0=all empty)")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--sleep", type=float, default=0.8, help="Seconds between API calls")
    args = parser.parse_args()
    out = args.out
    if not out.is_dir():
        raise SystemExit(f"Missing dataset dir: {out}")

    empty = list_empty_slots(out)
    if args.limit > 0:
        empty = empty[: args.limit]
    print(f"Empty slots: {len(empty)} under {out}")
    if not empty:
        print("Nothing to fetch — all slots already have audio.")
        return 0

    if args.dry_run:
        for stem in empty[:15]:
            print(f"  would fetch: {stem}  queries={_queries_for(stem)!r}")
        if len(empty) > 15:
            print(f"  ... and {len(empty) - 15} more")
        return 0

    key = _api_key()
    ok = 0
    fail = 0
    # cache query -> list of previews; rotate per slot for variety
    cache: dict[str, list[tuple[str, str]]] = {}
    used_ids: set[str] = set()
    slot_index_by_prefix: dict[str, int] = {}

    for stem in empty:
        queries = _queries_for(stem)
        if not queries:
            print(f"SKIP {stem}: no search mapping")
            fail += 1
            continue
        prefix = _prefix_for(stem) or stem
        pick_i = slot_index_by_prefix.get(prefix, 0)
        slot_index_by_prefix[prefix] = pick_i + 1
        chosen: tuple[str, str] | None = None
        try:
            for q in queries:
                if q not in cache:
                    cache[q] = _search_previews(q, key, page=1)
                    time.sleep(args.sleep)
                    if len(cache[q]) < 3:
                        # second page for more options
                        cache[q].extend(_search_previews(q, key, page=2))
                        time.sleep(args.sleep)
                hits = cache[q]
                # prefer unused sound ids; wrap around
                for offset in range(len(hits)):
                    url, sid = hits[(pick_i + offset) % len(hits)]
                    if sid not in used_ids or offset == len(hits) - 1:
                        chosen = (url, sid)
                        used_ids.add(sid)
                        break
                if chosen:
                    break
            if not chosen:
                print(f"MISS {stem}: no Freesound hit for {queries!r}")
                fail += 1
                continue
            url, sid = chosen
            dest = out / f"{stem}.mp3"
            print(f"GET  {stem} ← freesound/{sid}")
            _download(url, dest)
            ok += 1
            time.sleep(args.sleep)
        except urllib.error.HTTPError as exc:
            print(f"HTTP {exc.code} for {stem}: {exc}")
            fail += 1
        except Exception as exc:  # noqa: BLE001 — keep batch going
            print(f"ERR  {stem}: {exc}")
            fail += 1

    print(f"Done. downloaded={ok} failed={fail}")
    print("Re-count: ls the folder for *.mp3 then run train.")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())

"""Generate ~3-min HAYA masters, then smooth-crossfade loop each to 35 min.

No ACE-Step continuation — preserve the approved vocal by repeating the same
3-min take with long exponential acrossfades (~18s) so joins stay musical.
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path

from batch_birthday.ai_stealth import (
    STEALTH_AI_TARGET,
    STEALTH_PITCH_RATES,
    apply_stealth_mp3,
    stealth_pitch_rate_for,
)
from batch_birthday.ai_music_detector import DEFAULT_THRESHOLD, run_ai_detectors
from batch_birthday.humanize_audio import humanize_mp3
from batch_deephouse.acestep_task import generate_to_file
from batch_deephouse.ae_titles import LOCKED_YOUTUBE_SLUGS
from batch_deephouse.extend_mix import build_crossfade_long_mix, probe_duration_sec
from batch_deephouse.haya_signature_recipe import (
    RIMA_COLOR,
    build_signature_lyrics,
    build_signature_payload,
    master_signature_mp3,
)
from batch_deephouse.paths import OUTPUT_DIR

API_BASE = "http://127.0.0.1:8001"
SONG_DURATION = 180  # ~3 min full song
TARGET_35 = 35 * 60
CROSSFADE_SEC = 18.0
BPM = 110

# Locked catalog — same seeds/hooks that earned keep votes (where known).
SONGS: list[dict] = [
    {
        "slug": "hanan",
        "title": "Hanan",
        "hook": "حنان حنان",
        "hook_lines": ["حنان حنان", "ارجع لي بهدوء"],
        "seed": 81201,
        "verse1": [
            "في عيني حنان هادي",
            "يلفّ القلب بلطف",
            "والليل يسمعني",
            "وأنت بعيد عني",
        ],
        "verse2": [
            "كل نفس يقول",
            "ارجع لي بهدوء",
            "والحنان يحضنني",
            "ولحن يبقى معي",
        ],
        "verse3": [
            "الطريق فاضي الليلة",
            "ونبض يسأل عنك",
            "قرب لي شوي",
            "والدنيا تمشي",
        ],
    },
    {
        "slug": "lama",
        "title": "Lama",
        "hook": "لما لما",
        "hook_lines": ["لما لما", "قرب لي بلطف"],
        "seed": 83420,
        "verse1": [
            "لما أشوفك بهدوء",
            "قلبي يلين شوية",
            "والليل يلفّني",
            "وأنت قريب مني",
        ],
        "verse2": [
            "كل لحن ينادي",
            "قرب لي بلطف",
            "والدقات هادية",
            "ونظرة تبقيني",
        ],
        "verse3": [
            "الليل طويل عليّا",
            "وصوتك في بالي",
            "خليك جنبي",
            "ولحن يبقى معي",
        ],
    },
    {
        "slug": "layl",
        "title": "Layl",
        "hook": "يا ليل تعال",
        "hook_lines": ["يا ليل تعال", "خليني معك"],
        "seed": 98101,
        "verse1": [
            "الليل يطول عليّا",
            "والدنيا ساكتة",
            "قلبي ينادي بهدوء",
            "وصوتك في بالي",
        ],
        "verse2": [
            "كل نبضة تقول",
            "قرب لي الليلة",
            "والطريق فاضي",
            "ونظرة تبقيني",
        ],
        "verse3": [
            "يا ليل بلطف",
            "تمشي معايا",
            "والعود يرد",
            "ولحن يبقى معي",
        ],
    },
    {
        "slug": "luma",
        "title": "Luma",
        "hook": "نور الليلة",
        "hook_lines": ["نور الليلة", "خلّيه يضل"],
        "seed": 100434,
        "verse1": [
            "لمعة خفيفة في الليل",
            "تمشي مع أنفاسي",
            "والقلب هادي",
            "ولوما قريبة",
        ],
        "verse2": [
            "كل لحن يضيء",
            "يا نور بلطف",
            "والصوت دافئ",
            "ونظرة تبقيني",
        ],
        "verse3": [
            "الضوء في عيونك",
            "يهدّيني شوي",
            "والليل يصير أهدى",
            "وإنتِ معايا",
        ],
    },
    {
        "slug": "mira",
        "title": "Mira",
        "hook": "ميرا ميرا",
        "hook_lines": ["ميرا ميرا", "يا ميرا بلطف"],
        "seed": 93722,
        "verse1": [
            "ميرا في عيني الليلة",
            "تمشي بهدوء على الطريق",
            "والدقات ثابتة",
            "وإنتِ قريبة مني",
        ],
        "verse2": [
            "كل لحن ينادي",
            "يا ميرا بلطف",
            "والعود يرد خفيف",
            "ونظرة تبقيني",
        ],
        "verse3": [
            "الليل هادي عليّا",
            "وميرا في بالي",
            "قرب لي شوي",
            "ولحن يبقى معي",
        ],
    },
    {
        "slug": "noura",
        "title": "Noura",
        "hook": "نورة نورة",
        "hook_lines": ["نورة نورة", "ارجع لي بهدوء"],
        "seed": 90317,
        "verse1": [
            "في عيني نورة هادية",
            "يلفّ القلب بلطف",
            "والليل يسمعني",
            "وأنت بعيد عني",
        ],
        "verse2": [
            "كل نفس يقول",
            "ارجع لي بهدوء",
            "والنور يحضنني",
            "ولحن يبقى معي",
        ],
        "verse3": [
            "كل ضوء ينادي",
            "يا نورة بلطف",
            "والعود يرد",
            "ونظرة تبقيني",
        ],
    },
    {
        "slug": "qamar",
        "title": "Qamar",
        "hook": "قمر قمر",
        "hook_lines": ["قمر قمر", "ارجع لي بلطف"],
        "seed": 89244,
        "verse1": [
            "قمر على الطريق",
            "يمشي معايا الليلة",
            "والدقات ثابتة",
            "وأنت بعيد عني",
        ],
        "verse2": [
            "كل ضوء ينادي",
            "ارجع لي بلطف",
            "والساب دافئ",
            "ونظرة تخلّيني",
        ],
        "verse3": [
            "الليل طويل",
            "وقمر في بالي",
            "قرب لي بهدوء",
            "ولحن يبقى معي",
        ],
    },
    {
        "slug": "rana",
        "title": "Rana",
        "hook": "ارجعي لي",
        "hook_lines": ["ارجعي لي", "ما تبعدي الليلة"],
        "seed": 100212,
        "verse1": [
            "الطريق فاضي الليلة",
            "وصوتك بعيد",
            "قلبي ينادي بهدوء",
            "ورنا في خيالي",
        ],
        "verse2": [
            "كل كلمة تقول",
            "ارجعي لي بلطف",
            "والدقات ثابتة",
            "ولحن يبقى معي",
        ],
        "verse3": [
            "الليل يطول عليّا",
            "ونبض يسأل عنك",
            "خليك جنبي شوي",
            "والدنيا تمشي",
        ],
    },
    {
        "slug": "rima",
        "title": "Rima",
        "hook": "ريما ريما",
        "hook_lines": ["ريما ريما", "يا ريما اقتربي"],
        "seed": 91501,
        "verse1": [
            "ريما بتغني في بالي",
            "والطريق فاضي الليلة",
            "والدقات ثابتة",
            "وإنتِ بعيدة عني",
        ],
        "verse2": [
            "كل كلمة تنادي",
            "يا ريما اقتربي",
            "والعود يرد بلطف",
            "ونظرة تخلّيني",
        ],
        "verse3": [
            "الليل هادي",
            "وريما في خيالي",
            "قرب لي شوي",
            "ولحن يبقى معي",
        ],
    },
    {
        "slug": "safa",
        "title": "Safa",
        "hook": "صفاء الليلة",
        "hook_lines": ["صفاء الليلة", "هدّيني شوي"],
        "seed": 100545,
        "verse1": [
            "الصوت ناعم عليّا",
            "والليل صافي",
            "صفاء في بالي",
            "والدنيا ساكتة",
        ],
        "verse2": [
            "كل نبضة تقول",
            "يا صفاء بهدوء",
            "والعود يرد",
            "ولحن يبقى معي",
        ],
        "verse3": [
            "الهوا خفيف الليلة",
            "وقلبي يرتاح",
            "قرب لي بلطف",
            "ونظرة تخلّيني",
        ],
    },
]


def _fix_verse(lines: list[str]) -> list[str]:
    """Replace accidental non-Arabic production words."""
    return [ln.replace("والساب دافئ", "والصوت دافئ") for ln in lines]


def _build_lyrics(spec: dict) -> str:
    """Rima-shape lyrics with short soft open + full form for ~3 min."""
    motif = spec["hook_lines"][0]
    hook_block = "\n".join(spec["hook_lines"])
    v1 = "\n".join(_fix_verse(spec["verse1"]))
    v2 = "\n".join(_fix_verse(spec["verse2"]))
    v3 = "\n".join(_fix_verse(spec["verse3"]))
    return f"""[Intro]
(soft female hum mmm ~4–8s only — light pad under vocal)
(main beat enters by 8 seconds)

[Verse]
{v1}

[Chorus]
{hook_block}
{motif}

[Verse]
{v2}

[Chorus]
{hook_block}
{motif}
{motif}

[Bridge]
{motif}
(soft oud answer)

[Chorus]
{hook_block}
{motif}

[Verse]
{v3}

[Chorus]
{hook_block}
{motif}
{motif}

[Outro]
{motif}
(soft natural fade)
"""


def generate_3min(spec: dict) -> Path:
    """Generate one ~3-min humanized master → ``{slug}_3min.mp3``."""
    slug = spec["slug"]
    out_dir = OUTPUT_DIR / slug
    out_dir.mkdir(parents=True, exist_ok=True)
    lyrics = _build_lyrics(spec)
    (out_dir / "lyrics_3min.txt").write_text(lyrics, encoding="utf-8")
    raw = out_dir / f"{slug}_3min_raw.mp3"
    payload = build_signature_payload(
        hook=spec["hook"],
        slug=slug,
        lyrics=lyrics,
        seed=spec["seed"],
        duration=SONG_DURATION,
        color_note=RIMA_COLOR,
        motif_note=f"sticky '{spec['hook']}' after short soft vocal open",
    )
    print(f"GENERATE 3min {slug} seed={spec['seed']}")
    generate_to_file(
        payload,
        api_base=API_BASE,
        api_key="",
        out_path=raw,
        label=f"{slug}_3min",
    )
    listen, ai = master_signature_mp3(raw, slug=f"{slug}_3min")
    # Canonical short name for looping
    three = out_dir / f"{slug}_3min.mp3"
    shutil.copy2(listen, three)
    print(f"OK 3min {slug} → {three} ai≈{ai:.4f} dur={probe_duration_sec(three):.1f}s")
    return three


def _harden_excerpt(src: Path, dst: Path, *, slug: str) -> float:
    """Stealth-harden long mix; score on mid excerpt."""
    import subprocess
    import tempfile

    preferred = stealth_pitch_rate_for(slug)
    candidates = [preferred, *[r for r in STEALTH_PITCH_RATES if r != preferred]]
    best_rate, best_ai = preferred, 1.0
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp = Path(tmp_dir)
        excerpt = tmp / "ex.mp3"
        subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-ss",
                "90",
                "-t",
                "90",
                "-i",
                str(src),
                "-c:a",
                "libmp3lame",
                "-b:a",
                "192k",
                str(excerpt),
            ],
            check=True,
            capture_output=True,
        )
        for rate in candidates:
            cand = tmp / f"s_{rate:.4f}.mp3"
            apply_stealth_mp3(excerpt, cand, pitch_rate=rate)
            dets = run_ai_detectors(cand, threshold=DEFAULT_THRESHOLD)
            ai = dets[0].ai_probability if dets else 1.0
            print(f"  stealth rate={rate:.4f} ai≈{ai:.4f}")
            if ai < best_ai:
                best_ai, best_rate = ai, rate
            if ai <= STEALTH_AI_TARGET:
                break
        apply_stealth_mp3(src, dst, pitch_rate=best_rate)
    return best_ai


def package_smooth_35(slug: str, three_min: Path) -> Path:
    """Loop the 3-min master with smooth 18s acrossfades → ``{slug}_35min.mp3``."""
    out_dir = OUTPUT_DIR / slug
    import tempfile

    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp = Path(tmp_dir)
        raw_long = tmp / "long_raw.mp3"
        human = tmp / "long_human.mp3"
        final_tmp = tmp / "long_final.mp3"
        build_crossfade_long_mix(
            three_min,
            raw_long,
            target_sec=float(TARGET_35),
            crossfade_sec=CROSSFADE_SEC,
            fade_in_sec=6.0,
            fade_out_sec=12.0,
        )
        print(f"  looped → {probe_duration_sec(raw_long):.1f}s (xf={CROSSFADE_SEC}s)")
        humanize_mp3(raw_long, human, style="distribute", bpm=BPM)
        ai = _harden_excerpt(human, final_tmp, slug=slug)
        final = out_dir / f"{slug}_35min.mp3"
        # Keep 3min + 35min only (plus lyrics)
        for child in list(out_dir.iterdir()):
            if child.name in {f"{slug}_3min.mp3", "lyrics_3min.txt"}:
                continue
            if child.is_file():
                child.unlink(missing_ok=True)
            elif child.is_dir():
                shutil.rmtree(child)
        shutil.copy2(final_tmp, final)
        print(f"  KEEP {final.name} (+ {slug}_3min.mp3) ai≈{ai:.4f}")
    return out_dir / f"{slug}_35min.mp3"


def main() -> None:
    """Generate 3-min songs then smooth-loop to 35 min for locked catalog."""
    by_slug = {s["slug"]: s for s in SONGS}
    results = []
    for slug in LOCKED_YOUTUBE_SLUGS:
        spec = by_slug[slug]
        three = generate_3min(spec)
        long = package_smooth_35(slug, three)
        results.append(
            {
                "slug": slug,
                "three_min": str(three),
                "thirty_five": str(long),
                "duration_3min": probe_duration_sec(three),
                "duration_35min": probe_duration_sec(long),
                "recipe": "3min signature + smooth 18s acrossfade loop",
            }
        )
        (OUTPUT_DIR / "_youtube_35min_summary.json").write_text(
            json.dumps(results, indent=2), encoding="utf-8"
        )
    print(f"DONE {len(results)} songs (3min + smooth 35min)")


if __name__ == "__main__":
    main()

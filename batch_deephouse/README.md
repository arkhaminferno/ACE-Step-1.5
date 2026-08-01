# batch_deephouse

Instrumental **chill deep house** project for ACE-Step.

Goal: build a YouTube channel of long deep-house sessions.  
**Phase 1:** lock a 2-minute pilot with a sticky signature melody.  
**Phase 2:** extend approved tracks toward longer / ~1-hour builds.  
**Video:** later (you’ll bring an After Effects template).

## Style target

Inspired by [Ferdaus Mix](https://www.youtube.com/@FerdausMix) Arabic Deep Chill / Dark Mood
(e.g. [Dark Mood — نيرفانا](https://www.youtube.com/watch?v=TdYo9tOOTic)) — **not a copy**:

- Soft deep-chill groove (coding / night drive / calm gym) — **not** dancefloor
- Sticky **oud / oriental** signature melody (separate from the beat)
- Emotional **Arabic** vocals
- Deep bass + dark cinematic atmosphere
- ~108 BPM moody pulse

## Layout

```
batch_deephouse/
├── input/tracks.csv          # catalog (slug = song name, e.g. yalil)
├── metadata/metadata.json    # Chrome extension import (YouTube autofill)
├── output/{slug}/            # yalil.mp3, yalil_human.mp3, yalil.json
├── prompts.py
├── generator.py
├── publish_metadata.py       # export metadata for extension
└── HOW_TO_USE.md
```

Folders use the **song name only** (`yalil`), not `haya-01-yalil-pulse-35m`.

## Brand

**Channel:** HAYA · **Handle:** `@hayamusic`

## Current song

| Field | Value |
|-------|--------|
| Title | Yalil |
| Slug / folder | `yalil` |
| Short | (merged into full track) |
| Original | `output/yalil/yalil.mp3` (~35m) |
| Upload | `output/yalil/yalil_human.mp3` (same audio for now) |
| Metadata | `output/yalil/yalil.json` + `metadata/metadata.json` |
| BPM | **110** · D minor · female Arabic |

## Commands

```bash
# From ACE-Step-1.5 root — start API in another terminal first
./batch_deephouse/scripts/start_acestep_api.sh

PYTHONPATH="$PWD" python_embeded/bin/python3.11 -m batch_deephouse --list
PYTHONPATH="$PWD" python_embeded/bin/python3.11 -m batch_deephouse --slug yalil --force --deliver

# Export YouTube autofill metadata for the Chrome extension
PYTHONPATH="$PWD" python_embeded/bin/python3.11 -m batch_deephouse export-metadata
```

Import `batch_deephouse/metadata/metadata.json` in the extension (same flow as birthday songs).

See `HOW_TO_USE.md` for the full workflow.

# batch_soulcalm

Instrumental night music **to overthink or fall asleep** — like channels such as
[i miss her.](https://www.youtube.com/@imissher.ambient).

## Concept

- **Audio USP:** soft piano + warm retro ambient pads (instrumental only)
- **Video:** one full-frame still of her — fade in → hold → fade out
- No titles / watermark / copyright text on the video

## Length plan

| Phase | Duration | Status |
|-------|----------|--------|
| Sample | **3 min** | generate + approve |
| Longform | **1 hour+** | extend after sample lock |

## First track

| Field | Value |
|-------|--------|
| Title | it's late, you should be asleep |
| Slug | `its_late` |
| Style | instrumental piano + retro ambient |
| BPM | 72 · A minor |
| Sample | `output/its_late/its_late_3min.mp3` |

## Commands

```bash
./batch_deephouse/scripts/start_acestep_api.sh
PYTHONPATH=. ./python_embeded/bin/python3.11 -m batch_soulcalm generate-sample

# After dropping assets/her_still.jpg
PYTHONPATH=. ./python_embeded/bin/python3.11 -m batch_soulcalm render-still
```

# CelebrateVibes / birthday instrument dataset

Stems for DoRA training used by `batch_birthday` (EDM + classic/cover lanes).

## Instruments to include (all of them)

EDM core:
- four-on-floor kick loops
- bright synth / supersaw leads
- deep bass / sub
- crowd claps / hand claps on 2 and 4

Party extras:
- party horns / hype hits
- piano stabs
- pluck leads

Classic / cover lanes:
- grand or upright piano
- acoustic steel-string guitar (fingerstyle)
- light strings
- light drums

## Layout

```
birthday_edm_dataset/
  kick_four_on_floor_128bpm.mp3 + .json + .lyrics.txt
  supersaw_lead_128bpm.mp3 + ...
  acoustic_guitar_cover_110bpm.mp3 + ...
  examples/
```

Instrumental beds → `"language": "unknown"`. Caption must name the instrument clearly.

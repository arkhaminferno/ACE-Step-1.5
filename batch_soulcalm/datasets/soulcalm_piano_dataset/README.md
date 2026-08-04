# SoulCalm piano / pad dataset

Stems for DoRA training used by `batch_soulcalm`.

## Instruments to include (all of them)

Core:
- soft felt piano (many clips — different keys, tempos ~60–80 BPM)
- warm retro synth pads

Experiment extras (add if you have them):
- Rhodes / soft electric piano
- quiet cello or string pad
- soft sub / low pad
- celesta / music box

## Layout

```
soulcalm_piano_dataset/
  felt_piano_amin_70bpm.mp3
  felt_piano_amin_70bpm.json
  felt_piano_amin_70bpm.lyrics.txt
  retro_pad_amin_70bpm.mp3
  ...
  examples/   ← templates
```

Instrumental → `"language": "unknown"`. Caption must name **felt piano** or **pad**.

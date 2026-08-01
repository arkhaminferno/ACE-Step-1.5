# How to use — Deep House pilots

## 1. Start ACE-Step API

```bash
cd /Users/infy/Downloads/ACE-Step-1.5
./batch_deephouse/scripts/start_acestep_api.sh
```

Leave that terminal running. Health check:

```bash
curl -s http://127.0.0.1:8001/health | head
```

## 2. Generate the 2-minute pilot

```bash
cd /Users/infy/Downloads/ACE-Step-1.5
PYTHONPATH="$PWD" python_embeded/bin/python3.11 -m batch_deephouse \
  --slug soft-horizon-deep-house --force
```

Output:

```
batch_deephouse/output/soft-horizon-deep-house/soft-horizon-deep-house.mp3
batch_deephouse/output/soft-horizon-deep-house/soft-horizon-deep-house.json
```

## 3. Listen & decide

Ask:

1. Is the **signature melody** sticky?
2. Is the groove calm enough for background work?
3. Would you play this on loop?

- **Yes** → we extend duration (next step: longer generate / continuation).
- **No** → tweak `mood` / seed in `input/tracks.csv` and regenerate with `--force`.

## 4. Add more pilots

Edit `input/tracks.csv`:

```csv
title,slug,bpm,key_scale,duration_sec,seed,mood,enabled
Soft Horizon,soft-horizon-deep-house,120,A minor,120,42001,"warm night drive...",true
New Title,new-title-deep-house,122,F minor,120,42002,"darker pads, glassy motif",true
```

Then:

```bash
PYTHONPATH="$PWD" python_embeded/bin/python3.11 -m batch_deephouse --limit 1 --force
```

## 5. Not yet

- Video / After Effects (you’ll provide the template later)
- 1-hour renders (only after a pilot is approved)
- YouTube upload metadata (after song lock)

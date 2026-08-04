# HOW TO USE — batch_soulcalm

Instrumental piano + retro ambient (no vocals).

## 1. Start API

```bash
./batch_deephouse/scripts/start_acestep_api.sh
```

## 2. Generate 3-min sample

```bash
PYTHONPATH=. ./python_embeded/bin/python3.11 -m batch_soulcalm generate-sample
```

Listen: `batch_soulcalm/output/its_late/its_late_3min.mp3`

## 3. Video

Put her still at `batch_soulcalm/assets/her_still.jpg`, then:

```bash
PYTHONPATH=. ./python_embeded/bin/python3.11 -m batch_soulcalm render-still
```

## 4. After lock → 1–3 hour longform

Extend the approved instrumental master (do not remaster the long cut).

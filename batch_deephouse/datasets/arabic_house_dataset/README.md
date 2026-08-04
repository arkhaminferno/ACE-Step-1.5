# Arabic House Adapter Dataset (Phase 2)

Dry, high-fidelity instrument stems for DoRA / Side-Step fine-tuning.

## Layout

Pair **every** audio file with matching sidecars (same basename):

```
arabic_house_dataset/
 ├── oud_lead_bayati_120bpm.mp3
 ├── oud_lead_bayati_120bpm.lyrics.txt
 ├── oud_lead_bayati_120bpm.json
 ├── ney_flute_hijaz_120bpm.mp3
 ├── ney_flute_hijaz_120bpm.lyrics.txt
 └── ney_flute_hijaz_120bpm.json
```

Examples / templates live in `examples/`. Drop your real dry stems here
(or into `raw/` then run `auto_label.py`).

## JSON schema

```json
{
  "caption": "A dry, close-mic acoustic Oud solo playing an expressive melody in Maqam Bayati, authentic Middle Eastern lute, minor tonality",
  "bpm": 120,
  "keyscale": "D minor",
  "timesignature": "4",
  "language": "unknown"
}
```

- Instrumental-only → `"language": "unknown"`
- Caption must name **instrument + maqam** (anti guzheng/pipa fallback)
- Keep bpm/key consistent with the filename when possible

## Auto-label

```bash
export PYTORCH_MPS_HIGH_WATERMARK_RATIO=0.0   # macOS
cd /path/to/ACE-Step-1.5
PYTHONPATH="$PWD" python_embeded/bin/python3.11 \
  -m batch_deephouse.datasets.auto_label \
  --dataset-dir batch_deephouse/datasets/arabic_house_dataset \
  --write-lyrics
```

Optional: `--model-id Civitai/acestep-transcriber-FP8` (default) or the
official ACE-Step transcriber id if you prefer.

## Templates in `examples/`

Copy a template, rename to match your stem, drop the `.mp3` beside it:

| Template | Instrument |
|----------|------------|
| `oud_lead_bayati_120bpm.*` | Oud |
| `ney_flute_hijaz_120bpm.*` | Ney |
| `qanun_arpeggio_rast_108bpm.*` | Qanun |
| `violin_lead_bayati_108bpm.*` | Violin |
| `darbuka_tek_108bpm.*` | Darbuka |

## Next (Phase 3)

**Preferred:** train DoRA on a **Windows NVIDIA PC**, then load the adapter on this **Mac** for song generation — see `batch_deephouse/docs/TRAIN_MAC_PC.md`.

```bash
# on the CUDA machine
./batch_deephouse/scripts/phase3_dora_train.sh preprocess
./batch_deephouse/scripts/phase3_dora_train.sh analyze
./batch_deephouse/scripts/phase3_dora_train.sh train
```

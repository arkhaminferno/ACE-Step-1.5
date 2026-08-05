# Where training stems should come from (Arabic v2)

## Do NOT do this

**Do not generate stems with ACE-Step / Recipe 4 / Suno** and then train on them.  
The model will learn its own wrong “guzheng-like” oud/qanun — quality gets worse.

The old files in `arabic_house_dataset/` (oud + ney samples) are optional legacy —  
**prefer this fresh `arabic_house_dataset_v2/` kit** and only real dry audio.

---

## Automate free stems (recommended on Windows)

You **cannot** command-line download Splice/Loopmasters (paid + login).

You **can** auto-fill slots from **Freesound** (Creative Commons previews):

1. Account + API key: https://freesound.org/apiv2/apply  
2. Git Bash:
```bash
cd /c/Users/Inferno/Downloads/ACE-Step-1.5
export FREESOUND_API_KEY=paste_your_key_here
PYTHONPATH=. python -m batch_deephouse.datasets.fetch_freesound_stems --dry-run
PYTHONPATH=. python -m batch_deephouse.datasets.fetch_freesound_stems
find batch_deephouse/datasets/arabic_house_dataset_v2 -iname '*.mp3' | wc -l
```

Quality is “good enough to start,” not studio Kontakt. Replace weak clips later with better packs.

---

## Good sources (pick any mix)

1. **Record real instruments** (best)  
   Phone or interface, close-mic, dry room, 30–90s takes.

2. **Licensed sample libraries / packs** (very good)  
   Kontakt / Native Instruments / Loopmasters / Splice etc.  
   Search: dry oud, qanun, ney, Arabic violin, darbuka one-shots/loops.  
   Export **dry** (little/no reverb), mono or stereo WAV → convert to mp3/wav.

3. **VSTs you own** rendered dry  
   Arabic oud/qanun plugins, drum machines for kick/hats — bounce without big hall reverb.

4. **Your own DAW loops**  
   Ableton/FL/Logic — one instrument per clip, no full mix.

---

## Rules for every clip

- **One instrument** (or one bed element) per file  
- Dry / close — not a full song mix  
- 20–90 seconds is enough  
- Name must match a slot, e.g. `oud_bayati_108_01.mp3` next to `oud_bayati_108_01.json`  
- Caption already names instrument + maqam — don’t train unlabeled mush  

---

## After you drop mp3s

On Windows (repo root):

```bash
export SIDESTEP_DIR="$PWD/Side-Step"
export AUDIO_DIR="$PWD/batch_deephouse/datasets/arabic_house_dataset_v2"
export TENSOR_DIR="$PWD/batch_deephouse/datasets/preprocessed_tensors_arabic_v2"
export OUTPUT_DIR="$PWD/output/arabic_deep_house_dora"

./scripts/train_project_adapter.sh arabic preprocess
./scripts/train_project_adapter.sh arabic analyze
./scripts/train_project_adapter.sh arabic train
```

(Or set those env vars so the arabic project points at v2 — see train script.)

Aim: **fill ≥40 of the scaffolded slots** before a serious train.

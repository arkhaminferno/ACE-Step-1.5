# Full instrument training — all three projects

Train **3 separate DoRA adapters** (do not mix piano into Arabic).
Each adapter’s dataset lists **every instrument that project uses**, plus
common experiment extras so you can try new leads later.

## Master instrument lists

### 1) HAYA / `batch_deephouse` (Recipe 4 + experiments) — **NO concert piano**

| Group | Instruments |
|-------|-------------|
| Arabic leads | oud, qanun, ney/nay, violin, santur |
| Arabic perc | darbuka, riq, (optional) tabla |
| House bed | four-on-floor kick, warm sub bass, swung hats, lush pads |
| Experiment extras | soft pluck, filtered e-piano **stabs only**, acoustic guitar reply, buzuq, mijwiz |

Dataset: `batch_deephouse/datasets/arabic_house_dataset/`  
Adapter out: `output/arabic_deep_house_dora/` → publish to `batch_deephouse/adapters/arabic_deep_house/`

### 2) SoulCalm / `batch_soulcalm`

| Group | Instruments |
|-------|-------------|
| Core | soft **felt piano**, warm retro synth pads |
| Experiment extras | Rhodes / soft EP, quiet cello/strings pad, soft sub, celesta / music-box |

Dataset: `batch_soulcalm/datasets/soulcalm_piano_dataset/`  
Adapter out: `output/soulcalm_piano_dora/` → publish to `batch_soulcalm/adapters/soulcalm_piano/`

### 3) CelebrateVibes / `batch_birthday`

| Group | Instruments |
|-------|-------------|
| EDM core | four-on-floor kick, bright synths / supersaws, deep bass, crowd claps |
| Party extras | party horns, piano stabs, pluck leads |
| Classic / cover lanes | grand/upright piano, acoustic steel-string guitar, light strings, light drums |

Dataset: `batch_birthday/datasets/birthday_edm_dataset/`  
Adapter out: `output/birthday_edm_dora/` → publish to `batch_birthday/adapters/birthday_edm/`

**Windows first-time:** if that folder is empty, copy templates from:
`batch_deephouse/datasets/templates/birthday_edm_dataset/` → `batch_birthday/datasets/birthday_edm_dataset/`

---

## How many stems (full coverage)

| Adapter | Target clips | Notes |
|---------|--------------|--------|
| Arabic | **40–60** | ≥3–5 per instrument above |
| Soulcalm | **25–40** | mostly felt piano + pads |
| Birthday | **40–60** | EDM beds + piano/guitar for classic |
| **Total** | **~105–160** | |

---

## Space (Windows, all three)

| Item | Estimate |
|------|----------|
| Base + VAE (once) | ~5 GB |
| Side-Step / envs | ~10–15 GB |
| All stems | ~2–8 GB |
| Preprocessed tensors (all 3) | ~15–30 GB |
| Epoch checkpoints while training | ~20–40 GB peak (delete after) |
| Final 3 adapters only | ~0.3–0.6 GB |
| **Free disk to keep** | **~120–150 GB** |

After each adapter finishes: delete that run’s `checkpoints/epoch_*` and old tensors if needed.

---

## Time (RTX 5070, full coverage)

| Stage | Per adapter | All 3 |
|-------|-------------|--------|
| Preprocess + analyze | 1–2 h | 3–6 h |
| Train (rank 32, ~300–400 epochs) | **5–12 h** | **~20–35 h** |
| Publish + git push | 20 min | ~1 h |
| **Calendar** | overnight ×1 | **3–5 nights** |

Practical order: Arabic night 1 → Soulcalm night 2 → Birthday night 3.

---

## Commands (from repo root, Git Bash)

```bash
export SIDESTEP_DIR="$PWD/Side-Step"

# One project:
./scripts/train_project_adapter.sh arabic preprocess
./scripts/train_project_adapter.sh arabic analyze
./scripts/train_project_adapter.sh arabic train      # uses rank 32 on 12GB

./scripts/train_project_adapter.sh soulcalm all
./scripts/train_project_adapter.sh birthday all

# Or queue all three (long):
./scripts/train_project_adapter.sh all all
```

Publish after each:
```bash
./scripts/publish_project_adapter.sh arabic best
./scripts/publish_project_adapter.sh soulcalm best
./scripts/publish_project_adapter.sh birthday best
git add batch_deephouse/adapters batch_soulcalm/adapters batch_birthday/adapters
git commit -m "Add project DoRA adapters for Mac inference."
git push
```

On Mac: `git lfs pull && git pull`, then load the adapter for the project you generate.

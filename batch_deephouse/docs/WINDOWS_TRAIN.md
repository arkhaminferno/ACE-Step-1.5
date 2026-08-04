# Windows training — step by step + time + push adapter for Mac

## Time estimates (NVIDIA GPU)

| Stage | 20–50 stems | Notes |
|-------|-------------|--------|
| Setup (clone, `uv`, download base) | 30–90 min | Once |
| Preprocess | **15–60 min** | ~1–3 min/clip on RTX 40-series |
| Analyze (PP++) | **10–40 min** | Fisher map for DoRA ranks |
| Train DoRA (rank 64, ~200–500 epochs) | **3–12 hours** | RTX 4090 faster; 3060/4060 longer |
| Export + commit `best` via Git LFS | **10–20 min** | Adapter ~80–200 MB |

With only **2** stems: training finishes sooner (~1–3 h) but quality will be **weak** — collect 20+ first.

Mac M4 Pro: use for **generate only** after `git pull` (minutes per song).

---

## Windows one-time setup

1. Install **Git**, **Git LFS**, **NVIDIA drivers**, **CUDA-capable GPU ≥16 GB VRAM**.
2. Install [uv](https://docs.astral.sh/uv/).
3. Clone / pull this repo:

```bat
git lfs install
git clone https://github.com/arkhaminferno/ACE-Step-1.5.git
cd ACE-Step-1.5
git pull
```

4. Ensure `checkpoints\acestep-v15-base` exists (same as Mac — copy from Mac USB or re-download).
5. Side-Step (already vendored as `Side-Step/` in repo, or sibling):

```bat
cd Side-Step
install_windows.bat
cd ..
```

6. Put stems in:

```
batch_deephouse\datasets\arabic_house_dataset\
  my_oud.mp3
  my_oud.json
  my_oud.lyrics.txt
  ...
```

Copy JSON templates from `examples\`.

---

## Train (Git Bash or WSL from repo root)

```bash
export SIDESTEP_DIR="$PWD/Side-Step"   # if using in-repo Side-Step
./batch_deephouse/scripts/phase3_dora_train.sh preprocess
./batch_deephouse/scripts/phase3_dora_train.sh analyze
./batch_deephouse/scripts/phase3_dora_train.sh train
```

Or PowerShell equivalent via `Side-Step\sidestep.bat` — see Side-Step README.

Output:

```
output/arabic_deep_house_dora/
  best/          ← use this for Mac
  final/
  checkpoints/   ← do NOT push all of these (huge)
```

Optional export:

```bash
./batch_deephouse/scripts/export_dora_adapter.sh best
```

---

## Push trained adapter so Mac can `git pull`

**Do not** push every epoch or `training_state.pt` (GBs). Push only the **inference adapter**.

### Path we use in this repo

```
batch_deephouse/adapters/arabic_deep_house/
  README.md
  best/
    adapter_config.json
    adapter_model.safetensors   ← Git LFS
  ADAPTER_META.json             ← seed, epochs, date, notes
```

### On Windows after training

```bash
# from ACE-Step-1.5 root
./batch_deephouse/scripts/publish_adapter_to_repo.sh best
git add batch_deephouse/adapters/arabic_deep_house
git commit -m "$(cat <<'EOF'
Add Arabic deep-house DoRA adapter for Mac inference.

EOF
)"
git push origin HEAD
```

Requires **Git LFS** (`.gitattributes` tracks `*.safetensors`).

### On Mac

```bash
git lfs install
git pull
# start API :8001, then:
./batch_deephouse/scripts/load_arabic_adapter_mac.sh best 0.45
# generate Recipe 4 songs as usual
```

The Mac loader resolves `batch_deephouse/adapters/arabic_deep_house/best` when present
(see `batch_deephouse/dora_checkpoint.py` / publish script).

---

## Checklist

- [ ] 20+ dry stems + JSON on Windows  
- [ ] `acestep-v15-base` on Windows  
- [ ] Side-Step installed (`install_windows.bat`)  
- [ ] preprocess → analyze → train  
- [ ] `publish_adapter_to_repo.sh best` + `git push`  
- [ ] Mac: `git pull` + load adapter + Recipe 4  

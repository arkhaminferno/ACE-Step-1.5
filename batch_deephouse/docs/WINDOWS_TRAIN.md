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

## From zero on a fresh Windows PC (RTX 5070)

Yes — you install several things once. Follow **in order**.

**VRAM note:** RTX 5070 is often **12 GB**. Training can work with **rank 32** + lower epochs.
If you OOM, drop to rank 16. Ideal is ≥16 GB, but 12 GB is usable with tight settings.

### 1) NVIDIA driver
- Install latest Studio/Game Ready driver from nvidia.com → reboot  
- Check Task Manager → Performance → GPU shows RTX 5070  

### 2) Git + Git LFS
1. Install **Git for Windows**: https://git-scm.com/download/win  
   (enable “Git from the command line”)  
2. Open **Git Bash**:
```bash
git lfs install
```
If missing: https://git-lfs.com then `git lfs install` again.

### 3) uv
**PowerShell:**
```powershell
irm https://astral.sh/uv/install.ps1 | iex
```
Reopen terminal. Check: `uv --version`

### 4) Clone repo
**Git Bash** (change YOURNAME):
```bash
cd /c/Users/YOURNAME/Documents
git clone https://github.com/arkhaminferno/ACE-Step-1.5.git
cd ACE-Step-1.5
git lfs pull
git pull
```

### 5) Copy ACE-Step base weights from Mac
Copy this folder from Mac USB into the Windows clone:

```
checkpoints/acestep-v15-base/
```

(Also copy `checkpoints/vae` if present.)

### 6) Install Side-Step
```bat
cd Side-Step
install_windows.bat
cd ..
```

### 7) Add stems (do this before train)
Need **20+** dry clips (repo only has 2). Put under:

```
batch_deephouse\datasets\arabic_house_dataset\
```

Each file needs matching `.json` + `.lyrics.txt` (copy from `examples\`).

### 8) Train — Git Bash from repo root

```bash
export SIDESTEP_DIR="$PWD/Side-Step"
./batch_deephouse/scripts/phase3_dora_train.sh preprocess
./batch_deephouse/scripts/phase3_dora_train.sh analyze
```

**Then train (5070 / 12 GB — tight):**
```bash
cd Side-Step
uv run sidestep --yes train \
  --checkpoint-dir ../checkpoints \
  --model base \
  --dataset-dir ../batch_deephouse/datasets/preprocessed_tensors \
  --output-dir ../output/arabic_deep_house_dora \
  --adapter dora \
  --rank 32 \
  --target-modules q_proj k_proj v_proj o_proj condition_embedder \
  --timestep-mode continuous \
  --learning-rate 1e-4 \
  --epochs 400
cd ..
```

If that OOMs, change `--rank 32` → `--rank 16`.

**If you have 16 GB+ VRAM**, you can instead:
```bash
./batch_deephouse/scripts/phase3_dora_train.sh train
```

---

## Train (Git Bash — short form, after setup)

```bash
export SIDESTEP_DIR="$PWD/Side-Step"
./batch_deephouse/scripts/phase3_dora_train.sh preprocess
./batch_deephouse/scripts/phase3_dora_train.sh analyze
./batch_deephouse/scripts/phase3_dora_train.sh train
```

Or PowerShell via `Side-Step\sidestep.bat` — see Side-Step README.
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

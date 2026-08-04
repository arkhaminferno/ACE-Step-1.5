# Train Arabic instruments on PC → produce songs on Mac

## Short answer

| Step | Where | Why |
|------|--------|-----|
| **Train** DoRA/LoRA | **Windows (NVIDIA CUDA)** preferred | Stable VRAM; MPS often OOMs |
| **Generate** songs | **Your Mac (M4 Pro)** | Adapters are portable weight files |

You do **not** need to generate on Windows. Train once on PC → copy the adapter folder / `.safetensors` to this Mac → load it in the ACE-Step API → keep using Recipe 4 here.

Your M4 Pro (24 GB unified) is excellent for **inference**. Full LoRA/DoRA **training** has OOM’d even on **36 GB** Macs ([ACE-Step #282](https://github.com/ace-step/ACE-Step-1.5/issues/282)). Treat Mac training as experimental only.

---

## What you are training

Not a whole new model — a small **adapter** that teaches the existing DiT “what real oud / qanun / ney / violin sound like.”

Pipeline already in this repo:

1. Dry stems + JSON in `batch_deephouse/datasets/arabic_house_dataset/`
2. Side-Step preprocess → tensors
3. Side-Step DoRA train → `output/arabic_deep_house_dora/`
4. Optional export → `.safetensors`
5. Mac: `load_lora` + Recipe 4 generate

---

## Part A — Collect data (can do on Mac)

Put **dry, close-mic** stems (30–90s each is fine; mix of 108 BPM loops helps):

```
batch_deephouse/datasets/arabic_house_dataset/
  oud_....mp3 + .json + .lyrics.txt
  qanun_....mp3 + .json + .lyrics.txt
  ney_....mp3 + .json + .lyrics.txt
  violin_....mp3 + .json + .lyrics.txt
  darbuka_....mp3 + .json + .lyrics.txt   # optional
```

**Target:** 20–50+ clips. You currently have only **2** (oud + ney) — too few for a strong adapter.

JSON must name **instrument + maqam** (see `examples/` and templates). Instrumentals use `"language": "unknown"`.

Copy the whole `arabic_house_dataset/` folder to the Windows PC (USB / cloud / git LFS).

---

Full Windows steps, time table, and **how to push the adapter for Mac `git pull`**:

→ **`batch_deephouse/docs/WINDOWS_TRAIN.md`**

---

## Optional: try train on this Mac anyway?

Only for a **tiny smoke test** (1–2 short clips, rank 16, fp32):

```bash
export PYTORCH_MPS_HIGH_WATERMARK_RATIO=0.0
# expect slow + possible OOM on 24 GB — not for production adapters
```

Prefer cloud GPU (RunPod / Vast / local RTX PC) for the real adapter.

---

## Checklist

- [ ] 20+ dry Arabic instrument stems + JSON  
- [ ] Side-Step on Windows (`install_windows.bat`)  
- [ ] `acestep-v15-base` on the training machine  
- [ ] Train on CUDA → `publish_adapter_to_repo.sh best` → `git push`  
- [ ] Mac: `git lfs pull` → load LoRA → Recipe 4 generate  

# AI Image Generator

Generate images from text prompts using **Stable Diffusion** models (v2.1 and v3.5) via the HuggingFace `diffusers` library.

---

## 📋 Features

- 🎨 **Text-to-image generation** with customizable prompts
- 🖼️ **Two model versions** — Stable Diffusion 2.1 and 3.5
- 📦 **Batch generation** — Generate multiple images from a list of prompts
- ⚡ **GPU acceleration** — Automatic CUDA support for fast inference

---

## 📁 File Structure

| File | Model | Description |
|------|-------|-------------|
| `2-1.py` | Stable Diffusion 2.1 | Batch generation with multiple prompts, 768×768 |
| `3-5.py` | Stable Diffusion 3.5 | Single-prompt generation, 512×512 |

---

## 🚀 Getting Started

### Prerequisites
- Python 3.10+, NVIDIA GPU with CUDA (recommended)

### Installation
```bash
cd AI-Image-Generator
pip install -r requirements.txt
```

### Generate Images
```bash
python 2-1.py    # Stable Diffusion 2.1 (batch)
python 3-5.py    # Stable Diffusion 3.5
```
Images saved as `image_0.png`, `image_1.png`, etc.

---

## 📖 Logic Flow

1. Load StableDiffusionPipeline from HuggingFace
2. Move pipeline to CUDA device
3. Run pipeline with text prompts and inference parameters
4. Save generated images as PNG files

### Key Parameters
| Parameter | 2-1.py | 3-5.py | Purpose |
|-----------|--------|--------|---------|
| `num_inference_steps` | 50 | 28 | Denoising iterations |
| `guidance_scale` | 7.5 | 3.5 | Prompt adherence |
| `height × width` | 768×768 | 512×512 | Output dimensions |

---

## 📦 Dependencies
`diffusers[torch]`, `huggingface_hub`, `transformers`, `accelerate`, `sentencepiece`, `protobuf`

---

## 📝 License
Educational project — use freely for learning and reference.

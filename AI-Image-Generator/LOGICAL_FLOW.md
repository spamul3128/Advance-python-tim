# AI Image Generator — Logical Flow

## 📋 Project Overview
Generates AI images from text prompts using Stable Diffusion models (v2.1 and v3.5) via the HuggingFace diffusers library with GPU acceleration.

---

## 🔄 Stable Diffusion 2.1 Pipeline (2-1.py)

```
┌─────────────────────────────────────────────────────┐
│          Stable Diffusion 2.1 — Batch Mode           │
├─────────────────────────────────────────────────────┤
│                                                     │
│  Load Pre-trained Model                             │
│  (stabilityai/stable-diffusion-2-1)                 │
│       │                                             │
│       ▼                                             │
│  Configure DPMSolverMultistepScheduler              │
│  (Faster inference)                                 │
│       │                                             │
│       ▼                                             │
│  Move Pipeline to CUDA (GPU)                        │
│       │                                             │
│       ▼                                             │
│  ┌─────────────────���───────────┐                    │
│  │   For each prompt in list:  │                    │
│  │       │                     │                    │
│  │       ▼                     │                    │
│  │   Text Encoding             │                    │
│  │       │                     │                    │
│  │       ▼                     │                    │
│  │   Diffusion Process         │                    │
│  │   (50 inference steps)      │                    │
│  │   (768×768 resolution)      │                    │
│  │       │                     │                    │
│  │       ▼                     │                    │
│  │   Decode Latents → Image    │                    │
│  │       │                     │                    │
│  │       ▼                     │                    │
│  │   Save as image_N.png       │                    │
│  └─────────────────────────────┘                    │
│                                                     │
└─────────────────────────────────────────────────────┘
```

---

## 🔄 Stable Diffusion 3.5 Pipeline (3-5.py)

```
┌─────────────────────────────────────────────────────┐
│        Stable Diffusion 3.5 — Single Mode            │
├─────────────────────────────────────────────────────┤
│                                                     │
│  Load Pre-trained Model                             │
│  (stabilityai/stable-diffusion-3.5)                 │
│       │                                             │
│       ▼                                             │
│  Move Pipeline to CUDA (GPU)                        │
│       │                                             │
│       ▼                                             │
│  Single Prompt Input                                │
│       │                                             │
│       ▼                                             │
│  Text Encoding                                      │
│       │                                             │
│       ▼                                             │
│  Diffusion Process                                  │
│  (20 inference steps)                               │
│  (512×512 resolution)                               │
│       │                                             │
│       ▼                                             │
│  Decode Latents → Image                             │
│       │                                             │
│       ▼                                             │
│  Save as image_0.png                                │
│                                                     │
└─────────────────────────────────────────────────────┘
```


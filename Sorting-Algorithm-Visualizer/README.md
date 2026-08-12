# Sorting Algorithm Visualizer

An **interactive sorting algorithm visualizer** built with **Pygame** — watch algorithms sort data in real-time with color-coded animations.

---

## 📋 Features

- 🎨 **Visual Rendering** — Color-coded bar charts showing sorting progress
- 🔄 **Real-time Animation** — Watch swaps and comparisons as they happen
- 📐 **Configurable** — Adjustable number of elements and window size
- 🎮 **Pygame-based** — Smooth rendering with `DrawInformation` class

---

## 🏗️ Architecture

```
Random Data → Pygame Window → Sorting Algorithm → Real-time Bar Chart Updates
                  │
            DrawInformation class
            (manages rendering state)
```

---

## 🚀 Getting Started

```bash
cd Sorting-Algorithm-Visualizer
pip install pygame
python tutorial.py
```

---

## 📖 Logic Flow

1. **Initialize** — `DrawInformation` class sets up Pygame window and rendering params
2. **Generate** — Random data array created
3. **Render** — Bars drawn proportional to values with gradient colors
4. **Sort** — Algorithm executes with yield/callback for each swap
5. **Update** — Pygame redraws bars after each operation
6. **Complete** — Final sorted state displayed

### Key Class: `DrawInformation`
| Attribute | Purpose |
|-----------|---------|
| `width`, `height` | Window dimensions |
| `lst` | Current data array |
| `block_width` | Calculated bar width |
| `start_x` | Drawing offset |
| `GRADIENTS` | Color scheme for bars |

---

## 📦 Dependencies
`pygame`

---

## 📝 License
Educational project — use freely for learning and reference.

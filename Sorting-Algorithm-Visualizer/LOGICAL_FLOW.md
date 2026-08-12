# Sorting Algorithm Visualizer — Logical Flow

## 📋 Project Overview
Interactive real-time visualization of sorting algorithms using Pygame with color-coded animations showing comparisons and swaps.

---

## 🔄 Complete Logical Flow

```
┌──────────────────────────────────────────────────────────────┐
│            Sorting Algorithm Visualizer                       │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  Initialize Application                                      │
│       │                                                      │
│       ▼                                                      │
│  Generate 50 Random Values                                   │
│       │                                                      │
│       ▼                                                      │
│  ┌──────────────────────────────────────┐                    │
│  │  DrawInformation Setup                │                   │
│  │  ├── Pygame window                    │                   │
│  │  ├── Calculate bar widths             │                   │
│  │  ├── Define color gradients           │                   │
│  │  └── Initial bar rendering            │                   │
│  └──────────────┬───────────────────────┘                    │
│                 │                                            │
│                 ▼                                            │
│  ┌──────────────────────────────────────┐                    │
│  │  MAIN EVENT LOOP                      │  ◄────────┐       │
│  │                                       │           │       │
│  │  Keyboard Controls:                   │           │       │
│  │  ├── SPACE → Start/Pause sorting      │           │       │
│  │  ├── R     → Reset with new values    │           │       │
│  │  ├── A     → Ascending order          │           │       │
│  │  ├── D     → Descending order         │           │       │
│  │  ├── B     → Select Bubble Sort       │           │       │
│  │  └── I     → Select Insertion Sort    │           │       │
│  └──────────────┬───────────────────────┘           │       │
│                 │                                    │       │
│            SPACE pressed                             │       │
│                 │                                    │       │
│                 ▼                                    │       │
│  ┌──────────────────────────────────────┐           │       │
│  │  SORTING ANIMATION                    │           │       │
│  │                                       │           │       │
│  │  ┌─────── Bubble Sort ──────┐         │           │       │
│  │  │                          │         │           │       │
│  │  │  For each pass:          │         │           │       │
│  │  │  ├── Compare adjacent    │         │           │       │
│  │  │  ├── Swap if needed      │         │           │       │
│  │  │  ├── Color: GREEN (comp) │         │           │       │
│  │  │  ├── Color: RED (swap)   │         │           │       │
│  │  │  └── yield (pause frame) │         │           │       │
│  │  └──────────────────────────┘         │           │       │
│  │                                       │           │       │
│  │  ┌─────── Insertion Sort ───┐         │           │       │
│  │  │                          │         │           │       │
│  │  │  For each element:       │         │           │       │
│  │  │  ├── Find insert pos     │         │           │       │
│  │  │  ├── Shift elements      │         │           │       │
│  │  │  ├── Color: GREEN (comp) │         │           │       │
│  │  │  ├── Color: RED (shift)  │         │           │       │
│  │  │  └── yield (pause frame) │         │           │       │
│  │  └──────────────────────────┘         │           │       │
│  │                                       │           │       │
│  │  Each yield → Redraw bars             │           │       │
│  └──────────────┬───────────────────────┘           │       │
│                 │                                    │       │
│                 ▼                                    │       │
│  Sorting Complete ──→ Return to event loop ──────────┘       │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

---

## 🎨 Visual Color Coding

```
Default bars:  Gray gradient (3 shades)
Comparing:     GREEN
Swapping:      RED
```


# Photo to Pencil Sketch — Python + OpenCV

Convert any colour photo into a realistic pencil sketch with a simple Tkinter GUI. Beginner-friendly project for learning image processing and GUI basics.

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![OpenCV](https://img.shields.io/badge/OpenCV-4.x-green)
![License](https://img.shields.io/badge/License-MIT-lightgrey)

## Demo

> TODO: Add before/after screenshots for highest impact. Upload to `docs/` then uncomment below:

- Input: `docs/input-example.jpg`
- Output: `docs/output-example.png`

<!-- Uncomment after adding docs/ images:
![Input example](docs/input-example.jpg)
![Output example](docs/output-example.png)
-->

GUI flow: Choose Image → 5-step Matplotlib plot + 300x300 preview → Save Sketch as PNG.

## Features

- Tkinter GUI: Choose Image, Save Sketch, live preview
- Step visualization with Matplotlib: Original, Grayscale, Inverted, Blurred, Pencil Sketch
- One-click PNG export via file dialog
- Works with JPG, JPEG, PNG

## Stack

- `opencv-python` — grayscale, GaussianBlur, divide for dodge blend
- `numpy` — array math
- `matplotlib` — 2x3 step display
- `Pillow` — GUI preview resize (`Image`, `ImageTk`)
- `Tkinter` (stdlib) — file dialogs, buttons, preview label

## Install

```bash
git clone https://github.com/Tarakesh17/colour-photo-to-pencil-sketch-.git
cd colour-photo-to-pencil-sketch-
pip install -r requirements.txt
```

Requires Python 3.8+ on macOS / Windows / Linux. Tkinter ships with stdlib Python (on Linux you may need `sudo apt install python3-tk`).

## Run

```bash
python main.py
```

1. Click "Choose Image"
2. Select JPG / PNG / JPEG
3. View 5-step plot + GUI preview
4. Click "Save Sketch" to export PNG

## How It Works

Pipeline in `process_image(path)` → returns `img, gray, inverted, blurred, sketch`:

1. `grayscale` — BGR → Gray via `cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)`
2. `invert` — `255 - gray`
3. `blur` — `GaussianBlur` `21x21`, `sigmaX=0, sigmaY=0` on inverted image
4. `dodge` — `cv2.divide(gray, 255 - blurred, scale=256)` — core sketch effect
5. Display with Matplotlib + save with `cv2.imwrite`

## Structure

```
.
├── main.py            # GUI + pipeline (renamed from PhotoInversion_proj.py)
├── requirements.txt   # opencv-python, numpy, matplotlib, Pillow
├── README.md
├── LICENSE            # MIT
├── .gitignore
└── docs/
    ├── input-example.jpg   # TODO: add sample input
    └── output-example.png  # TODO: add sample output
```

## Limitations

- Fixed blur kernel `(21,21)` — no slider for line thickness
- Single image at a time, no batch / CLI mode
- Large images (>4000px) are slow in Matplotlib preview
- Tkinter preview fixed at `300x300`, aspect ratio not preserved

## Learnings

- Dodge blend for sketch effect and why blur radius controls stroke weight
- BGR vs RGB handling between OpenCV, Matplotlib, and Pillow
- Basic GUI state handling with `last_sketch` guard before save

## Next Improvements

- [ ] Thickness slider for blur kernel
- [ ] Preserve aspect ratio in preview
- [ ] CLI flags `--input --output` for no-GUI batch use
- [ ] Sample input/output in `docs/`

## License

MIT — see LICENSE file.

Done by Tarakesh.M.K.P

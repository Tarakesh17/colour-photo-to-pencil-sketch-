"""Colour photo → pencil sketch (OpenCV + Tkinter).

Run GUI:
    python main.py

Run headless / batch:
    python main.py --input photo.jpg --output sketch.png
    python main.py --input photo.jpg --output sketch.png --ksize 31 --no-steps
"""

import argparse
import os
import sys

import cv2
import matplotlib.pyplot as plt
from PIL import Image

try:
    import tkinter as tk
    from tkinter import filedialog, messagebox
    from PIL import ImageTk
    HAS_TK = True
except Exception:  # headless / python without _tkinter (e.g. Homebrew) → CLI still works
    tk = None
    filedialog = None
    messagebox = None
    ImageTk = None
    HAS_TK = False


def grayscale(img):
    """BGR image → single-channel gray."""
    return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)


def invert(img):
    """255 - image."""
    return 255 - img


def _normalize_ksize(ksize):
    """Force positive odd kernel size for GaussianBlur."""
    ksize = int(ksize)
    if ksize < 3:
        ksize = 3
    if ksize % 2 == 0:
        ksize += 1
    return ksize


def blur(img, ksize=21):
    """Gaussian blur on inverted gray. ksize must be odd."""
    ksize = _normalize_ksize(ksize)
    return cv2.GaussianBlur(img, (ksize, ksize), sigmaX=0, sigmaY=0)


def dodge(front, back):
    """Dodge blend: front / (255 - back). cv2.divide saturates div-by-zero to 255."""
    return cv2.divide(front, 255 - back, scale=256)


def suggest_ksize(width, height, base=21):
    """Scale blur with image size so small/4K images look right. Keeps odd."""
    m = min(width, height)
    # ~1% of min dimension, clamped to 5..51
    k = max(5, min(51, (m // 100) | 1 if (m // 100) % 2 else (m // 100) + 1))
    # Bias toward caller's base for typical 500-1500px photos
    if 500 <= m <= 1500:
        return _normalize_ksize(base)
    return _normalize_ksize(k)


def process_image(path, ksize=21, auto_ksize=False):
    """Read path → (img, gray, inverted, blurred, sketch).

    Raises FileNotFoundError / ValueError with clear message (no raw crash).
    """
    if not path or not os.path.isfile(path):
        raise FileNotFoundError(f"Image not found: {path}")
    img = cv2.imread(path)
    if img is None:
        raise ValueError(f"Could not decode image (unsupported/corrupt): {path}")
    gray = grayscale(img)
    inverted = invert(gray)
    if auto_ksize:
        h, w = gray.shape
        ksize = suggest_ksize(w, h, base=ksize)
    blurred = blur(inverted, ksize=ksize)
    sketch = dodge(gray, blurred)
    return img, gray, inverted, blurred, sketch


def convert_file(input_path, output_path, ksize=21, auto_ksize=False):
    """Headless single-file conversion. Returns output_path."""
    _, _, _, _, sketch = process_image(input_path, ksize=ksize, auto_ksize=auto_ksize)
    out_dir = os.path.dirname(os.path.abspath(output_path))
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
    if not cv2.imwrite(output_path, sketch):
        raise IOError(f"Failed to write sketch to: {output_path}")
    return output_path


def show_steps(img, gray, inverted, blurred, sketch, block=True):
    """5-panel Matplotlib breakdown. block=False keeps Tkinter responsive."""
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    plt.figure(figsize=(10, 8))
    for i, (title, data, cmap) in enumerate([
        ("Original", img_rgb, None),
        ("Grayscale", gray, "gray"),
        ("Inverted", inverted, "gray"),
        ("Blurred", blurred, "gray"),
        ("Pencil Sketch", sketch, "gray"),
    ], start=1):
        plt.subplot(2, 3, i)
        plt.imshow(data, cmap=cmap)
        plt.title(title)
        plt.axis("off")

    plt.tight_layout()
    plt.show(block=block)
    if not block:
        plt.pause(0.1)


# --- GUI ---
class SketchApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🎨 Pencil Sketch App")
        self.root.geometry("440x620")
        self.root.configure(bg="#f0f8ff")

        self.last_sketch = None

        tk.Label(root, text="Pencil Sketch Converter", font=("Helvetica", 18, "bold"),
                 fg="#003366", bg="#f0f8ff").pack(pady=15)

        # Thickness control (fixes fixed-21 limitation)
        ctrl = tk.Frame(root, bg="#f0f8ff")
        ctrl.pack(pady=5)
        tk.Label(ctrl, text="Stroke thickness:", bg="#f0f8ff", fg="#003366").pack(side="left")
        self.ksize_var = tk.IntVar(value=21)
        tk.Scale(ctrl, from_=5, to=51, resolution=2, orient="horizontal",
                 variable=self.ksize_var, bg="#f0f8ff", length=180).pack(side="left", padx=8)
        tk.Checkbutton(ctrl, text="Auto", bg="#f0f8ff",
                       variable=getattr(self, "_auto_var", None) or self._init_auto_var(ctrl)).pack(side="left")

        tk.Button(root, text="🖼️ Choose Image", command=self.choose_image,
                  font=("Arial", 12), width=20,
                  bg="#4CAF50", fg="white",
                  activebackground="#45a049", activeforeground="white").pack(pady=10)

        tk.Button(root, text="💾 Save Sketch", command=self.save_sketch,
                  font=("Arial", 12), width=20,
                  bg="#2196F3", fg="white",
                  activebackground="#1976D2", activeforeground="white").pack(pady=10)

        self.status = tk.Label(root, text="Pick an image to start", bg="#f0f8ff", fg="#555555")
        self.status.pack(pady=5)

        self.preview_label = tk.Label(root, bg="#f0f8ff")
        self.preview_label.pack(pady=10)

        tk.Label(root, text="Done by Tarakesh.M.K.P", font=("Arial", 10),
                 bg="#f0f8ff", fg="#777777").pack(side="bottom", pady=10)

    def _init_auto_var(self, parent):
        self.auto_var = tk.BooleanVar(value=False)
        return self.auto_var

    def choose_image(self):
        path = filedialog.askopenfilename(
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp *.webp"),
                       ("All files", "*.*")]
        )
        if not path:
            return
        try:
            ksize = self.ksize_var.get()
            auto = self.auto_var.get()
            img, gray, inverted, blurred, sketch = process_image(path, ksize=ksize, auto_ksize=auto)
        except (FileNotFoundError, ValueError) as e:
            messagebox.showerror("Error", str(e))
            return

        self.last_sketch = sketch
        self.status.config(text=f"{os.path.basename(path)} → sketch (k={ksize}{' auto' if auto else ''})")

        # Non-blocking so Tk stays alive (bug fix: old plt.show() froze GUI)
        try:
            show_steps(img, gray, inverted, blurred, sketch, block=False)
        except Exception:
            pass  # preview in GUI still works even if matplotlib backend fails

        # Aspect-preserving preview (bug fix: old resize((300,300)) stretched)
        preview = Image.fromarray(sketch)
        preview.thumbnail((300, 300), Image.LANCZOS)
        tk_preview = ImageTk.PhotoImage(preview)
        self.preview_label.config(image=tk_preview)
        self.preview_label.image = tk_preview

    def save_sketch(self):
        if self.last_sketch is None:
            messagebox.showwarning("Warning", "Please process an image first!")
            return
        save_path = filedialog.asksaveasfilename(defaultextension=".png",
                                                 filetypes=[("PNG files", "*.png"),
                                                            ("JPEG files", "*.jpg")],
                                                 initialfile="sketch.png")
        if save_path:
            if cv2.imwrite(save_path, self.last_sketch):
                messagebox.showinfo("Saved", f"Sketch saved to:\n{save_path}")
            else:
                messagebox.showerror("Error", f"Failed to write:\n{save_path}")


def launch_gui():
    if not HAS_TK:
        print("error: Tkinter is not available in this Python (e.g. Homebrew without tcl-tk). "
              "Use CLI: python main.py --input photo.jpg --output sketch.png",
              file=sys.stderr)
        raise SystemExit(1)
    root = tk.Tk()
    SketchApp(root)
    root.mainloop()


def parse_args(argv=None):
    p = argparse.ArgumentParser(description="Photo → pencil sketch")
    p.add_argument("--input", "-i", help="Input photo path (headless mode)")
    p.add_argument("--output", "-o", help="Output sketch path (headless mode)")
    p.add_argument("--ksize", type=int, default=21, help="Blur kernel (odd, 5-51)")
    p.add_argument("--auto-ksize", action="store_true", help="Scale blur to image size")
    p.add_argument("--no-steps", action="store_true", help="Skip matplotlib step plot")
    return p.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    if args.input or args.output:
        if not args.input or not args.output:
            print("error: --input and --output are required together", file=sys.stderr)
            return 2
        try:
            img, gray, inverted, blurred, sketch = process_image(
                args.input, ksize=args.ksize, auto_ksize=args.auto_ksize)
            convert_file(args.input, args.output, ksize=args.ksize, auto_ksize=args.auto_ksize)
            if not args.no_steps:
                show_steps(img, gray, inverted, blurred, sketch, block=True)
            print(f"Saved sketch to {args.output}")
            return 0
        except (FileNotFoundError, ValueError, IOError) as e:
            print(f"error: {e}", file=sys.stderr)
            return 1
    launch_gui()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

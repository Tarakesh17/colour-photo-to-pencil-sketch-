#colourfull gui[final]

import cv2 #used for image processing (grayscale, blur, invert, etc.)
import numpy as np
import matplotlib.pyplot as plt #Used to display image processing steps in a nice visual layout
import tkinter as tk
from tkinter import filedialog, messagebox #To build the GUI (Graphical User Interface) // Tkinter tools for opening/saving files and showing popups
from PIL import Image, ImageTk
import os

def grayscale(img):
    return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

def invert(img):
    return 255 - img

def blur(img):
    return cv2.GaussianBlur(img, (21, 21), sigmaX=0, sigmaY=0)

def dodge(front, back):
    result = cv2.divide(front, 255 - back, scale=256)
    return result

def process_image(path):
    img = cv2.imread(path)
    gray = grayscale(img)
    inverted = invert(gray)
    blurred = blur(inverted)
    sketch = dodge(gray, blurred)
    return img, gray, inverted, blurred, sketch

def show_steps(img, gray, inverted, blurred, sketch):
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    plt.figure(figsize=(10, 8))
#original
    plt.subplot(2, 3, 1)
    plt.imshow(img_rgb)
    plt.title("Original")
    plt.axis('off')
#grayscale
    plt.subplot(2, 3, 2)
    plt.imshow(gray, cmap='gray')
    plt.title("Grayscale")
    plt.axis('off')
#inverted
    plt.subplot(2, 3, 3)
    plt.imshow(inverted, cmap='gray')
    plt.title("Inverted")
    plt.axis('off')
#blur
    plt.subplot(2, 3, 4)
    plt.imshow(blurred, cmap='gray')
    plt.title("Blurred")
    plt.axis('off')
#pencil sketch
    plt.subplot(2, 3, 5)
    plt.imshow(sketch, cmap='gray')
    plt.title("Pencil Sketch")
    plt.axis('off')

    plt.tight_layout()
    plt.show()
#choose the image from the user
def choose_image():
    path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.png *.jpeg")])
    if not path:
        return

    global last_sketch, last_save_path

    img, gray, inverted, blurred, sketch = process_image(path)
    last_sketch = sketch
    last_save_path = path

    # Display result in matplotlib
    show_steps(img, gray, inverted, blurred, sketch)

    # Show sketch preview in GUI
    preview = Image.fromarray(sketch)
    preview = preview.resize((300, 300))
    tk_preview = ImageTk.PhotoImage(preview)
    preview_label.config(image=tk_preview)
    preview_label.image = tk_preview

def save_sketch():
    if last_sketch is None:
        messagebox.showwarning("Warning", "Please process an image first!")
        return

    save_path = filedialog.asksaveasfilename(defaultextension=".png",
                                             filetypes=[("PNG files", "*.png")],
                                             initialfile="sketch.png")
    if save_path:
        cv2.imwrite(save_path, last_sketch)
        messagebox.showinfo("Saved", f"Sketch saved to:\n{save_path}")

# --- GUI Setup ---
last_sketch = None
last_save_path = ""

root = tk.Tk()
root.title("🎨 Pencil Sketch App")
root.geometry('420x460')
root.configure(bg="#f0f8ff")  # Light pastel background

# Title label
tk.Label(root, text="Pencil Sketch Converter", font=("Helvetica", 18, "bold"),
         fg="#003366", bg="#f0f8ff").pack(pady=15)

# Choose Image Button
tk.Button(root, text="🖼️ Choose Image", command=choose_image,
          font=("Arial", 12), width=20,
          bg="#4CAF50", fg="blue",
          activebackground="#45a049", activeforeground="white").pack(pady=10)

# Save Sketch Button
tk.Button(root, text="💾 Save Sketch", command=save_sketch,
          font=("Arial", 12), width=20,
          bg="#2196F3", fg="red",
          activebackground="#1976D2", activeforeground="white").pack(pady=10)

# Preview label
preview_label = tk.Label(root, bg="#f0f8ff")
preview_label.pack(pady=20)

# Footer
tk.Label(root, text="Done by Tarakesh.M.K.P", font=("Arial", 10),
         bg="#f0f8ff", fg="#777777").pack(side="bottom", pady=10)

root.mainloop()
<!-- PROJECT TITLE -->
#  Mini Image‑Editor CLI

A lightweight, **NumPy‑only** image‑processing tool written in pure Python.  
Feed it a JSON config and it chains brightness, contrast, blur, Sobel‑edge, sharpening, and more—then saves or displays the result.


---

## Features
* **Zero heavy dependencies** – only `numpy`, `imageio`, `matplotlib`
* Declarative **JSON pipelines**—no Python edits to change effects
* Built‑in operations: Brightness, Contrast, Saturation, Box‑blur, Sobel, Sharpen
* Safe I/O: automatic parent‑directory creation, last‑chance clipping, rich error messages
* 100 % type‑annotated & PEP 8‑formatted

---

## Quick start

```bash
# Clone and set up a virtual environment
git clone https://github.com/Raphaelkremer/image-editor.git
cd image-editor
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt   # numpy, imageio, matplotlib

# Run with a sample configuration
python -m src.main --config examples/config08_blur_then_sharpen.json

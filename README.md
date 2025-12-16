# 🖼️ Civitai Metadata Fixer

Fix the **"We couldn't detect valid metadata in this image"** error when uploading to Civitai.

This tool adds Automatic1111-compatible metadata to your PNG images so Civitai can properly detect and display generation parameters.

![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

## 🌐 Live Demo

**[Use it now → civitai-metadata-fixer.vercel.app](https://civitai-metadata-fixer.vercel.app)**

No installation required! Works entirely in your browser.

## ✨ Features

- 🌐 **Web-based UI** - Works in any browser, no desktop dependencies
- 📤 **Drag & Drop** - Simply drag your images onto the page
- 🔍 **Auto-detect** - Parses existing A1111/ComfyUI metadata if present
- ⚡ **One-click Auto-fill** - Instantly add valid metadata with sensible defaults
- 📋 **Full Control** - Edit prompt, negative prompt, steps, sampler, CFG, seed, model, and more
- 💾 **Download Fixed Images** - Get Civitai-ready PNGs instantly
- 🔒 **Privacy** - All processing happens locally in your browser

## 🚀 Local Installation (Optional)

```bash
# Clone the repository
git clone https://github.com/bartwisch/civitai-metadata-fixer.git
cd civitai-metadata-fixer

# Option 1: Just open index.html in your browser

# Option 2: Run Python version with more features
pip install flask pillow
python civitai_metadata_fixer.py
```

## ☁️ Deploy Your Own

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/bartwisch/civitai-metadata-fixer)

## 📖 Usage

```bash
python civitai_metadata_fixer.py
```

The tool will automatically open in your browser at `http://127.0.0.1:5000`.

### Quick Fix (One-Click)

1. Drag & drop your image
2. Click **"⚡ Auto-fill Valid Metadata"**
3. Click **"💾 Download Fixed Image"**
4. Upload to Civitai ✅

### Custom Metadata

1. Drag & drop your image
2. Fill in your actual prompt and settings
3. Click **"💾 Download Fixed Image"**
4. Upload to Civitai ✅

## 🔧 How It Works

Civitai requires PNG images to have metadata in the Automatic1111 format stored in PNG `tEXt` chunks. Images from some tools (ComfyUI, custom scripts, edited images) may not have this metadata or have it in an incompatible format.

This tool embeds properly formatted `parameters` metadata that includes:
- Prompt & Negative Prompt
- Steps, Sampler, CFG Scale
- Seed, Size
- Model name & hash

## 📝 Requirements

- Python 3.7+
- Flask
- Pillow (PIL)

## 📄 License

MIT License - feel free to use, modify, and distribute.

## 🤝 Contributing

Pull requests welcome! Feel free to open issues for bugs or feature requests.

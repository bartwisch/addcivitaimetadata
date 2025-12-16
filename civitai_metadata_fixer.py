#!/usr/bin/env python3
"""
Civitai Metadata Fixer Tool - Web Version
Adds or fixes PNG metadata to make images compatible with Civitai uploads.
"""

from flask import Flask, render_template_string, request, jsonify, send_file
from PIL import Image
from PIL.PngImagePlugin import PngInfo
import os
import io
import base64
import re
from pathlib import Path
import webbrowser
from threading import Timer

app = Flask(__name__)

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Civitai Metadata Fixer</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: 'Segoe UI', system-ui, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            min-height: 100vh;
            color: #fff;
            padding: 20px;
        }
        .container { max-width: 900px; margin: 0 auto; }
        h1 {
            text-align: center;
            margin-bottom: 30px;
            background: linear-gradient(90deg, #e94560, #ff6b9d);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-size: 2.5em;
        }
        .card {
            background: rgba(255,255,255,0.05);
            border-radius: 16px;
            padding: 24px;
            margin-bottom: 20px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.1);
        }
        .card h2 {
            color: #e94560;
            margin-bottom: 16px;
            font-size: 1.2em;
        }
        .drop-zone {
            border: 3px dashed rgba(233,69,96,0.5);
            border-radius: 12px;
            padding: 60px 20px;
            text-align: center;
            cursor: pointer;
            transition: all 0.3s ease;
            background: rgba(233,69,96,0.05);
        }
        .drop-zone:hover, .drop-zone.dragover {
            border-color: #e94560;
            background: rgba(233,69,96,0.15);
        }
        .drop-zone p { color: #a0a0a0; font-size: 1.1em; }
        .drop-zone .icon { font-size: 3em; margin-bottom: 10px; }
        #preview-container {
            display: none;
            text-align: center;
            margin-top: 20px;
        }
        #preview-image {
            max-width: 100%;
            max-height: 300px;
            border-radius: 8px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.3);
        }
        .form-group { margin-bottom: 16px; }
        label {
            display: block;
            margin-bottom: 6px;
            color: #a0a0a0;
            font-weight: 500;
        }
        input, textarea, select {
            width: 100%;
            padding: 12px 16px;
            background: rgba(0,0,0,0.3);
            border: 1px solid rgba(255,255,255,0.1);
            border-radius: 8px;
            color: #fff;
            font-size: 14px;
            transition: border-color 0.3s;
        }
        input:focus, textarea:focus, select:focus {
            outline: none;
            border-color: #e94560;
        }
        textarea { resize: vertical; min-height: 100px; font-family: inherit; }
        .row { display: flex; gap: 16px; flex-wrap: wrap; }
        .row .form-group { flex: 1; min-width: 120px; }
        .btn {
            padding: 14px 28px;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            display: inline-flex;
            align-items: center;
            gap: 8px;
        }
        .btn-primary {
            background: linear-gradient(135deg, #e94560, #ff6b9d);
            color: #fff;
        }
        .btn-primary:hover { transform: translateY(-2px); box-shadow: 0 4px 20px rgba(233,69,96,0.4); }
        .btn-secondary {
            background: rgba(255,255,255,0.1);
            color: #fff;
        }
        .btn-secondary:hover { background: rgba(255,255,255,0.2); }
        .button-group { display: flex; gap: 12px; flex-wrap: wrap; margin-top: 20px; }
        #current-metadata {
            background: rgba(0,0,0,0.3);
            padding: 16px;
            border-radius: 8px;
            font-family: monospace;
            font-size: 13px;
            max-height: 200px;
            overflow-y: auto;
            white-space: pre-wrap;
            color: #a0a0a0;
        }
        .status {
            padding: 12px 20px;
            border-radius: 8px;
            margin-top: 16px;
            display: none;
        }
        .status.success { display: block; background: rgba(78,204,163,0.2); color: #4ecca3; }
        .status.error { display: block; background: rgba(233,69,96,0.2); color: #e94560; }
        .checkbox-group { display: flex; align-items: center; gap: 8px; }
        .checkbox-group input { width: auto; }
        .info-text { font-size: 12px; color: #666; margin-top: 4px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🖼️ Civitai Metadata Fixer</h1>
        
        <div class="card">
            <h2>📁 Select Image</h2>
            <div class="drop-zone" id="drop-zone">
                <div class="icon">📤</div>
                <p>Drop PNG image here or click to browse</p>
                <input type="file" id="file-input" accept=".png,.jpg,.jpeg,.webp" style="display:none">
            </div>
            <div id="preview-container">
                <img id="preview-image" src="" alt="Preview">
                <p id="image-info" style="margin-top:10px; color:#a0a0a0;"></p>
            </div>
        </div>

        <div class="card">
            <h2>📋 Current Metadata</h2>
            <div id="current-metadata">Load an image to see its metadata...</div>
        </div>

        <div class="card">
            <h2>✏️ New Metadata (Automatic1111 Format)</h2>
            <form id="metadata-form">
                <div class="form-group">
                    <label for="prompt">Prompt *</label>
                    <textarea id="prompt" placeholder="Enter your positive prompt here..." rows="4"></textarea>
                </div>
                
                <div class="form-group">
                    <label for="negative">Negative Prompt</label>
                    <textarea id="negative" placeholder="Enter negative prompt..." rows="3"></textarea>
                </div>
                
                <div class="row">
                    <div class="form-group">
                        <label for="steps">Steps</label>
                        <input type="number" id="steps" value="20" min="1" max="150">
                    </div>
                    <div class="form-group">
                        <label for="sampler">Sampler</label>
                        <select id="sampler">
                            <option>DPM++ 2M Karras</option>
                            <option>DPM++ SDE Karras</option>
                            <option>DPM++ 2M SDE Karras</option>
                            <option>Euler a</option>
                            <option>Euler</option>
                            <option>DDIM</option>
                            <option>UniPC</option>
                            <option>LMS</option>
                            <option>Heun</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label for="cfg">CFG Scale</label>
                        <input type="number" id="cfg" value="7" min="1" max="30" step="0.5">
                    </div>
                </div>
                
                <div class="row">
                    <div class="form-group">
                        <label for="seed">Seed</label>
                        <input type="text" id="seed" value="-1" placeholder="-1 for random">
                    </div>
                    <div class="form-group">
                        <label for="width">Width</label>
                        <input type="number" id="width" value="512">
                    </div>
                    <div class="form-group">
                        <label for="height">Height</label>
                        <input type="number" id="height" value="512">
                    </div>
                </div>
                
                <div class="row">
                    <div class="form-group">
                        <label for="model">Model Name</label>
                        <input type="text" id="model" placeholder="e.g., realisticVisionV51">
                    </div>
                    <div class="form-group">
                        <label for="model_hash">Model Hash</label>
                        <input type="text" id="model_hash" placeholder="e.g., 15012c538f">
                    </div>
                    <div class="form-group">
                        <label for="clip_skip">Clip Skip</label>
                        <input type="number" id="clip_skip" value="1" min="1" max="12">
                    </div>
                </div>

                <div class="button-group">
                    <button type="button" class="btn btn-primary" onclick="saveImage(false)">
                        💾 Download Fixed Image
                    </button>
                    <button type="button" class="btn btn-secondary" onclick="previewMetadata()">
                        👁️ Preview Metadata
                    </button>
                    <button type="button" class="btn btn-secondary" onclick="autoFillMetadata()" style="background: linear-gradient(135deg, #4ecca3, #45b393);">
                        ⚡ Auto-fill Valid Metadata
                    </button>
                </div>
            </form>
            <div id="status" class="status"></div>
        </div>
    </div>

    <script>
        let currentImageData = null;
        let currentFilename = 'image.png';
        
        const dropZone = document.getElementById('drop-zone');
        const fileInput = document.getElementById('file-input');
        
        dropZone.addEventListener('click', () => fileInput.click());
        dropZone.addEventListener('dragover', (e) => {
            e.preventDefault();
            dropZone.classList.add('dragover');
        });
        dropZone.addEventListener('dragleave', () => dropZone.classList.remove('dragover'));
        dropZone.addEventListener('drop', (e) => {
            e.preventDefault();
            dropZone.classList.remove('dragover');
            if (e.dataTransfer.files.length) handleFile(e.dataTransfer.files[0]);
        });
        fileInput.addEventListener('change', (e) => {
            if (e.target.files.length) handleFile(e.target.files[0]);
        });
        
        function handleFile(file) {
            currentFilename = file.name;
            const reader = new FileReader();
            reader.onload = (e) => {
                currentImageData = e.target.result;
                document.getElementById('preview-image').src = currentImageData;
                document.getElementById('preview-container').style.display = 'block';
                
                // Send to server to extract metadata
                fetch('/load-image', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({image: currentImageData, filename: currentFilename})
                })
                .then(res => res.json())
                .then(data => {
                    document.getElementById('image-info').textContent = 
                        `${data.width}x${data.height} • ${file.name}`;
                    document.getElementById('width').value = data.width;
                    document.getElementById('height').value = data.height;
                    document.getElementById('current-metadata').textContent = 
                        data.metadata || 'No metadata found';
                    
                    // Fill form if metadata was parsed
                    if (data.parsed) {
                        if (data.parsed.prompt) document.getElementById('prompt').value = data.parsed.prompt;
                        if (data.parsed.negative) document.getElementById('negative').value = data.parsed.negative;
                        if (data.parsed.steps) document.getElementById('steps').value = data.parsed.steps;
                        if (data.parsed.sampler) document.getElementById('sampler').value = data.parsed.sampler;
                        if (data.parsed.cfg) document.getElementById('cfg').value = data.parsed.cfg;
                        if (data.parsed.seed) document.getElementById('seed').value = data.parsed.seed;
                        if (data.parsed.model) document.getElementById('model').value = data.parsed.model;
                        if (data.parsed.model_hash) document.getElementById('model_hash').value = data.parsed.model_hash;
                    }
                });
            };
            reader.readAsDataURL(file);
        }
        
        function buildMetadata() {
            const prompt = document.getElementById('prompt').value.trim();
            const negative = document.getElementById('negative').value.trim();
            const steps = document.getElementById('steps').value;
            const sampler = document.getElementById('sampler').value;
            const cfg = document.getElementById('cfg').value;
            const seed = document.getElementById('seed').value;
            const width = document.getElementById('width').value;
            const height = document.getElementById('height').value;
            const model = document.getElementById('model').value.trim();
            const modelHash = document.getElementById('model_hash').value.trim();
            const clipSkip = document.getElementById('clip_skip').value;
            
            let params = prompt;
            if (negative) params += `\\nNegative prompt: ${negative}`;
            
            let settings = [
                `Steps: ${steps}`,
                `Sampler: ${sampler}`,
                `CFG scale: ${cfg}`,
                `Seed: ${seed}`,
                `Size: ${width}x${height}`
            ];
            if (model) settings.push(`Model: ${model}`);
            if (modelHash) settings.push(`Model hash: ${modelHash}`);
            if (clipSkip !== '1') settings.push(`Clip skip: ${clipSkip}`);
            
            params += `\\n${settings.join(', ')}`;
            return params;
        }
        
        function previewMetadata() {
            const metadata = buildMetadata().replace(/\\\\n/g, '\\n');
            alert('Metadata Preview:\\n\\n' + metadata);
        }
        
        function autoFillMetadata() {
            // Fill with minimal valid metadata that Civitai will accept
            if (!document.getElementById('prompt').value.trim()) {
                document.getElementById('prompt').value = 'AI generated image';
            }
            document.getElementById('steps').value = document.getElementById('steps').value || '20';
            document.getElementById('cfg').value = document.getElementById('cfg').value || '7';
            document.getElementById('seed').value = document.getElementById('seed').value || Math.floor(Math.random() * 4294967295);
            if (!document.getElementById('model').value.trim()) {
                document.getElementById('model').value = 'sd_xl_base_1.0';
            }
            if (!document.getElementById('model_hash').value.trim()) {
                document.getElementById('model_hash').value = 'be9edd61';
            }
            showStatus('Auto-filled with valid metadata! Click "Download Fixed Image" to save.', 'success');
        }
        
        function saveImage(overwrite) {
            if (!currentImageData) {
                showStatus('Please load an image first', 'error');
                return;
            }
            if (!document.getElementById('prompt').value.trim()) {
                showStatus('Prompt is required for Civitai', 'error');
                return;
            }
            
            const metadata = buildMetadata();
            
            fetch('/save-image', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    image: currentImageData,
                    filename: currentFilename,
                    parameters: metadata
                })
            })
            .then(res => res.blob())
            .then(blob => {
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = currentFilename.replace(/\\.[^.]+$/, '_civitai.png');
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                URL.revokeObjectURL(url);
                showStatus('Image saved with Civitai-compatible metadata!', 'success');
            })
            .catch(err => showStatus('Error: ' + err.message, 'error'));
        }
        
        function showStatus(message, type) {
            const status = document.getElementById('status');
            status.textContent = message;
            status.className = 'status ' + type;
        }
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/load-image', methods=['POST'])
def load_image():
    data = request.json
    image_data = data['image']
    
    # Decode base64 image
    header, encoded = image_data.split(',', 1)
    image_bytes = base64.b64decode(encoded)
    img = Image.open(io.BytesIO(image_bytes))
    
    result = {
        'width': img.width,
        'height': img.height,
        'metadata': '',
        'parsed': {}
    }
    
    # Extract metadata
    if hasattr(img, 'info') and img.info:
        metadata_parts = []
        for key, value in img.info.items():
            if isinstance(value, str):
                display = value[:1000] + '...' if len(value) > 1000 else value
                metadata_parts.append(f"{key}: {display}")
        result['metadata'] = '\n\n'.join(metadata_parts)
        
        # Try to parse A1111 format
        if 'parameters' in img.info:
            result['parsed'] = parse_a1111_params(img.info['parameters'])
    
    return jsonify(result)

def parse_a1111_params(params_str):
    """Parse A1111 format parameters"""
    parsed = {}
    try:
        parts = params_str.split("Negative prompt:")
        if len(parts) >= 2:
            parsed['prompt'] = parts[0].strip()
            rest = parts[1]
            
            settings_markers = ["Steps:", "Sampler:", "CFG"]
            settings_start = len(rest)
            for marker in settings_markers:
                pos = rest.find(marker)
                if pos != -1 and pos < settings_start:
                    settings_start = pos
            
            parsed['negative'] = rest[:settings_start].strip()
            settings = rest[settings_start:]
        else:
            parsed['prompt'] = params_str.strip()
            settings = ""
        
        # Parse settings
        if settings:
            steps_match = re.search(r'Steps:\s*(\d+)', settings)
            if steps_match: parsed['steps'] = steps_match.group(1)
            
            sampler_match = re.search(r'Sampler:\s*([^,]+)', settings)
            if sampler_match: parsed['sampler'] = sampler_match.group(1).strip()
            
            cfg_match = re.search(r'CFG scale:\s*([\d.]+)', settings)
            if cfg_match: parsed['cfg'] = cfg_match.group(1)
            
            seed_match = re.search(r'Seed:\s*(\d+)', settings)
            if seed_match: parsed['seed'] = seed_match.group(1)
            
            model_match = re.search(r'Model:\s*([^,]+)', settings)
            if model_match: parsed['model'] = model_match.group(1).strip()
            
            hash_match = re.search(r'Model hash:\s*([a-fA-F0-9]+)', settings)
            if hash_match: parsed['model_hash'] = hash_match.group(1)
            
    except Exception as e:
        print(f"Parse error: {e}")
    
    return parsed

@app.route('/save-image', methods=['POST'])
def save_image():
    data = request.json
    image_data = data['image']
    parameters = data['parameters'].replace('\\n', '\n')
    
    # Decode base64 image
    header, encoded = image_data.split(',', 1)
    image_bytes = base64.b64decode(encoded)
    img = Image.open(io.BytesIO(image_bytes))
    
    # Convert to RGB/RGBA as needed
    if img.mode not in ('RGB', 'RGBA'):
        img = img.convert('RGBA' if 'A' in img.mode else 'RGB')
    
    # Create PNG with metadata
    pnginfo = PngInfo()
    pnginfo.add_text("parameters", parameters)
    
    # Preserve other metadata
    if hasattr(img, 'info'):
        for key, value in img.info.items():
            if key != 'parameters' and isinstance(value, str):
                pnginfo.add_text(key, value)
    
    # Save to bytes
    output = io.BytesIO()
    img.save(output, format='PNG', pnginfo=pnginfo)
    output.seek(0)
    
    return send_file(output, mimetype='image/png', as_attachment=True, 
                     download_name='fixed_image.png')

def open_browser():
    webbrowser.open('http://127.0.0.1:5000')

if __name__ == '__main__':
    print("\n" + "="*50)
    print("🖼️  Civitai Metadata Fixer")
    print("="*50)
    print("\n📌 Opening browser at http://127.0.0.1:5000")
    print("   Press Ctrl+C to stop the server\n")
    
    Timer(1.5, open_browser).start()
    app.run(debug=False, port=5000)

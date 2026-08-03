import os
import subprocess
import tempfile
from io import BytesIO
import cv2
import numpy as np
from flask import Flask, request, send_file, render_template_string

app = Flask(__name__)

HTML_UI = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MP4 to Transparent GIF</title>
    <style>
        :root { --bg: #121212; --surface: #1e1e1e; --primary: #3b82f6; --text: #f3f4f6; }
        body { font-family: system-ui, -apple-system, sans-serif; background-color: var(--bg); color: var(--text); display: flex; justify-content: center; align-items: center; min-height: 100vh; margin: 0; padding: 20px; box-sizing: border-box; }
        .container { background: var(--surface); padding: 30px; border-radius: 16px; box-shadow: 0 10px 30px rgba(0,0,0,0.5); width: 100%; max-width: 550px; }
        h2 { margin-top: 0; text-align: center; }
        .drop-zone { border: 2px dashed #4b5563; border-radius: 12px; padding: 20px; text-align: center; cursor: pointer; transition: 0.3s; margin-bottom: 20px; display: flex; flex-direction: column; align-items: center; justify-content: center; overflow: hidden; }
        .drop-zone.dragover { border-color: var(--primary); background: rgba(59, 130, 246, 0.1); }
        .controls { display: flex; flex-direction: column; gap: 15px; margin-bottom: 20px; }
        .row-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; }
        .control-group { display: flex; flex-direction: column; gap: 5px; }
        input[type="color"] { width: 100%; height: 40px; border: none; border-radius: 8px; cursor: pointer; background: none; }
        input[type="range"] { width: 100%; }
        button { background: var(--primary); color: white; border: none; padding: 12px; border-radius: 8px; font-weight: bold; cursor: pointer; width: 100%; transition: 0.2s; }
        button:hover { background: #2563eb; }
        button:disabled { background: #4b5563; cursor: not-allowed; }
        #status { text-align: center; margin-top: 15px; font-size: 0.9em; color: #9ca3af; }
        .preview-area { margin-top: 20px; text-align: center; display: none; }
        .preview-area img { max-width: 100%; border-radius: 8px; background: repeating-conic-gradient(#374151 0% 25%, transparent 0% 50%) 50% / 20px 20px #1f2937; }
        .download-btn { margin-top: 15px; background: #10b981; }
        .download-btn:hover { background: #059669; }
        #videoPreview { display: none; max-width: 100%; max-height: 200px; border-radius: 8px; margin-top: 15px; background: #000; }
    </style>
</head>
<body>
    <div class="container">
        <h2>MP4 to GIF Converter</h2>
        <p style="text-align: center; color: #9ca3af; font-size: 0.9em; margin-top: -10px;">Size Optimized Engine</p>
        
        <div class="drop-zone" id="dropZone">
            <span id="dropText">Drag & Drop an MP4 here<br><br>or click to select file</span>
            <video id="videoPreview" autoplay loop muted playsinline></video>
            <input type="file" id="fileInput" accept="video/mp4" style="display: none;">
        </div>

        <div class="controls">
            <div class="control-group">
                <label>Outside Background Color</label>
                <input type="color" id="colorPicker" value="#ffffff">
            </div>
            
            <div class="row-2">
                <div class="control-group">
                    <label>Tolerance: <span id="tolValue">0.05</span></label>
                    <input type="range" id="tolerance" min="0.01" max="0.3" step="0.01" value="0.05">
                </div>
                <div class="control-group">
                    <label>Speed: <span id="speedValue">1.0x</span></label>
                    <input type="range" id="speed" min="0.5" max="3.0" step="0.1" value="1.0">
                </div>
            </div>
            
            <div class="row-2">
                <div class="control-group">
                    <label>Width: <span id="widthValue">400px</span></label>
                    <input type="range" id="width" min="100" max="1080" step="10" value="400">
                </div>
                <div class="control-group">
                    <label>FPS: <span id="fpsValue">15</span></label>
                    <input type="range" id="outFps" min="5" max="30" step="1" value="15">
                </div>
            </div>
        </div>

        <button id="convertBtn">Convert to GIF</button>
        <div id="status"></div>

        <div class="preview-area" id="previewArea">
            <img id="resultImg" alt="Result GIF">
            <a id="downloadLink" download="transparent.gif">
                <button class="download-btn">Download GIF</button>
            </a>
        </div>
    </div>

    <script>
        const dropZone = document.getElementById('dropZone');
        const fileInput = document.getElementById('fileInput');
        const dropText = document.getElementById('dropText');
        const convertBtn = document.getElementById('convertBtn');
        const status = document.getElementById('status');
        const previewArea = document.getElementById('previewArea');
        const resultImg = document.getElementById('resultImg');
        const downloadLink = document.getElementById('downloadLink');
        const videoPreview = document.getElementById('videoPreview');

        // Sliders
        const toleranceSlider = document.getElementById('tolerance');
        const tolValue = document.getElementById('tolValue');
        const speedSlider = document.getElementById('speed');
        const speedValue = document.getElementById('speedValue');
        const widthSlider = document.getElementById('width');
        const widthValue = document.getElementById('widthValue');
        const fpsSlider = document.getElementById('outFps');
        const fpsValue = document.getElementById('fpsValue');

        let currentFile = null;

        toleranceSlider.oninput = (e) => tolValue.textContent = e.target.value;
        widthSlider.oninput = (e) => widthValue.textContent = e.target.value + 'px';
        fpsSlider.oninput = (e) => fpsValue.textContent = e.target.value;
        speedSlider.oninput = (e) => {
            speedValue.textContent = e.target.value + 'x';
            videoPreview.playbackRate = parseFloat(e.target.value);
        };
        
        dropZone.onclick = (e) => {
            if(e.target !== videoPreview) fileInput.click();
        };
        
        dropZone.ondragover = (e) => { e.preventDefault(); dropZone.classList.add('dragover'); };
        dropZone.ondragleave = () => dropZone.classList.remove('dragover');
        dropZone.ondrop = (e) => {
            e.preventDefault();
            dropZone.classList.remove('dragover');
            if (e.dataTransfer.files.length) handleFile(e.dataTransfer.files[0]);
        };
        fileInput.onchange = (e) => {
            if (e.target.files.length) handleFile(e.target.files[0]);
        };

        function handleFile(file) {
            if (file.type !== "video/mp4") return alert("Please select an MP4 file.");
            currentFile = file;
            dropText.innerHTML = `<strong>${file.name}</strong>`;
            
            videoPreview.src = URL.createObjectURL(file);
            videoPreview.style.display = 'block';
            videoPreview.load();
            videoPreview.playbackRate = parseFloat(speedSlider.value);
        }

        convertBtn.onclick = async () => {
            if (!currentFile) return alert("Please select a video first.");
            
            const formData = new FormData();
            formData.append('video', currentFile);
            formData.append('color', document.getElementById('colorPicker').value);
            formData.append('tolerance', toleranceSlider.value);
            formData.append('speed', speedSlider.value);
            formData.append('width', widthSlider.value);
            formData.append('fps', fpsSlider.value);

            convertBtn.disabled = true;
            status.textContent = "Analyzing, resizing & clearing background (Takes a few seconds)...";
            previewArea.style.display = 'none';

            try {
                const response = await fetch('/convert', { method: 'POST', body: formData });
                if (!response.ok) throw new Error("Conversion failed. Check terminal.");
                
                const blob = await response.blob();
                const url = URL.createObjectURL(blob);
                
                resultImg.src = url;
                downloadLink.href = url;
                previewArea.style.display = 'block';
                status.textContent = "Success!";
            } catch (error) {
                status.textContent = "Error: " + error.message;
            } finally {
                convertBtn.disabled = false;
            }
        };
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_UI)

@app.route('/convert', methods=['POST'])
def convert():
    if 'video' not in request.files:
        return "No video uploaded", 400

    video = request.files['video']
    hex_color = request.form.get('color', '#ffffff').replace('#', '')
    tolerance_float = float(request.form.get('tolerance', '0.05'))
    speed = float(request.form.get('speed', '1.0'))
    max_width = int(request.form.get('width', '400'))
    out_fps = int(request.form.get('fps', '15'))

    r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    target_bgr = np.array([b, g, r], dtype=np.int16)
    
    tol_val = int(tolerance_float * 255)
    diff = (tol_val, tol_val, tol_val)
    
    pts_modifier = 1.0 / speed

    with tempfile.TemporaryDirectory() as tmpdirname:
        input_path = os.path.join(tmpdirname, 'input.mp4')
        output_path = os.path.join(tmpdirname, 'output.gif')
        
        video.save(input_path)

        # 1. PROCESS WITH OPENCV
        cap = cv2.VideoCapture(input_path)
        
        # MASK_ONLY mode
        flags = 4 | cv2.FLOODFILL_FIXED_RANGE | cv2.FLOODFILL_MASK_ONLY | (255 << 8)

        frame_idx = 0
        while True:
            ret, frame = cap.read()
            if not ret:
                break
                
            h, w = frame.shape[:2]
            bg_mask = np.zeros((h+2, w+2), np.uint8)
            
            frame_bgra = cv2.cvtColor(frame, cv2.COLOR_BGR2BGRA)
            
            corners = [(0,0), (w-1, 0), (0, h-1), (w-1, h-1)]
            for pt in corners:
                if bg_mask[pt[1]+1, pt[0]+1] == 0:
                    corner_bgr = frame[pt[1], pt[0]].astype(np.int16)
                    if np.all(np.abs(corner_bgr - target_bgr) <= tol_val):
                        cv2.floodFill(frame, bg_mask, pt, (0,0,0), diff, diff, flags)
            
            bg_mask_cropped = bg_mask[1:h+1, 1:w+1]
            frame_bgra[bg_mask_cropped == 255, 3] = 0
            
            cv2.imwrite(os.path.join(tmpdirname, f"frame_{frame_idx:04d}.png"), frame_bgra)
            frame_idx += 1
            
        cap.release()

        # 2. RENDER WITH FFMPEG (Added scale and fps filters to drastically reduce size)
        command = [
            "ffmpeg",
            "-i", os.path.join(tmpdirname, "frame_%04d.png"),
            "-filter_complex", 
            f"[0:v]setpts={pts_modifier}*PTS,fps={out_fps},scale={max_width}:-1:flags=lanczos,split[v0][v1];[v0]palettegen=reserve_transparent=1[p];[v1][p]paletteuse",
            "-y",
            output_path
        ]

        subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

        with open(output_path, 'rb') as f:
            gif_data = BytesIO(f.read())

    return send_file(
        gif_data,
        mimetype='image/gif',
        as_attachment=True,
        download_name='transparent.gif'
    )

if __name__ == '__main__':
    print("\\nServer running! Open http://127.0.0.1:5000 in your browser.")
    app.run(port=5000)

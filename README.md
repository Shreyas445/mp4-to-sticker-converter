# MP4 to Transparent GIF Converter 🎥➡️🖼️

A lightweight, local, Python-powered engine to convert MP4 videos into perfectly transparent, highly optimized GIFs. 
<br>



https://github.com/user-attachments/assets/eb4166e8-b25f-44ce-9875-b8f1d9c9bbcc



<img width="400" height="400" alt="transparent (8)" src="https://github.com/user-attachments/assets/1930f191-e63e-48a2-8b0d-26ae4016c2a4" />



Unlike standard "green-screen" filters that accidentally delete white clothing or internal colors, this tool uses a custom **OpenCV Flood-Fill edge-detection algorithm**. It analyzes the outside border of your video subject and surgically removes the background while leaving the inside of your subject perfectly intact.

<img width="auto" height="500px" alt="image" src="https://github.com/user-attachments/assets/8d5cb5c7-b266-4919-b1a5-71814c953b2c" />
<img width="auto" height="400px" alt="image" src="https://github.com/user-attachments/assets/ecb160ee-1036-431c-b00b-669d15b7d3e8" />


## Features ✨

* **Native Alpha Edge-Detect:** Uses OpenCV to delete outer backgrounds without destroying internal colors (no pink halos or missing eyes).
* **Zero Storage Footprint:** Video is processed entirely in RAM/Temp space. Nothing is permanently saved to your hard drive.
* **Size Optimization Engine:** Built-in sliders for Frame Rate (FPS) and Max Width to drastically compress GIF output sizes.
* **Speed Controller:** Adjust the playback speed of the final GIF (0.5x to 3.0x).
* **Responsive Dark-Mode UI:** A beautiful, single-page Flask frontend with drag-and-drop support and a live video preview.
* **Local Processing:** Runs entirely on your machine via FFmpeg. No uploads, no API keys, no watermarks.

---

## Installation & Setup 🛠️

### 1. Install System Requirements
You must have **FFmpeg** installed on your system and added to your system PATH.
* **Windows:** `winget install ffmpeg` (or download from the official site)
* **Mac:** `brew install ffmpeg`
* **Linux:** `sudo apt install ffmpeg`

### 2. Install Python Dependencies
Ensure you have Python 3 installed, then run:
```bash
pip install flask opencv-python numpy

```

---

## How to Run 🚀

1. Save the main script as `app.py`.
2. Open your terminal in the same folder as the script.
3. Run the application:
```bash
python app.py

```


4. Open your web browser and go to: **http://127.0.0.1:5000**

---

## How to Use the UI 🖥️

1. **Upload:** Drag and drop your MP4 file into the dashed box.
2. **Preview:** The video will automatically begin looping in the drop zone so you can verify the content.
3. **Select Color:** Use the color picker to select the exact background color you want removed (default is pure white `#FFFFFF`).
4. **Tune Parameters:**
* **Tolerance:** Adjusts how strictly the algorithm matches the background color. If the background isn't fully removing, slowly raise this value.
* **Speed:** Speeds up or slows down the output GIF.
* **Width & FPS:** Crucial for keeping file sizes small. A standard web GIF is usually around 400px wide at 15 FPS.


5. **Convert:** Click the button. The processing happens locally on your CPU. Once finished, the GIF will appear with a download button.

---

## Troubleshooting ⚠️

* **"Conversion Failed" error:** Ensure FFmpeg is correctly installed and accessible via your system PATH. Open a new terminal and type `ffmpeg -version` to verify.
* **The background isn't fully removed:** Increase the `Tolerance` slider slightly.
* **The file size is too massive:** Lower the `Width` to 300px or 400px and drop the `FPS` to 10 or 15. GIFs do not use modern video compression, so large dimensions will result in massive files.
* **Video preview doesn't load:** Ensure your file is a standard H.264 encoded `.mp4`. Browsers cannot preview `.mkv` or `.avi` files natively.

---

## Tech Stack 🧩

* **Backend:** Python, Flask
* **Computer Vision:** OpenCV (cv2), Numpy
* **Rendering Engine:** FFmpeg
* **Frontend:** HTML5, CSS3, Vanilla JavaScript (Fetch API)


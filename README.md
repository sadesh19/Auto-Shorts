# AutoShorts AI

Local web app that converts a video into a 9:16 vertical short with a zoom effect and captions. Runs fully on CPU, no API keys needed.

---

## Tasks

**Task 1 — Basic Renderer**
Cuts the video to the chosen time range, centre-crops to 9:16, exports as MP4.

**Task 2 — Zoom Effect**
Punch-in zoom from 1.0× → 1.15× over 1.5 s at clip start, holds after. Per-frame via OpenCV.

**Task 2 — Captions**
Static "AutoShorts" label in the lower third. Font scales with clip width so it never overflows. Ready to accept word-level timestamps from the transcription module.

**Flask UI**
Drag-and-drop upload, start/end time inputs, Generate button, animated progress bar, Download button on completion. Dark theme (`#0a0a0f` / `#7C3AED`).

---

## Run

```bash
pip install -r requirements.txt
cd autoshorts
python app.py
```

Open `http://127.0.0.1:5000`

---

## Files

```
autoshorts/
├── app.py               # Flask routes
├── pipeline/
│   ├── renderer.py      # Cut → crop → zoom → captions → export
│   ├── effects.py       # Zoom (OpenCV)
│   └── captions.py      # Caption overlay (moviepy)
├── static/
│   ├── style.css
│   └── app.js
├── templates/
│   └── index.html
├── uploads/
└── shorts_output/
```

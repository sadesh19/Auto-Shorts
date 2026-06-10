import os
from flask import Flask, render_template, request, jsonify, send_file
from werkzeug.utils import secure_filename

from pipeline.renderer import render_short


app = Flask(__name__)

# ── Config ───────────────────────────────────────────────────────────────────
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "uploads")
OUTPUT_FOLDER = os.path.join(os.path.dirname(__file__), "shorts_output")
ALLOWED_EXTENSIONS = {"mp4", "mov", "avi", "mkv", "webm"}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# ── Routes ───────────────────────────────────────────────────────────────────

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload():
    """
    Accepts a video file upload, runs the render pipeline, and returns
    a JSON response so the frontend can show a download button.

    Form fields (all optional):
        start_time  – float, default 0
        end_time    – float, default 30
    """
    if "video" not in request.files:
        return jsonify({"error": "No video file in request"}), 400

    file = request.files["video"]

    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    if not allowed_file(file.filename):
        return jsonify({"error": "Unsupported file type"}), 400

    # Safe filename — prevents path traversal
    filename = secure_filename(file.filename)
    upload_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(upload_path)

    # Optional clip timing from form
    try:
        start_time = float(request.form.get("start_time", 0))
        end_time = float(request.form.get("end_time", 30))
    except ValueError:
        start_time, end_time = 0, 30

    output_filename = "output.mp4"
    output_path = os.path.join(OUTPUT_FOLDER, output_filename)

    # Run the pipeline
    # word_timestamps=None → falls back to static caption
    # (a transcription module from another team member can pass word_timestamps
    #  by calling render_short() directly)
    render_short(
        video_path=upload_path,
        start_time=start_time,
        end_time=end_time,
        output_path=output_path,
        word_timestamps=None,
    )

    return jsonify({
        "message": "Short created successfully",
        "download_url": "/download/output.mp4",
        "filename": output_filename,
    })


@app.route("/download/<filename>")
def download(filename):
    """Serve the rendered short for download."""
    safe_name = secure_filename(filename)
    file_path = os.path.join(OUTPUT_FOLDER, safe_name)

    if not os.path.exists(file_path):
        return jsonify({"error": "File not found"}), 404

    return send_file(
        file_path,
        as_attachment=True,
        download_name=safe_name,
        mimetype="video/mp4",
    )


if __name__ == "__main__":
    app.run(debug=True)

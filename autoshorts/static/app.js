/**
 * AutoShorts AI — Frontend Logic
 *
 * Handles:
 *   • Drag-and-drop + click-to-browse file selection
 *   • Form submission via fetch (no page reload)
 *   • Animated progress bar during processing
 *   • Showing the download button on success
 *   • Showing error messages on failure
 */

const dropZone     = document.getElementById("drop-zone");
const fileInput    = document.getElementById("file-input");
const fileInfo     = document.getElementById("file-info");
const generateBtn  = document.getElementById("generate-btn");
const progressSec  = document.getElementById("progress-section");
const progressFill = document.getElementById("progress-fill");
const statusText   = document.getElementById("status-text");
const resultSec    = document.getElementById("result-section");
const downloadBtn  = document.getElementById("download-btn");
const errorSec     = document.getElementById("error-section");
const errorMsg     = document.getElementById("error-msg");
const startInput   = document.getElementById("start-time");
const endInput     = document.getElementById("end-time");
const opacitySlider = document.getElementById("logo-opacity");
const opacityValue  = document.getElementById("opacity-value");

let selectedFile = null;
let fakeTimer    = null;   // used to animate progress bar

// ── Opacity slider live label ────────────────────────────────────────────────
opacitySlider.addEventListener("input", () => {
  opacityValue.textContent = opacitySlider.value;
});

// ── File selection ──────────────────────────────────────────────────────────

fileInput.addEventListener("change", () => {
  if (fileInput.files.length > 0) handleFile(fileInput.files[0]);
});

dropZone.addEventListener("dragover", (e) => {
  e.preventDefault();
  dropZone.classList.add("dragover");
});

dropZone.addEventListener("dragleave", () => {
  dropZone.classList.remove("dragover");
});

dropZone.addEventListener("drop", (e) => {
  e.preventDefault();
  dropZone.classList.remove("dragover");
  if (e.dataTransfer.files.length > 0) handleFile(e.dataTransfer.files[0]);
});

function handleFile(file) {
  selectedFile = file;
  const sizeMB = (file.size / (1024 * 1024)).toFixed(1);
  fileInfo.textContent = `${file.name}  •  ${sizeMB} MB`;
  resetResult();
}

// ── Form submit ─────────────────────────────────────────────────────────────

generateBtn.addEventListener("click", async () => {
  if (!selectedFile) {
    showError("Please select a video file first.");
    return;
  }

  resetResult();
  setGenerating(true);
  startFakeProgress();

  const formData = new FormData();
  formData.append("video", selectedFile);
  formData.append("start_time", startInput.value || "0");
  formData.append("end_time",   endInput.value   || "30");
  formData.append("logo_opacity", (parseInt(opacitySlider.value) / 100).toFixed(2));

  try {
    const response = await fetch("/upload", {
      method: "POST",
      body: formData,
    });

    const data = await response.json();
    stopFakeProgress(100);

    if (!response.ok || data.error) {
      showError(data.error || "Something went wrong. Please try again.");
    } else {
      showResult(data.download_url, data.filename);
    }
  } catch (err) {
    stopFakeProgress(0);
    showError("Network error — is the Flask server running?");
  } finally {
    setGenerating(false);
  }
});

// ── Progress animation ──────────────────────────────────────────────────────

// Fake progress increments while the server is working.
// The bar jumps to 100% when the response arrives.

const STAGES = [
  { pct: 10, label: "Uploading…" },
  { pct: 25, label: "Processing video…" },
  { pct: 55, label: "Applying 9:16 crop…" },
  { pct: 70, label: "Rendering zoom effect…" },
  { pct: 85, label: "Burning captions…" },
  { pct: 95, label: "Exporting MP4…" },
];

let stageIndex = 0;

function startFakeProgress() {
  progressSec.style.display = "block";
  stageIndex = 0;
  setProgress(0, "Starting…");

  fakeTimer = setInterval(() => {
    if (stageIndex < STAGES.length) {
      const { pct, label } = STAGES[stageIndex];
      setProgress(pct, label);
      stageIndex++;
    }
  }, 2500);  // advance a stage every 2.5 s
}

function stopFakeProgress(finalPct) {
  clearInterval(fakeTimer);
  setProgress(finalPct, finalPct === 100 ? "Done!" : "");
}

function setProgress(pct, label) {
  progressFill.style.width = pct + "%";
  statusText.textContent = label;
}

// ── UI state helpers ─────────────────────────────────────────────────────────

function setGenerating(active) {
  generateBtn.disabled = active;
  generateBtn.textContent = active ? "Generating…" : "Generate Short";
}

function showResult(downloadUrl, filename) {
  resultSec.style.display  = "block";
  downloadBtn.href         = downloadUrl;
  downloadBtn.download     = filename;
}

function showError(msg) {
  errorSec.style.display = "block";
  errorMsg.textContent   = msg;
}

function resetResult() {
  resultSec.style.display  = "none";
  errorSec.style.display   = "none";
  progressSec.style.display = "none";
  progressFill.style.width = "0%";
}

from moviepy import VideoFileClip

try:
    # When run from repo root (e.g. test_renderer.py): autoshorts is a package
    from autoshorts.pipeline.effects import apply_zoom_effect, add_watermark
    from autoshorts.pipeline.captions import add_caption, add_word_captions
except ModuleNotFoundError:
    # When run from inside autoshorts/ (e.g. Flask app.py)
    from pipeline.effects import apply_zoom_effect, add_watermark
    from pipeline.captions import add_caption, add_word_captions


# ─────────────────────────────────────────────
# 9:16 crop helper
# ─────────────────────────────────────────────

def crop_to_916(clip):
    """
    Center-crop a clip to 9:16 (vertical / portrait) aspect ratio.

    Strategy
    --------
    • If the source is wider than 9:16 → keep full height, crop width
    • If the source is taller than 9:16 → keep full width, crop height
    • Already 9:16 → return unchanged

    This is a pure centre-crop with no upscaling, so quality is preserved.
    """
    target_ratio = 9 / 16          # 0.5625

    src_w, src_h = clip.size
    src_ratio = src_w / src_h

    if abs(src_ratio - target_ratio) < 0.01:
        # Already close enough — nothing to do
        return clip

    if src_ratio > target_ratio:
        # Wider than 9:16 → trim left/right
        new_w = int(src_h * target_ratio)
        x_center = src_w // 2
        x1 = x_center - new_w // 2
        x2 = x1 + new_w
        return clip.cropped(x1=x1, y1=0, x2=x2, y2=src_h)
    else:
        # Taller than 9:16 → trim top/bottom
        new_h = int(src_w / target_ratio)
        y_center = src_h // 2
        y1 = y_center - new_h // 2
        y2 = y1 + new_h
        return clip.cropped(x1=0, y1=y1, x2=src_w, y2=y2)


# ─────────────────────────────────────────────
# Public render function
# ─────────────────────────────────────────────

def render_short(
    video_path,
    start_time,
    end_time,
    output_path,
    word_timestamps=None,
    logo_path=None,
    logo_opacity=0.8,
):
    """
    Full render pipeline for one short clip.

    Parameters
    ----------
    video_path      : str  – path to source video
    start_time      : float – clip start in seconds
    end_time        : float – clip end in seconds
    output_path     : str  – where to write the final MP4
    word_timestamps : list of dict, optional
        Each dict: {"word": str, "start": float, "end": float}
        Times are relative to the START of the clip (i.e., start_time = t=0).
        If None or empty, a static caption is used instead.
    logo_path    : str, optional – absolute path to a PNG watermark logo.
                   If None, watermark stage is skipped.
    logo_opacity : float – watermark opacity 0.0–1.0, default 0.8

    Pipeline stages (in order)
    --------------------------
    1. Cut        – subclip [start_time, end_time]
    2. Crop       – centre-crop to 9:16 vertical format  ← Task 1
    3. Zoom       – punch-in zoom effect                  ← Task 2
    4. Captions   – word-by-word highlight captions       ← Task 2
    5. Watermark  – logo overlay with opacity control     ← Task 3 (stretch)
    6. Export     – write MP4 with libx264 + aac
    """

    # ── 1. Cut ──────────────────────────────────────────────────────────────
    clip = VideoFileClip(video_path).subclipped(start_time, end_time)

    # ── 2. Crop to 9:16 ─────────────────────────────────────────────────────
    clip = crop_to_916(clip)

    # ── 3. Zoom effect ──────────────────────────────────────────────────────
    clip = apply_zoom_effect(clip)

    # ── 4. Captions ─────────────────────────────────────────────────────────
    if word_timestamps:
        clip = add_word_captions(clip, word_timestamps)
    else:
        clip = add_caption(clip, "AutoShorts")

    # ── 5. Watermark ─────────────────────────────────────────────────────────
    if logo_path:
        clip = add_watermark(clip, logo_path, opacity=logo_opacity)

    # ── 6. Export ───────────────────────────────────────────────────────────
    clip.write_videofile(
        output_path,
        codec="libx264",
        audio_codec="aac",
    )

import os
import cv2
import numpy as np
from PIL import Image
from moviepy import ImageClip, CompositeVideoClip


def apply_zoom_effect(clip, zoom_from=1.0, zoom_to=1.15, duration=1.5):
    """
    Punch-in zoom: eases from zoom_from to zoom_to over `duration` seconds,
    then holds at zoom_to for the rest of the clip.

    This replaces the original continuous-grow zoom that never reset.
    Using cv2 resize so we stay CPU-only with no GPU requirement.
    """

    def zoom_frame(get_frame, t):
        # Ease progress: clamp t so zoom stops growing after `duration` secs
        progress = min(t / duration, 1.0)
        scale = zoom_from + (zoom_to - zoom_from) * progress

        frame = get_frame(t)
        h, w = frame.shape[:2]

        new_h = int(h * scale)
        new_w = int(w * scale)

        # Resize up, then crop back to original size from centre
        resized = cv2.resize(frame, (new_w, new_h), interpolation=cv2.INTER_LINEAR)

        y = (new_h - h) // 2
        x = (new_w - w) // 2

        return resized[y : y + h, x : x + w]

    # moviepy v2 renamed .fl() → .transform()
    return clip.transform(zoom_frame)


# ─────────────────────────────────────────────
# Logo / watermark overlay
# ─────────────────────────────────────────────

def add_watermark(clip, logo_path, opacity=0.8, position="top-right", padding=20):
    """
    Composite a logo PNG over the clip for its full duration.

    Parameters
    ----------
    clip       : moviepy VideoClip
    logo_path  : str   – absolute path to a PNG (transparency supported)
    opacity    : float – 0.0 (invisible) → 1.0 (fully opaque), default 0.8
    position   : str   – one of: "top-right", "top-left",
                                  "bottom-right", "bottom-left"
    padding    : int   – pixel gap from the edge, default 20

    How it works
    ------------
    1. Open the PNG with Pillow to preserve the alpha channel.
    2. Scale it to 18 % of the clip width (keeps it visible but not intrusive).
    3. Apply opacity by scaling the alpha channel.
    4. Convert to a moviepy ImageClip, position it, then composite.
    """

    if not os.path.exists(logo_path):
        # Logo missing — skip silently so the rest of the pipeline still runs
        return clip

    clip_w, clip_h = clip.size

    # ── Load & resize logo ───────────────────────────────────────────────────
    img = Image.open(logo_path).convert("RGBA")

    # Target width: 18 % of clip width, keep aspect ratio
    target_w = max(40, int(clip_w * 0.18))
    ratio     = target_w / img.width
    target_h  = int(img.height * ratio)
    img       = img.resize((target_w, target_h), Image.LANCZOS)

    # ── Apply opacity ────────────────────────────────────────────────────────
    opacity = max(0.0, min(1.0, opacity))   # clamp 0–1
    r, g, b, a = img.split()
    a = a.point(lambda px: int(px * opacity))
    img = Image.merge("RGBA", (r, g, b, a))

    # ── Convert to numpy for moviepy ─────────────────────────────────────────
    logo_array = np.array(img)

    # ── Calculate position ───────────────────────────────────────────────────
    if position == "top-left":
        x, y = padding, padding
    elif position == "top-right":
        x, y = clip_w - target_w - padding, padding
    elif position == "bottom-left":
        x, y = padding, clip_h - target_h - padding
    else:  # bottom-right (default fallback)
        x, y = clip_w - target_w - padding, clip_h - target_h - padding

    # ── Build ImageClip and composite ────────────────────────────────────────
    logo_clip = (
        ImageClip(logo_array)
        .with_duration(clip.duration)
        .with_position((x, y))
    )

    return CompositeVideoClip([clip, logo_clip], size=clip.size)

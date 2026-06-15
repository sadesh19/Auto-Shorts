from moviepy import TextClip, CompositeVideoClip


# ─────────────────────────────────────────────
# Internal helpers
# ─────────────────────────────────────────────

def _font_size(clip_w, ratio=0.07):
    """
    Return a font size that is `ratio` × clip width, clamped to a
    sensible range so it looks good on both tiny and large videos.

    ratio=0.07 → ~7 % of width.  For a 360 px wide 9:16 clip that's
    ~25 px — readable without overflowing.  For a 1080 px clip it's ~75 px.
    """
    return max(18, min(int(clip_w * ratio), 90))


def _make_text_clip(text, font_size, color, stroke_color, stroke_width, clip_w):
    """
    Build a TextClip whose text area is constrained to clip_w so moviepy
    never renders text wider than the video frame.
    """
    return TextClip(
        text=text,
        font_size=font_size,
        color=color,
        stroke_color=stroke_color,
        stroke_width=stroke_width,
        size=(clip_w, None),          # constrain width → auto word-wrap height
        method="caption",             # wrap text to fit the given width
        text_align="center",
    )


# ─────────────────────────────────────────────
# Public helpers
# ─────────────────────────────────────────────

def add_caption(clip, text):
    """
    Legacy single-string caption — kept for backwards compatibility.
    Font size and width are now responsive to the clip dimensions.
    """
    clip_w, clip_h = clip.size
    font_size = _font_size(clip_w)

    caption = (
        _make_text_clip(
            text=text,
            font_size=font_size,
            color="white",
            stroke_color="black",
            stroke_width=2,
            clip_w=clip_w,
        )
        .with_position(("center", "bottom"))
        .with_duration(clip.duration)
    )
    return CompositeVideoClip([clip, caption])


def add_word_captions(clip, word_timestamps):
    """
    Word-by-word animated captions with per-word highlight.

    Parameters
    ----------
    clip : moviepy VideoClip
    word_timestamps : list of dict
        Each dict: {"word": str, "start": float, "end": float}
        Times are relative to clip start (i.e. start_time = t=0).

    Caption style
    -------------
    • Current word  → yellow (#FFD700), slightly larger
    • All other time → white with black outline
    • Font size scales with clip width so text never overflows the frame
    • Text area constrained to clip width — moviepy handles wrapping
    """

    if not word_timestamps:
        return add_caption(clip, "AutoShorts")

    layers = [clip]

    clip_w, clip_h = clip.size

    # Responsive font sizes — scale with clip width
    font_normal    = _font_size(clip_w, ratio=0.07)
    font_highlight = _font_size(clip_w, ratio=0.08)  # slightly bigger when active

    # Y position: lower third (~78 % down the frame)
    y_position = int(clip_h * 0.78)

    for word_info in word_timestamps:
        word = word_info["word"].strip()
        w_start = float(word_info["start"])
        w_end   = float(word_info["end"])

        if not word:
            continue

        # Clamp to clip duration
        w_start = max(0.0, min(w_start, clip.duration))
        w_end   = max(w_start + 0.05, min(w_end, clip.duration))
        word_duration = w_end - w_start

        if word_duration <= 0:
            continue

        # ── Highlighted (active) word — yellow ──────────────────────────────
        highlight = (
            _make_text_clip(
                text=word,
                font_size=font_highlight,
                color="#FFD700",
                stroke_color="black",
                stroke_width=3,
                clip_w=clip_w,
            )
            .with_position(("center", y_position))
            .with_start(w_start)
            .with_duration(word_duration)
        )
        layers.append(highlight)

        # ── White echo before the highlight ─────────────────────────────────
        if w_start > 0:
            pre = (
                _make_text_clip(
                    text=word,
                    font_size=font_normal,
                    color="white",
                    stroke_color="black",
                    stroke_width=2,
                    clip_w=clip_w,
                )
                .with_position(("center", y_position))
                .with_start(0)
                .with_duration(w_start)
            )
            layers.append(pre)

        # ── White echo after the highlight ──────────────────────────────────
        if w_end < clip.duration:
            post = (
                _make_text_clip(
                    text=word,
                    font_size=font_normal,
                    color="white",
                    stroke_color="black",
                    stroke_width=2,
                    clip_w=clip_w,
                )
                .with_position(("center", y_position))
                .with_start(w_end)
                .with_duration(clip.duration - w_end)
            )
            layers.append(post)

    return CompositeVideoClip(layers, size=clip.size)

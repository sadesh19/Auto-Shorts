import cv2
import numpy as np


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

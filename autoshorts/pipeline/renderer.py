from moviepy import VideoFileClip


def render_short(
        video_path,
        start_time,
        end_time,
        output_path):


    video = VideoFileClip(video_path)


    # cut selected moment
    clip = video.subclipped(
        start_time,
        end_time
    )


    # convert to 9:16
    clip = clip.resized(
        height=1920
    )


    clip = clip.cropped(
        width=1080,
        height=1920,
        x_center=clip.w/2,
        y_center=clip.h/2
    )


    # export
    clip.write_videofile(
        output_path,
        codec="libx264",
        audio_codec="aac"
    )


    return output_path
"""
Zoom Effect Module - Adds punch-in zoom to video clips
Independent module that can be used with any video
"""

import subprocess
import os
import shutil


class ZoomEffect:
    def __init__(self):
        self.ffmpeg_path = self._find_ffmpeg()

    def _find_ffmpeg(self):
        """Find ffmpeg executable"""
        # Check current directory
        if os.path.exists('ffmpeg.exe'):
            return 'ffmpeg.exe'

        # Check system PATH
        ffmpeg = shutil.which('ffmpeg')
        if ffmpeg:
            return ffmpeg

        # Check common locations
        common_paths = [
            r'C:\ffmpeg\bin\ffmpeg.exe',
            r'C:\Program Files\ffmpeg\bin\ffmpeg.exe',
        ]
        for path in common_paths:
            if os.path.exists(path):
                return path

        return 'ffmpeg'

    def add_punch_zoom(self, input_video, output_video, start_time=0, duration=None, zoom_intensity=0.15,
                       zoom_duration=1.5):
        """
        Add punch zoom effect to video

        Parameters:
        - input_video: path to input video file
        - output_video: path to save output video
        - start_time: start time in seconds (default: 0)
        - duration: duration in seconds (default: None = entire video)
        - zoom_intensity: how much to zoom (0.15 = 15% zoom, from 1.0x to 1.15x)
        - zoom_duration: how long the zoom takes in seconds (default: 1.5)

        Returns:
        - output_video path if successful, None if failed
        """

        if duration is None:
            # Get video duration using ffprobe
            duration = self._get_video_duration(input_video)

        # Build zoom filter
        # zooms from 1.0 to (1 + zoom_intensity) over zoom_duration seconds
        zoom_filter = f"zoompan=z='min(1+{zoom_intensity}, 1+{zoom_intensity}*min(t,{zoom_duration})/{zoom_duration})':d=1:x='(iw-iw/zoom)/2':y='(ih-ih/zoom)/2':fps=30"

        # Build ffmpeg command
        cmd = [
            self.ffmpeg_path,
            '-i', input_video,
            '-ss', str(start_time),
            '-t', str(duration),
            '-vf', zoom_filter,
            '-c:v', 'libx264',
            '-preset', 'fast',
            '-crf', '23',
            '-c:a', 'aac',
            '-b:a', '128k',
            '-movflags', '+faststart',
            '-y',
            output_video
        ]

        print(f"🎬 Adding zoom effect to: {output_video}")
        print(f"   Zoom: 1.0x → {1 + zoom_intensity}x over {zoom_duration}s")

        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0 and os.path.exists(output_video):
                print(f"✅ Zoom effect applied successfully!")
                return output_video
            else:
                print(f"❌ Zoom effect failed: {result.stderr[:200]}")
                return None
        except Exception as e:
            print(f"❌ Error: {e}")
            return None

    def add_punch_zoom_to_clip(self, video_path, clip_start, clip_end, output_path, zoom_intensity=0.15):
        """
        Add punch zoom to a specific clip from a video

        Parameters:
        - video_path: source video file
        - clip_start: start time in seconds
        - clip_end: end time in seconds
        - output_path: where to save the zoomed clip
        - zoom_intensity: zoom amount (0.15 = 15%)

        Returns:
        - output_path if successful
        """
        duration = clip_end - clip_start

        # First, crop to vertical if needed
        temp_output = output_path.replace('.mp4', '_temp.mp4')

        # Crop to vertical 9:16
        crop_cmd = [
            self.ffmpeg_path,
            '-i', video_path,
            '-ss', str(clip_start),
            '-t', str(duration),
            '-vf', 'crop=ih*9/16:ih,scale=1080:1920',
            '-c:v', 'libx264',
            '-preset', 'fast',
            '-crf', '23',
            '-c:a', 'aac',
            '-b:a', '128k',
            '-y',
            temp_output
        ]

        try:
            subprocess.run(crop_cmd, capture_output=True, check=True)

            # Add zoom to the cropped clip
            result = self.add_punch_zoom(temp_output, output_path, zoom_intensity=zoom_intensity,
                                         zoom_duration=min(1.5, duration / 2))

            # Clean up temp file
            if os.path.exists(temp_output):
                os.remove(temp_output)

            return result

        except Exception as e:
            print(f"❌ Error processing clip: {e}")
            return None

    def _get_video_duration(self, video_path):
        """Get video duration using ffprobe"""
        ffprobe = self.ffmpeg_path.replace('ffmpeg', 'ffprobe')
        if not os.path.exists(ffprobe):
            ffprobe = 'ffprobe'

        cmd = [
            ffprobe,
            '-v', 'error',
            '-show_entries', 'format=duration',
            '-of', 'default=noprint_wrappers=1:nokey=1',
            video_path
        ]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            return float(result.stdout.strip())
        except:
            return 10  # Default fallback


# Standalone test function
def test_zoom_effect():
    """Test the zoom effect on a sample video"""
    zoom = ZoomEffect()

    # Test with a video file
    test_video = "test.mp4"
    output_video = "test_zoomed.mp4"

    if os.path.exists(test_video):
        result = zoom.add_punch_zoom(test_video, output_video, duration=5)
        if result:
            print(f"✅ Zoom test successful! Check {output_video}")
        else:
            print("❌ Zoom test failed")
    else:
        print(f"⚠️ Test video '{test_video}' not found")


if __name__ == '__main__':
    test_zoom_effect()
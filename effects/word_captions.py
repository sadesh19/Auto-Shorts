"""
Word Captions Module - Adds word-level animated captions to video
Creates TikTok/Reels style captions with current word highlighting
"""

import subprocess
import os
import shutil
import json


class WordCaptions:
    def __init__(self):
        self.ffmpeg_path = self._find_ffmpeg()

    def _find_ffmpeg(self):
        """Find ffmpeg executable"""
        if os.path.exists('ffmpeg.exe'):
            return 'ffmpeg.exe'

        ffmpeg = shutil.which('ffmpeg')
        if ffmpeg:
            return ffmpeg

        common_paths = [
            r'C:\ffmpeg\bin\ffmpeg.exe',
            r'C:\Program Files\ffmpeg\bin\ffmpeg.exe',
        ]
        for path in common_paths:
            if os.path.exists(path):
                return path

        return 'ffmpeg'

    def create_ass_captions(self, words, output_ass_path, video_width=1080, video_height=1920):
        """
        Create ASS subtitle file with word highlighting

        Parameters:
        - words: list of dicts with 'word', 'start', 'end' keys
        - output_ass_path: where to save the ASS file
        - video_width, video_height: dimensions of output video
        """

        # ASS format header
        ass_content = f"""[Script Info]
Title: Word Captions
ScriptType: v4.00+
Collisions: Normal
PlayDepth: 0
Timer: 100.0000

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Arial,48,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,1,2,0,7,10,10,50,0
Style: Highlight,Arial,48,&H0000FFFF,&H000000FF,&H00000000,&H00000000,-1,0,0,0,110,110,0,0,1,2,0,7,10,10,50,0

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

        # Add each word as a dialogue line
        for i, word_info in enumerate(words):
            start_time = self._format_ass_time(word_info['start'])
            end_time = self._format_ass_time(word_info['end'])
            word_text = word_info['word'].strip()

            if not word_text:
                continue

            # Use Highlight style for current word
            ass_content += f"Dialogue: 0,{start_time},{end_time},Highlight,,0,0,0,,{word_text}\n"

        # Write to file
        with open(output_ass_path, 'w', encoding='utf-8') as f:
            f.write(ass_content)

        return output_ass_path

    def create_srt_captions(self, words, output_srt_path):
        """
        Create simple SRT subtitle file (backup format)
        """
        with open(output_srt_path, 'w', encoding='utf-8') as f:
            for i, word_info in enumerate(words):
                start = word_info['start']
                end = word_info['end']
                word = word_info['word'].strip()

                if not word:
                    continue

                # Format: HH:MM:SS,mmm
                start_str = self._format_srt_time(start)
                end_str = self._format_srt_time(end)

                f.write(f"{i + 1}\n{start_str} --> {end_str}\n{word}\n\n")

        return output_srt_path

    def _format_ass_time(self, seconds):
        """Format time for ASS: H:MM:SS.cc"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = seconds % 60
        centiseconds = int((secs - int(secs)) * 100)
        return f"{hours}:{minutes:02d}:{int(secs):02d}.{centiseconds:02d}"

    def _format_srt_time(self, seconds):
        """Format time for SRT: HH:MM:SS,mmm"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = seconds % 60
        milliseconds = int((secs - int(secs)) * 1000)
        return f"{hours:02d}:{minutes:02d}:{int(secs):02d},{milliseconds:03d}"

    def burn_captions_to_video(self, input_video, words, output_video, subtitle_style="ass"):
        """
        Burn captions directly into video

        Parameters:
        - input_video: path to input video file
        - words: list of word dicts with 'start', 'end', 'word'
        - output_video: where to save the video with captions
        - subtitle_style: 'ass' (fancy) or 'srt' (simple)

        Returns:
        - output_video path if successful
        """

        # Create subtitle file
        if subtitle_style == "ass":
            sub_path = output_video.replace('.mp4', '.ass')
            self.create_ass_captions(words, sub_path)
            filter_chain = f"ass={sub_path}"
        else:
            sub_path = output_video.replace('.mp4', '.srt')
            self.create_srt_captions(words, sub_path)
            filter_chain = f"subtitles={sub_path}"

        # Burn subtitles into video
        cmd = [
            self.ffmpeg_path,
            '-i', input_video,
            '-vf', filter_chain,
            '-c:v', 'libx264',
            '-preset', 'fast',
            '-crf', '23',
            '-c:a', 'copy',
            '-movflags', '+faststart',
            '-y',
            output_video
        ]

        print(f"📝 Burning {len(words)} captions to: {output_video}")

        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0 and os.path.exists(output_video):
                print(f"✅ Captions burned successfully!")
                # Clean up subtitle file
                if os.path.exists(sub_path):
                    os.remove(sub_path)
                return output_video
            else:
                print(f"❌ Caption burn failed: {result.stderr[:200]}")
                return None
        except Exception as e:
            print(f"❌ Error: {e}")
            return None

    def add_captions_to_clip(self, video_path, clip_start, clip_end, words, output_path):
        """
        Extract a clip and add word captions

        Parameters:
        - video_path: source video
        - clip_start: start time in seconds
        - clip_end: end time in seconds
        - words: list of word dicts for the ENTIRE video
        - output_path: where to save the clip with captions

        Returns:
        - output_path if successful
        """

        duration = clip_end - clip_start

        # Filter words that belong to this clip
        clip_words = [
            w for w in words
            if w['start'] >= clip_start and w['end'] <= clip_end
        ]

        if not clip_words:
            print(f"⚠️ No words found for clip {clip_start}-{clip_end}")
            return None

        # First crop to vertical and extract clip
        temp_video = output_path.replace('.mp4', '_temp.mp4')

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
            temp_video
        ]

        try:
            # Crop the video
            subprocess.run(crop_cmd, capture_output=True, check=True)

            # Adjust word timestamps for the cropped clip
            adjusted_words = []
            for word in clip_words:
                adjusted_words.append({
                    'word': word['word'],
                    'start': word['start'] - clip_start,
                    'end': word['end'] - clip_start,
                    'probability': word.get('probability', 0.9)
                })

            # Burn captions
            result = self.burn_captions_to_video(temp_video, adjusted_words, output_path)

            # Clean up
            if os.path.exists(temp_video):
                os.remove(temp_video)

            return result

        except Exception as e:
            print(f"❌ Error adding captions: {e}")
            return None


def words_from_transcript(transcript_json_path):
    """
    Extract word list from transcript JSON file

    Parameters:
    - transcript_json_path: path to transcript.json file

    Returns:
    - list of word dicts with 'word', 'start', 'end', 'probability'
    """
    with open(transcript_json_path, 'r', encoding='utf-8') as f:
        transcript = json.load(f)

    words = []
    for segment in transcript.get('segments', []):
        for word in segment.get('words', []):
            words.append({
                'word': word['word'],
                'start': word['start'],
                'end': word['end'],
                'probability': word.get('probability', 0.9)
            })

    return words


# Standalone test function
def test_captions():
    """Test captions on a sample video"""
    captions = WordCaptions()

    # Sample words for testing
    test_words = [
        {'word': 'Hello', 'start': 0.0, 'end': 0.5},
        {'word': 'world', 'start': 0.6, 'end': 1.0},
        {'word': 'this', 'start': 1.1, 'end': 1.4},
        {'word': 'is', 'start': 1.5, 'end': 1.7},
        {'word': 'a', 'start': 1.8, 'end': 1.9},
        {'word': 'test', 'start': 2.0, 'end': 2.5},
    ]

    test_video = "test.mp4"
    output_video = "test_with_captions.mp4"

    if os.path.exists(test_video):
        result = captions.burn_captions_to_video(test_video, test_words, output_video)
        if result:
            print(f"✅ Captions test successful! Check {output_video}")
        else:
            print("❌ Captions test failed")
    else:
        print(f"⚠️ Test video '{test_video}' not found")


if __name__ == '__main__':
    test_captions()
import os
import sys
import json
import argparse
import subprocess
import tempfile
from faster_whisper import WhisperModel

def extract_audio(video_path):
    """
    Extracts the audio track from a video file and saves it as a 16kHz mono WAV file.
    """
    if not os.path.exists(video_path):
        print(f"Error: Input file '{video_path}' does not exist.")
        sys.exit(1)
        
    # Create a temporary file path for the wav audio
    temp_dir = tempfile.gettempdir()
    base_name = os.path.splitext(os.path.basename(video_path))[0]
    temp_wav_path = os.path.join(temp_dir, f"{base_name}_temp_audio.wav")
    
    print(f"Extracting audio from '{video_path}' to '{temp_wav_path}'...")
    
    # ffmpeg command to extract audio: mono, 16kHz, PCM 16-bit WAV
    cmd = [
        "ffmpeg",
        "-y",
        "-i", video_path,
        "-vn",
        "-acodec", "pcm_s16le",
        "-ar", "16000",
        "-ac", "1",
        temp_wav_path
    ]
    
    try:
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        print("Audio extraction successful.")
        return temp_wav_path
    except subprocess.CalledProcessError as e:
        print(f"Error during audio extraction: {e}")
        print("ffmpeg output:")
        print(e.stderr)
        sys.exit(1)
    except FileNotFoundError:
        print("Error: ffmpeg is not installed or not in system PATH.")
        sys.exit(1)

def run_transcription(audio_path, model_size="base", device="cpu", compute_type="int8"):
    """
    Transcribes the audio file using faster-whisper and returns structured results.
    """
    print(f"Loading Whisper model '{model_size}' on '{device}' (compute_type={compute_type})...")
    try:
        model = WhisperModel(model_size, device=device, compute_type=compute_type)
    except Exception as e:
        print(f"Error loading model: {e}")
        # If CUDA is requested but fails, try to fall back to CPU
        if device == "cuda":
            print("Failed to load model on CUDA. Falling back to CPU with int8 compute type...")
            model = WhisperModel(model_size, device="cpu", compute_type="int8")
        else:
            sys.exit(1)
            
    print("Transcribing audio...")
    segments, info = model.transcribe(audio_path, beam_size=5, word_timestamps=True)
    
    print(f"Detected language: '{info.language}' with probability {info.language_probability:.2f}")
    
    # Build structured transcription data
    transcription_data = {
        "language": info.language,
        "language_probability": info.language_probability,
        "duration": info.duration,
        "segments": []
    }
    
    print("Processing transcription segments and word timestamps...")
    for segment in segments:
        segment_data = {
            "start": segment.start,
            "end": segment.end,
            "text": segment.text,
            "words": []
        }
        
        if segment.words:
            for word in segment.words:
                segment_data["words"].append({
                    "word": word.word,
                    "start": word.start,
                    "end": word.end,
                    "probability": word.probability
                })
                
        transcription_data["segments"].append(segment_data)
        
    return transcription_data

def save_transcript(data, output_path):
    """
    Saves the transcription data structure as a JSON file.
    """
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"Transcript successfully saved to '{output_path}'.")
    except Exception as e:
        print(f"Error saving transcript JSON: {e}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Extract audio from a video and transcribe it with word-level timestamps using faster-whisper.")
    parser.add_argument("-i", "--input", required=True, help="Path to the input video or audio file.")
    parser.add_argument("-o", "--output", help="Path to save the transcript JSON (defaults to <input_name>_transcript.json).")
    parser.add_argument("-m", "--model", default="base", help="Whisper model size to use (e.g. tiny, base, small, medium, large-v3). Default is 'base'.")
    parser.add_argument("--device", default="cpu", choices=["cpu", "cuda"], help="Device to run inference on. Default is 'cpu'.")
    parser.add_argument("--compute_type", default="int8", help="Compute type to use. Default is 'int8'. Use 'float16' for CUDA GPU.")
    
    args = parser.parse_args()
    
    # Set default output path if not provided
    if not args.output:
        base_dir = os.path.dirname(args.input)
        if not base_dir:
            base_dir = "."
        base_name = os.path.splitext(os.path.basename(args.input))[0]
        args.output = os.path.join(base_dir, f"{base_name}_transcript.json")
        
    temp_wav = None
    try:
        # Step 1: Extract audio
        temp_wav = extract_audio(args.input)
        
        # Step 2: Transcribe audio
        transcript_data = run_transcription(
            temp_wav, 
            model_size=args.model, 
            device=args.device, 
            compute_type=args.compute_type
        )
        
        # Step 3: Save to JSON
        save_transcript(transcript_data, args.output)
        
    finally:
        # Step 4: Cleanup temporary audio file
        if temp_wav and os.path.exists(temp_wav):
            try:
                os.remove(temp_wav)
                print(f"Cleaned up temporary audio file '{temp_wav}'.")
            except Exception as e:
                print(f"Warning: Could not remove temporary file '{temp_wav}': {e}")
                
    print("Transcription pipeline finished successfully!")

if __name__ == "__main__":
    main()

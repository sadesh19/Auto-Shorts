import os
import sys
import subprocess
import urllib.request

def check_ffmpeg():
    print("Checking if ffmpeg is available...")
    try:
        result = subprocess.run(["ffmpeg", "-version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode == 0:
            print("ffmpeg is available!")
            # Print the first line of version info
            print(result.stdout.split('\n')[0])
            return True
        else:
            print("ffmpeg command failed with return code:", result.returncode)
            return False
    except FileNotFoundError:
        print("Error: ffmpeg is not found in the system PATH.")
        return False

def download_sample_audio(url, filename):
    if os.path.exists(filename):
        print(f"Sample audio file '{filename}' already exists.")
        return True
    
    print(f"Downloading sample audio from {url}...")
    try:
        urllib.request.urlretrieve(url, filename)
        print(f"Successfully downloaded '{filename}'.")
        return True
    except Exception as e:
        print(f"Error downloading sample audio: {e}")
        return False

def run_transcription(filename):
    print("Loading faster-whisper model...")
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        print("Error: faster-whisper is not installed in this environment.")
        return False
    
    try:
        # Load a small model on CPU
        model_size = "tiny"
        print(f"Loading '{model_size}' model on CPU...")
        model = WhisperModel(model_size, device="cpu", compute_type="int8")
        
        print("Transcribing...")
        # Transcribe with word-level timestamps enabled
        segments, info = model.transcribe(filename, beam_size=5, word_timestamps=True)
        
        print(f"Detected language: '{info.language}' with probability {info.language_probability:.2f}")
        print("\nTranscription segments:")
        
        for segment in segments:
            print(f"[{segment.start:.2f}s -> {segment.end:.2f}s] {segment.text}")
            print("Word timestamps:")
            for word in segment.words:
                print(f"  - {word.word} [{word.start:.2f}s -> {word.end:.2f}s]")
                
        print("\nTranscription test completed successfully!")
        return True
    except Exception as e:
        print(f"Error during transcription: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("=== Auto Shorts - Environment Verification ===")
    if not check_ffmpeg():
        sys.exit(1)
        
    # Standard JFK speech sample from whisper.cpp repository (~11 seconds)
    sample_url = "https://github.com/ggerganov/whisper.cpp/raw/master/samples/jfk.wav"
    sample_filename = "jfk.wav"
    
    if not download_sample_audio(sample_url, sample_filename):
        sys.exit(1)
        
    if not run_transcription(sample_filename):
        sys.exit(1)
        
    print("Environment setup verification complete and fully functional!")

if __name__ == "__main__":
    main()

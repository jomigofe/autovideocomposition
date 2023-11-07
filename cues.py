import librosa

def detect_passages(audio_file_path, top_db=60):
    # Load the audio file
    y, sr = librosa.load(audio_file_path, sr=None)
    
    # Split the signal into non-silent segments
    segments = librosa.effects.split(y, top_db=top_db)
    
    # Convert segment samples to time
    segment_times = [(start/sr, end/sr) for start, end in segments]
    
    return segment_times

# Test the function
audio_file_path = "path_to_audio.mp3"
passages = detect_passages(audio_file_path)
print(passages)

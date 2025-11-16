

import librosa
from moviepy import VideoFileClip, concatenate_videoclips
from moviepy import video

# Load the audio file

def process_mp3tomp4(filename, id):
    y, sr = librosa.load(f"uploads/{filename}")

    print("loaded")

    # Detect tempo and beat frames
    tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)

    print(f"got tempo {tempo}")

    # Convert beat frames to time
    return librosa.frames_to_time(beat_frames, sr=sr)


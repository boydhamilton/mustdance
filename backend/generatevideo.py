import librosa
from moviepy import VideoFileClip, concatenate_videoclips, AudioFileClip
from moviepy import video
import math
import random

# Load the audio file

def process_mp3tomp4(filename, id):
    y, sr = librosa.load(f"uploads/{filename}")

    print("loaded")

    # Detect tempo and beat frames
    tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)

    print(f"got tempo {tempo}")

    # Convert beat frames to time
    beat_times = librosa.frames_to_time(beat_frames, sr=sr)


    four_bar_ref = 8 # (1/120 minutes per beat (we record 120 bpm) * 60) gives seconds per beat

    four_bar_delta = beat_times[15] - beat_times[0]
    print(four_bar_delta)
    speedup_factor = four_bar_ref / four_bar_delta


    # List of videos and their playback speeds
    dance_moves = [
        {"file": "outlines/clap.mp4"},
        {"file": "outlines/muscle.mp4"},
        {"file": "outlines/roll.mp4"}
    ]

    clips = []

    num_clips = math.floor(librosa.get_duration(y=y, sr=sr) / (four_bar_delta) )
    print(librosa.get_duration(y=y, sr=sr))
    print(num_clips)
    for i in range(num_clips):
        v = random.choice(dance_moves)
        clip = VideoFileClip(v["file"])
        
        # Change playback speed
        if speedup_factor != 1.0:
            clip = video.fx.MultiplySpeed(speedup_factor).apply(clip)
        
        clips.append(clip)

    # Concatenate all clips
    final_clip = concatenate_videoclips(clips)
    print(filename)
    audio = AudioFileClip(f"uploads/{filename}")

    # Set the MP3 as the audio track of the final video
    final_clip = final_clip.with_audio(audio)

    # Export final video
    final_clip.write_videofile(f"output/{id}.mp4", codec="libx264", audio_codec="aac")
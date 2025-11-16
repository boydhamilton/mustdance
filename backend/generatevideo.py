

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


def process_mp3tomp4(filename):
    
    beat_times = getbeattimestamps(filename)

    four_bar_ref = 8 # (1/120 minutes per beat (we record 120 bpm) * 60) gives seconds per beat

    four_bar_delta = beat_times[15] - beat_times[0]
    print(four_bar_delta)
    speedup_factor = four_bar_delta / four_bar_ref


    # List of videos and their playback speeds
    dance_moves = [
        {"file": "resources/test.mp4"}
    ]

    clips = []

    for v in dance_moves:
        clip = VideoFileClip(v["file"])
        
        # Change playback speed
        if speedup_factor != 1.0:
            clip = video.fx.MultiplySpeed(speedup_factor).apply(clip)
        
        clips.append(clip)

    # Concatenate all clips
    final_clip = concatenate_videoclips(clips)

    # Export final video
    final_clip.write_videofile(f"output/{id}.mp4", codec="libx264", audio_codec="aac")

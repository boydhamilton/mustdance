import librosa
from moviepy import VideoFileClip, concatenate_videoclips, AudioFileClip
from moviepy import video, vfx
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
    dance_moves_outline = [
        {"file": "outlines/clap.mp4"},
        {"file": "outlines/muscle.mp4"},
        {"file": "outlines/roll.mp4"}
    ]

    dance_moves_raw = [
        {"file": "moves/clap.mp4"},
        {"file": "moves/muscle.mp4"},
        {"file": "moves/roll.mp4"}
    ]

    clips_outline = []
    clips_raw = []
    

    num_clips = math.floor(librosa.get_duration(y=y, sr=sr) / (four_bar_delta) )
    print(librosa.get_duration(y=y, sr=sr))
    print(num_clips)
    index_list = []
    for i in range(num_clips):
        idx = random.randint(0, len(dance_moves_outline)-1 )
        index_list.append(idx)
        clip_outline = VideoFileClip(dance_moves_outline[idx]["file"])
        
        
        # Change playback speed
        if speedup_factor != 1.0:
            clip_outline = video.fx.MultiplySpeed(speedup_factor).apply(clip_outline)
            clip_outline = video.fx.MirrorX().apply(clip_outline)


        clips_outline.append(clip_outline)
        

    for i in index_list:
        clip_raw = VideoFileClip(dance_moves_raw[idx]["file"])
        if speedup_factor != 1.0:
            clip_raw = video.fx.MultiplySpeed(speedup_factor).apply(clip_raw)
            clips_raw.append(clip_raw)

    # Concatenate all clips_outline    
    final_clip_outline = concatenate_videoclips(clips_outline)


    final_clip_raw = concatenate_videoclips(clips_raw)

    print(filename)
    audio = AudioFileClip(f"uploads/{filename}")

    # Set the MP3 as the audio track of the final video
    final_clip_outline = final_clip_outline.with_audio(audio)

    # Export final video
    final_clip_outline.write_videofile(f"output/{id}.mp4", codec="libx264", audio_codec="aac")

    final_clip_raw.write_videofile(f"comparisons/comparison.mp4")
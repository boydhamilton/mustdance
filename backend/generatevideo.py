import librosa
from moviepy import VideoFileClip, concatenate_videoclips, AudioFileClip
from moviepy import video, vfx
import math
import random
import os
import shutil
import subprocess

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
        {"file": "outlines/jack.mp4"},
        {"file": "outlines/jump.mp4"},
        {"file": "outlines/kick.mp4"},
        {"file": "outlines/roll.mp4"},
        {"file": "outlines/slide.mp4"},
        {"file": "outlines/spin.mp4"},
    ]

    dance_moves_raw = [
        {"file": "moves/jack.mp4"},
        {"file": "moves/jump.mp4"},
        {"file": "moves/kick.mp4"},
        {"file": "moves/roll.mp4"},
        {"file": "moves/slide.mp4"},
        {"file": "moves/spin.mp4"},
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
        # just record the selections; we'll use ffmpeg to speed + concat (faster)
        pass

    # use ffmpeg to create sped-up temp clips and concat them
    ffmpeg_bin = shutil.which("ffmpeg")
    if not ffmpeg_bin:
        raise RuntimeError("ffmpeg not found on PATH - install ffmpeg for fast concat/encode")

    tmp_dir = f"tmp_{id}"
    os.makedirs(tmp_dir, exist_ok=True)

    def atempo_chain(factor: float) -> str:
        # builds an atempo filter chain that ffmpeg accepts (limits 0.5-2.0 per atempo)
        if factor == 1.0:
            return "atempo=1.0"
        parts = []
        # handle >1
        if factor > 1.0:
            while factor > 2.0:
                parts.append("atempo=2.0")
                factor /= 2.0
            parts.append(f"atempo={factor:.6f}")
        else:
            # factor < 1.0
            while factor < 0.5:
                parts.append("atempo=0.5")
                factor /= 0.5
            parts.append(f"atempo={factor:.6f}")
        return ",".join(parts)

    outline_tmp_files = []
    raw_tmp_files = []
    for i, sel_idx in enumerate(index_list):
        src_outline = dance_moves_outline[sel_idx]["file"]
        src_raw = dance_moves_raw[sel_idx]["file"]

        tmp_outline = os.path.join(tmp_dir, f"outline_{i}.mp4")
        tmp_raw = os.path.join(tmp_dir, f"raw_{i}.mp4")

        # speed video with setpts and drop original audio (we'll add the mp3 as final audio)
        vf = f"setpts=PTS/{speedup_factor:.6f}"
        af = atempo_chain(speedup_factor)

        # create tmp_outline (video only)
        cmd_outline = [
            ffmpeg_bin, "-y", "-i", src_outline,
            "-filter_complex", f"[0:v]{vf}[v];[0:a]{af}[a]",
            "-map", "[v]", "-an",
            "-c:v", "libx264", "-preset", "ultrafast", "-crf", "23",
            tmp_outline
        ]
        # some source clips may not have audio - we'll still run the command but ignore audio errors
        try:
            subprocess.run(cmd_outline, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except subprocess.CalledProcessError:
            # fallback: try video-only setpts (no audio filter)
            cmd_outline = [
                ffmpeg_bin, "-y", "-i", src_outline,
                "-filter:v", vf,
                "-an",
                "-c:v", "libx264", "-preset", "ultrafast", "-crf", "23",
                tmp_outline
            ]
            subprocess.run(cmd_outline, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        # create tmp_raw (video only) for comparison
        cmd_raw = [
            ffmpeg_bin, "-y", "-i", src_raw,
            "-filter:v", vf,
            "-an",
            "-c:v", "libx264", "-preset", "ultrafast", "-crf", "23",
            tmp_raw
        ]
        subprocess.run(cmd_raw, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        outline_tmp_files.append(tmp_outline)
        raw_tmp_files.append(tmp_raw)

    # write concat lists
    outline_list = os.path.join(tmp_dir, "outline_list.txt")
    raw_list = os.path.join(tmp_dir, "raw_list.txt")
    with open(outline_list, "w") as f:
        for p in outline_tmp_files:
            f.write(f"file '{os.path.abspath(p)}'\n")
    with open(raw_list, "w") as f:
        for p in raw_tmp_files:
            f.write(f"file '{os.path.abspath(p)}'\n")

    os.makedirs("output", exist_ok=True)
    os.makedirs("comparisons", exist_ok=True)

    # concat outline clips and attach uploaded audio
    final_output = f"output/{id}.mp4"
    cmd_final = [
        ffmpeg_bin, "-y", "-f", "concat", "-safe", "0", "-i", outline_list,
        "-i", f"uploads/{filename}",
        "-map", "0:v", "-map", "1:a",
        "-c:v", "libx264", "-preset", "ultrafast", "-crf", "23",
        "-c:a", "aac", "-b:a", "128k",
        "-shortest",
        final_output
    ]
    subprocess.run(cmd_final, check=True)

    # concat raw clips for comparison (no audio)
    comparison_output = "comparisons/comparison.mp4"
    cmd_comp = [
        ffmpeg_bin, "-y", "-f", "concat", "-safe", "0", "-i", raw_list,
        "-c:v", "libx264", "-preset", "ultrafast", "-crf", "23",
        "-an",
        comparison_output
    ]
    subprocess.run(cmd_comp, check=True)

    # cleanup tmp files
    try:
        for fpath in os.listdir(tmp_dir):
            os.remove(os.path.join(tmp_dir, fpath))
        os.rmdir(tmp_dir)
    except Exception:
        pass

    print(f"wrote {final_output} and {comparison_output}")
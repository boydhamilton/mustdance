from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import uuid
import threading
import generatevideo
from moviepy import VideoFileClip
from videoanalyzer import score_videos
import json
import shutil
import subprocess

app = Flask(__name__)
CORS(app, supports_credentials=True)

currently_generating = {

}

# Receives audio file for processing
@app.route("/upload", methods=["POST"])
def upload():
    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    # save file in uploads directory
    audioid = str(uuid.uuid4())
    filename = audioid + "." + file.filename.split(".")[-1]
    # ensure uploads directory exists
    os.makedirs("uploads", exist_ok=True)
    upload_path = os.path.join("uploads", filename)
    file.save(upload_path)

    thread = threading.Thread(target=generatevideo.process_mp3tomp4, args=(filename,audioid),)
    thread.start()
    currently_generating[audioid] = thread
    return jsonify({"id": audioid}), 200


def process_video(webm_path,):
    mp4_path = webm_path.replace(".webm", ".mp4")

    ffmpeg_bin = shutil.which("ffmpeg")
    used_ffmpeg = False
    if ffmpeg_bin:
        # Configure fast options. Tune with env vars:
        #   FFMPEG_HW_ACCEL = "nvenc" to try NVIDIA hw encoder (h264_nvenc)
        #   DOWNSCALE = "640" to scale width to 640 (keep aspect)
        #   FPS = "24" to force framerate
        hw = os.getenv("FFMPEG_HW_ACCEL", "").lower()
        downscale = os.getenv("DOWNSCALE", "")
        fps = os.getenv("FPS", "")

        if hw == "nvenc":
            vcodec = "h264_nvenc"
            vparams = ["-preset", "fast"]  # nvenc presets differ; tune as needed
        else:
            vcodec = "libx264"
            vparams = ["-preset", "ultrafast", "-crf", "23", "-threads", "0"]

        cmd = [ffmpeg_bin, "-y", "-i", webm_path]

        # optional downscale
        if downscale:
            cmd += ["-vf", f"scale={downscale}:-2"]

        # optional fps
        if fps:
            cmd += ["-r", fps]

        # video codec + params
        cmd += ["-c:v", vcodec] + vparams

        # audio: try to copy if present to avoid re-encode; otherwise encode to aac
        # using "-c:a copy" may fail if audio codec incompatible with mp4; fallback below handles errors
        cmd += ["-c:a", "aac", "-b:a", "128k"]

        cmd += [mp4_path]

        try:
            print("Running ffmpeg:", " ".join(cmd))
            subprocess.run(cmd, check=True)
            used_ffmpeg = True
        except Exception as e:
            print("ffmpeg conversion failed, falling back to moviepy:", e)

    # Fallback to moviepy if ffmpeg not available or failed
    if not used_ffmpeg:
        try:
            clip = VideoFileClip(webm_path)
            clip.write_videofile(mp4_path, codec="libx264")
        except Exception as e:
            print("moviepy conversion failed:", e)
            return

    print(f"Saved webm: {webm_path}")
    print(f"Saved mp4 : {mp4_path}")

    comparison_video = os.path.join("comparisons", "comparison.mp4")
    scores = []
    if os.path.exists(comparison_video):
        print("\nRunning pose comparison...")
        scores = score_videos(mp4_path, comparison_video, step=2.0)
        print("Similarity Scores:")
        print(sum(scores) / len(scores) if scores else 0.0)
    else:
        print("comparison.mp4 not found in comparisons folder. Skipping scoring.")

    scores_dir = "scores"
    id= os.path.splitext(os.path.basename(mp4_path))[0]
    os.makedirs(scores_dir, exist_ok=True)
    json_path = os.path.join(scores_dir, id + ".json")
    total_score = int(sum([s * 100 for s in scores])) if scores else 0.0
    percent_score = (total_score / len(scores)) if scores else 0.0
    data = {"total_score": total_score, "percent_score": percent_score}
    with open(json_path, "w") as jf:
        json.dump(data, jf, indent=4)


@app.route("/upload_video", methods=["POST"])
def upload_video():
    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    os.makedirs("comparisons", exist_ok=True)
    webm_path = os.path.join("comparisons", file.filename)
    file.save(webm_path)

    thread = threading.Thread(target=process_video, args=(webm_path,))
    thread.start()
    return jsonify({"status": "processing"}), 200

@app.route("/ready/<id>",)
def ready(id):
    output_path = os.path.join("output", id + ".mp4")
    if os.path.exists(output_path) and currently_generating[id].is_alive() == False:
        return jsonify({"ready": True, "url": f"/download/{id}"}), 200
    else:
        return jsonify({"ready": False}), 200
    
@app.route("/download/<id>")
def download(id):
    output_path = os.path.join("output", id + ".mp4")
    if os.path.exists(output_path):
        return send_from_directory("output", id + ".mp4")
    else:
        return jsonify({"error": "File not found"}), 404

@app.route("/scoreready/<id>")
def scoreready(id):
    score_path = os.path.join("scores", id + ".json")
    if os.path.exists(score_path):
        return jsonify({"ready": True, "url": f"/score/{id}"}), 200
    else:
        return jsonify({"ready": False}), 200

@app.route("/score/<id>")
def score(id):
    score_path = os.path.join("scores", id + ".json")
    if os.path.exists(score_path):
        with open(score_path, "r") as f:
            score_data = f.read()
        return score_data, 200
    else:
        return jsonify({"error": "Score not found"}), 404

# Example of making Spotify request using token
@app.route("/me")
def me():
    access_token = request.args.get("access_token")
    sp = spotipy.Spotify(auth=access_token)
    return jsonify(sp.current_user())

# debug lol 
@app.route("/")
def home():
    return "Flask server is running!"

if __name__ == "__main__":
    app.run(port=5000, debug=True)

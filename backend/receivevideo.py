from fastapi import FastAPI, File, UploadFile
import uvicorn
import os
from moviepy import VideoFileClip
from videoanalyzer import score_videos
from fastapi.middleware.cors import CORSMiddleware
import threading

app = FastAPI()

origins = [
        "http://localhost:3000",  # Your frontend development server
        "https://your-production-frontend.com", # Your production frontend URL
    ]

app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,  # Set to True if your frontend sends cookies or authorization headers
        allow_methods=["*"],     # Or specify specific methods like ["GET", "POST"]
        allow_headers=["*"],     # Or specify specific headers
    )

UPLOAD_DIR = "comparisons"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def process_video(webm_path):
    # Convert to mp4
    mp4_path = webm_path.replace(".webm", ".mp4")

    clip = VideoFileClip(webm_path)
    clip.write_videofile(mp4_path, codec="libx264")

    print(f"Saved webm: {webm_path}")
    print(f"Saved mp4 : {mp4_path}")

    comparison_video = os.path.join("comparisons", "comparison.mp4")
    scores = []
    if os.path.exists(comparison_video):
        print("\nRunning pose comparison...")
        scores = score_videos(mp4_path, comparison_video, step=0.2)
        
        print("Similarity Scores:")
        print(sum(scores) / len(scores) if scores else 0.0)
    else:
        print("comparison.mp4 not found in uploads folder. Skipping scoring.")

    import json
    scores_dir = "scores"
    os.makedirs(scores_dir, exist_ok=True)
    json_path = os.path.join(scores_dir, os.path.splitext(os.path.basename(mp4_path))[0] + ".json")
    total_score = int(sum([s * 100 for s in scores])) if scores else 0.0
    percent_score = (total_score / len(scores)) if scores else 0.0
    data = {"total_score": total_score, "percent_score": percent_score}
    with open(json_path, "w") as jf:
        json.dump(data, jf, indent=4)


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    # Save original webm
    webm_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(webm_path, "wb") as f:
        f.write(await file.read())

    # Process video
    thread = threading.Thread(target=process_video, args=(webm_path,))

    return {"status": "success"}



if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

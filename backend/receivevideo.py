from fastapi import FastAPI, File, UploadFile
import uvicorn
import os
from moviepy import VideoFileClip
app = FastAPI()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    # Save original webm
    webm_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(webm_path, "wb") as f:
        f.write(await file.read())

    # Convert to mp4
    mp4_path = webm_path.replace(".webm", ".mp4")

    clip = VideoFileClip(webm_path)
    clip.write_videofile(mp4_path, codec="libx264")

    print(f"Saved webm: {webm_path}")
    print(f"Saved mp4 : {mp4_path}")

    return {"status": "success", "mp4_saved": mp4_path}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

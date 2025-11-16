from flask import Flask, redirect, request, jsonify, make_response, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import uuid
import threading
import generatevideo

load_dotenv()

app = Flask(__name__)
CORS(app, supports_credentials=True)

# sp_oauth = SpotifyOAuth(
#     client_id=os.getenv("SPOTIPY_CLIENT_ID"),
#     client_secret=os.getenv("SPOTIPY_CLIENT_SECRET"),
#     redirect_uri=os.getenv("SPOTIPY_REDIRECT_URI"),
#     scope="user-read-email user-library-read",
# )

# # 1. React → Flask: “Start login”
# @app.route("/login")
# def login():
#     auth_url = sp_oauth.get_authorize_url()
#     return jsonify({"url": auth_url})

# # 2. Spotify → Flask: Callback
# @app.route("/callback")
# def callback():
#     code = request.args.get("code")
#     token_info = sp_oauth.get_access_token(code, as_dict=True)

#     resp = make_response(redirect("http://localhost:3000/songs"))

#     return redirect(f"http://localhost:3000/callback?access_token={token_info["access_token"]}&refresh_token={token_info["refresh_token"]}&expires_in={token_info["expires_in"]}")

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

    thread = threading.Thread(target=generatevideo.process_mp3tomp4, args=(filename,audioid))
    thread.start()
    return jsonify({"id": audioid}), 200

@app.route("/ready/<id>",)
def ready(id):
    output_path = os.path.join("output", id + ".mp4")
    if os.path.exists(output_path):
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

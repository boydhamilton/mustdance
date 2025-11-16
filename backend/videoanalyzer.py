import cv2
import mediapipe as mp
import numpy as np

mp_pose = mp.solutions.pose

# -----------------------------------------
# Extract pose landmarks from a single image
# -----------------------------------------
def get_pose_landmarks(image):
    with mp_pose.Pose(static_image_mode=True) as pose:
        results = pose.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        if not results.pose_landmarks:
            return None

        h, w, _ = image.shape
        landmarks = []
        for lm in results.pose_landmarks.landmark:
            landmarks.append(np.array([lm.x * w, lm.y * h]))

        return np.array(landmarks)

# -----------------------------------------
# Normalize pose and compute similarity score
# -----------------------------------------
def compare_poses(landmarksA, landmarksB):
    def normalize(landmarks):
        left_hip = landmarks[23]
        right_hip = landmarks[24]
        center = (left_hip + right_hip) / 2
        scale = np.linalg.norm(left_hip - right_hip)
        if scale < 1e-6:
            scale = 1.0
        return (landmarks - center) / scale

    A = normalize(landmarksA)
    B = normalize(landmarksB)

    diffs = np.linalg.norm(A - B, axis=1)
    score = 1 - (np.mean(diffs) / 2.0)
    return float(max(0, min(1, score)))

# -----------------------------------------
# Grab a frame at a specific time
# -----------------------------------------
def get_frame_at_time(video_path, t):
    cap = cv2.VideoCapture(video_path)
    cap.set(cv2.CAP_PROP_POS_MSEC, t * 1000)
    ret, frame = cap.read()
    cap.release()
    return frame if ret else None

# -----------------------------------------
# Main scoring function comparing both videos
# -----------------------------------------
def score_videos(videoA, videoB, step=1.0):
    capA = cv2.VideoCapture(videoA)
    capB = cv2.VideoCapture(videoB)

    fpsA = capA.get(cv2.CAP_PROP_FPS)
    framesA = capA.get(cv2.CAP_PROP_FRAME_COUNT)
    durationA = framesA / fpsA if fpsA else 0

    fpsB = capB.get(cv2.CAP_PROP_FPS)
    framesB = capB.get(cv2.CAP_PROP_FRAME_COUNT)
    durationB = framesB / fpsB if fpsB else 0

    duration = min(durationA, durationB)

    capA.release()
    capB.release()

    scores = []

    t = 0.0
    while t < duration:
        frameA = get_frame_at_time(videoA, t)
        frameB = get_frame_at_time(videoB, t)

        lA = get_pose_landmarks(frameA)
        lB = get_pose_landmarks(frameB)

        if lA is None or lB is None:
            scores.append(0.0)
        else:
            scores.append(compare_poses(lA, lB))

        t += step

    return scores

# -----------------------------------------
# Run scoring directly when executing script
# -----------------------------------------
if __name__ == "__main__":
    recording = "recording.mp4"
    comparison = "comparison.mp4"

    result_scores = score_videos(recording, comparison, step=1.0)

    print("Pose similarity scores:")
    print(result_scores)

import cv2
import mediapipe as mp
import numpy as np

mp_selfie = mp.solutions.selfie_segmentation

cap = cv2.VideoCapture("boyd3.mp4")
# read fps from source, fallback to 30
fps = cap.get(cv2.CAP_PROP_FPS) or 30
out = None
output_path = "mask_output.mp4"

with mp_selfie.SelfieSegmentation(model_selection=1) as segmenter:
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = segmenter.process(rgb)

        # make the mask white (255) only where model predicts person, black elsewhere
        mask = (result.segmentation_mask > 0.5).astype(np.uint8) * 255
        # ensure mask matches frame size
        mask = cv2.resize(mask, (frame.shape[1], frame.shape[0]))

        # convert to 3-channel BGR so VideoWriter reliably accepts it
        mask_bgr = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)

        # initialize writer on first frame
        if out is None:
            height, width = frame.shape[:2]
            fourcc = cv2.VideoWriter_fourcc(*"mp4v")
            out = cv2.VideoWriter(output_path, fourcc, fps if fps > 0 else 30, (width, height))

        # write the mask frame to mp4
        out.write(mask_bgr)

        person = cv2.bitwise_and(frame, frame, mask=mask)

        cv2.imshow("mask", mask)
        if cv2.waitKey(1) == 27:
            break

    # cleanup
    if out is not None:
        out.release()
cap.release()
cv2.destroyAllWindows()

import cv2
import mediapipe as mp
import numpy as np

mp_selfie = mp.solutions.selfie_segmentation

cap = cv2.VideoCapture("boyd4.mp4")
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

        # Get segmentation mask (person = 1, background = 0)
        mask = (result.segmentation_mask > 0.5).astype(np.uint8) * 255
        mask = cv2.resize(mask, (frame.shape[1], frame.shape[0]))

        # Additional white background removal: pixels with high values across all channels get zeroed
        # This catches overexposed whites that selfie segmentation might miss
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        white_bg = (gray > 230).astype(np.uint8)
        mask = cv2.bitwise_and(mask, mask, mask=cv2.bitwise_not(white_bg * 255))

        # Clean up mask: erode small noise, dilate to fill holes
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

        # Smooth edges with Gaussian blur
        mask = cv2.GaussianBlur(mask, (5, 5), 0)
        # Re-threshold to binary after blur
        _, mask = cv2.threshold(mask, 127, 255, cv2.THRESH_BINARY)

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

import cv2
import mediapipe as mp
import numpy as np

mp_selfie = mp.solutions.selfie_segmentation

cap = cv2.VideoCapture("dance.mp4")

with mp_selfie.SelfieSegmentation(model_selection=1) as segmenter:
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = segmenter.process(rgb)

        mask = (result.segmentation_mask > 0.5).astype(np.uint8) * 255
        person = cv2.bitwise_and(frame, frame, mask=mask)

        cv2.imshow("mask", mask)
        cv2.imshow("person", person)
        if cv2.waitKey(1) == 27:
            break

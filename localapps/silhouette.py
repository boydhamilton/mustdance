import cv2
import mediapipe as mp
import numpy as np
from typing import Optional

mp_selfie = mp.solutions.selfie_segmentation


def generate_silhouette_video(
    input_path: str,
    output_path: str = "../backend/outlines/mask_output.mp4",
    model_selection: int = 1,
    show_window: bool = False,
) -> str:
    """Process `input_path` and write a binary silhouette mask video to `output_path`.

    Returns `output_path` on success. Raises `FileNotFoundError` if `input_path` can't be opened.
    """
    cap = cv2.VideoCapture(input_path)
    if not cap.isOpened():
        raise FileNotFoundError(f"Cannot open video: {input_path}")

    # read fps from source, fallback to 30
    fps = cap.get(cv2.CAP_PROP_FPS) or 30
    out: Optional[cv2.VideoWriter] = None

    with mp_selfie.SelfieSegmentation(model_selection=model_selection) as segmenter:
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

            if show_window:
                cv2.imshow("mask", mask)
                if cv2.waitKey(1) == 27:
                    break

    # cleanup
    if out is not None:
        out.release()
    cap.release()
    if show_window:
        cv2.destroyAllWindows()

    return output_path


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Generate silhouette mask video from input video")
    parser.add_argument("input", nargs="?", default="firsttest.mp4", help="input video path")
    parser.add_argument("-o", "--output", default="../backend/outlines/mask_output.mp4", help="output video path")
    parser.add_argument("--model-selection", type=int, default=1, help="mediapipe SelfieSegmentation model_selection")
    parser.add_argument("--show", action="store_true", help="show mask window while processing")
    args = parser.parse_args()

    generate_silhouette_video(args.input, args.output, model_selection=args.model_selection, show_window=args.show)

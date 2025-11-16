"use client";

import { useEffect, useRef, useState } from "react";
import Webcam from "react-webcam";

export default function WebcamPose() {
  const webcamRef = useRef<Webcam>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [loaded, setLoaded] = useState(false);

  useEffect(() => {
    const script = document.createElement("script");
    script.src =
      "https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@latest/dist/tasks-vision.js";
    script.async = true;

    script.onload = () => {
      setLoaded(true);
    };

    document.body.appendChild(script);
  }, []);

  useEffect(() => {
    if (!loaded) return;

    const vision = (window as any).vision;

    if (!vision) return;

    let poseLandmarker: any = null;

    const initModel = async () => {
      const fileset = await vision.FilesetResolver.forVisionTasks(
        "https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@latest/wasm"
      );

      poseLandmarker = await vision.PoseLandmarker.createFromOptions(fileset, {
        baseOptions: {
          modelAssetPath:
            "https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@latest/pose_landmarker_lite.task",
        },
        runningMode: "VIDEO",
        numPoses: 1,
      });

      startProcessing();
    };

    const startProcessing = () => {
      const renderLoop = () => {
        const video = webcamRef.current?.video;
        if (!video || !poseLandmarker) {
          requestAnimationFrame(renderLoop);
          return;
        }

        if (video.readyState === 4) {
          poseLandmarker.detectForVideo(
            video,
            performance.now(),
            (result: any) => {
              draw(result);
            }
          );
        }

        requestAnimationFrame(renderLoop);
      };

      requestAnimationFrame(renderLoop);
    };

    const draw = (result: any) => {
      const canvas = canvasRef.current;
      const ctx = canvas?.getContext("2d");
      const video = webcamRef.current?.video;

      if (!canvas || !ctx || !video) return;

      ctx.clearRect(0, 0, canvas.width, canvas.height);
      ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

      const landmarks = result.landmarks?.[0];
      if (!landmarks) return;

      ctx.fillStyle = "lime";

      for (let lm of landmarks) {
        ctx.beginPath();
        ctx.arc(lm.x * canvas.width, lm.y * canvas.height, 5, 0, Math.PI * 2);
        ctx.fill();
      }
    };

    initModel();
  }, [loaded]);

  return (
    <div className="flex flex-col items-center">
      {!loaded && <p>Loading pose model...</p>}

      <Webcam
        ref={webcamRef}
        mirrored
        style={{ width: 640, height: 480 }}
        videoConstraints={{ width: 640, height: 480 }}
      />

      <canvas
        ref={canvasRef}
        width={640}
        height={480}
        className="rounded-lg shadow border mt-4"
      />
    </div>
  );
}

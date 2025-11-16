"use client";

import { useSearchParams, useRouter } from "next/navigation";
import { useRef, useState } from "react";
import Webcam from "react-webcam";

export default function DancePage() {
  const webcamRef = useRef<Webcam>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);

  const videoRef = useRef<HTMLVideoElement | null>(null);

  const [recording, setRecording] = useState(false);
  const [status, setStatus] = useState<string | null>(null);
  const [countdown, setCountdown] = useState<string>("Waiting for start...");

  const params = useSearchParams();
  const router = useRouter();
  const id = params.get("id") || "";

  const apiBase = (process.env.NEXT_PUBLIC_API_URL as string) || "http://localhost:5000";

  const startCountdown = () => {
    setRecording(true);
    setCountdown("3")
    setTimeout(() => setCountdown("2"), 1000);
    setTimeout(() => setCountdown("1"), 2000);
    setTimeout(() => { setCountdown(""); startRecording() }, 3000);
  }

  // Start Recording
  const startRecording = () => {
    const stream = webcamRef.current?.stream as MediaStream | undefined;
    videoRef.current?.play().catch(() => { });
    if (!stream) {
      setStatus("Camera not available");
      return;
    }

    chunksRef.current = [];
    const recorder = new MediaRecorder(stream);
    recorder.ondataavailable = (e) => {
      if (e.data.size > 0) chunksRef.current.push(e.data);
    };

    recorder.onstop = async () => {
      const blob = new Blob(chunksRef.current, { type: "video/webm" });
      const formData = new FormData();
      formData.append("file", blob, id + ".webm");

      try {
        setStatus("Uploading...");
        const response = await fetch(`http://localhost:5000/upload_video`, { method: "POST", body: formData, headers: { 'Access-Control-Request-Method': 'POST' } });
        const data = await response.json();
        console.log("Backend response:", data);
        router.push("/score?id=" + id)
      } catch (err) {
        console.error("Upload error:", err);
        setStatus("Upload failed");
      }
    };

    recorder.start();
    mediaRecorderRef.current = recorder;
    setStatus("Recording");
  };

  // Stop Recording
  const stopRecording = () => {
    mediaRecorderRef.current?.stop();
    setRecording(false);
  };

  return (
    <div className="min-h-screen bg-black text-white flex flex-col">
      {/* Large flat video area */}
      <div className="w-full max-w-5xl mx-auto h-[76vh] max-h-[980px] flex items-center justify-center overflow-hidden relative">
        <video
          ref={videoRef}
          playsInline
          className="w-full h-full object-contain"
          src={`${apiBase}/download/${id}`}
          onEnded={stopRecording}
        />
        <div className="absolute top-4 left-1/2 transform -translate-x-1/2 bg-black/50 text-white text-xl font-black px-3 py-1 rounded pointer-events-none">
          {countdown}
        </div>
      </div>

      {/* Controls below the video */}
      <div className="w-full p-4 flex flex-col items-center gap-3 bg-transparent">
        <div className="flex items-center gap-3">
          {!recording ? (
            <button
              onClick={startCountdown}
              className="px-4 py-2 bg-green-600 hover:bg-green-500 text-white rounded-md"
            >
              Start Recording
            </button>
          ) : <></>}
        </div>
      </div>

      {/* Hidden webcam used for recording (higher resolution) */}
      <Webcam ref={webcamRef} audio={false} className="hidden" videoConstraints={{ width: 1280, height: 720 }} />
    </div>
  );
}

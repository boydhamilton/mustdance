"use client";

import { useSearchParams } from "next/navigation";
import { useRef, useState } from "react";
import Webcam from "react-webcam";

export default function WebcamRecorder() {
  const webcamRef = useRef<Webcam>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);

  const videoRef = useRef<HTMLVideoElement | null>(null);

  const [downloadUrl, setDownloadUrl] = useState<string | null>(null);
  const [recording, setRecording] = useState(false);

  const params = useSearchParams();

  const id = params.get("id") || "";

  // Start Recording
  const startRecording = () => {
    const stream = webcamRef.current?.stream;
    videoRef.current!.play();
    if (!stream) return;

    chunksRef.current = []; // reset chunks from last recording
    const recorder = new MediaRecorder(stream);

    recorder.ondataavailable = (e) => {
      if (e.data.size > 0) chunksRef.current.push(e.data);
    };

    recorder.onstop = () => {
      const blob = new Blob(chunksRef.current, { type: "video/webm" });
      const url = URL.createObjectURL(blob);
      setDownloadUrl(url);

      const a = document.createElement('a');
      a.href = url;
      a.download = 'recording.webm';
      a.click();
      // optionally revoke immediately after a short delay:
      setTimeout(() => URL.revokeObjectURL(url), 1000);
    };

    recorder.start();
    mediaRecorderRef.current = recorder;
    setRecording(true);
  };

  // Stop Recording
  const stopRecording = () => {
    mediaRecorderRef.current?.stop();
    setRecording(false);
  };

  return (
    <div className="flex flex-col items-center gap-4 mt-8">

      {/* Hidden webcam */}
      <Webcam
        ref={webcamRef}
        audio={false}
        className="hidden"
        videoConstraints={{ width: 640, height: 480 }}
      />

      <video
        ref={videoRef}
        muted
        playsInline
        className="bg-black max-w-3/4"
        src={"http://localhost:5000/download/" + id}
        onEnded={stopRecording}
      ></video>

      {/* Buttons */}
      {!recording && (
        <button
          onClick={startRecording}
          className="px-4 py-2 bg-green-600 text-white rounded"
        >
          Start Recording
        </button>
      )}
    </div>
  );
}

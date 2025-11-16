"use client";

import { useRef, useState } from "react";
import Webcam from "react-webcam";

export default function WebcamRecorder() {
  const webcamRef = useRef<Webcam>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);

  const [isRecording, setIsRecording] = useState(false);
  const [recordedChunks, setRecordedChunks] = useState<Blob[]>([]);
  const [videoURL, setVideoURL] = useState<string | null>(null);

  const startRecording = () => {
    setRecordedChunks([]);
    setVideoURL(null);

    const stream = webcamRef.current?.video?.srcObject as MediaStream;
    if (!stream) {
      console.error("No webcam stream available");
      return;
    }

    const recorder = new MediaRecorder(stream, {
      mimeType: "video/webm; codecs=vp9",
    });

    recorder.ondataavailable = (event) => {
      if (event.data.size > 0) {
        setRecordedChunks((prev) => [...prev, event.data]);
      }
    };

    recorder.start();
    mediaRecorderRef.current = recorder;
    setIsRecording(true);
  };

  const stopRecording = () => {
    if (!mediaRecorderRef.current) return;

    mediaRecorderRef.current.stop();
    setIsRecording(false);

    setTimeout(() => {
      const blob = new Blob(recordedChunks, { type: "video/webm" });
      const url = URL.createObjectURL(blob);
      setVideoURL(url);
    }, 300);
  };

  const downloadRecording = () => {
    if (recordedChunks.length === 0) return;

    const blob = new Blob(recordedChunks, { type: "video/webm" });
    const url = URL.createObjectURL(blob);

    const a = document.createElement("a");
    a.style.display = "none";
    a.href = url;
    a.download = "webcam_recording.webm";
    document.body.appendChild(a);
    a.click();

    URL.revokeObjectURL(url);
  };

  return (
    <div className="flex flex-col items-center space-y-4 p-6">
      <h1 className="text-xl font-semibold">Webcam Recorder</h1>

      {/* Webcam Feed */}
      <Webcam
        ref={webcamRef}
        audio={false}
        style={{ width: 640, height: 480 }}
      />

      {/* Start/Stop Buttons */}
      {!isRecording ? (
        <button
          onClick={startRecording}
          className="px-6 py-2 bg-green-600 text-white rounded"
        >
          Start Recording
        </button>
      ) : (
        <button
          onClick={stopRecording}
          className="px-6 py-2 bg-red-600 text-white rounded"
        >
          Stop Recording
        </button>
      )}

      {/* Video Preview */}
      {videoURL && (
        <div className="flex flex-col items-center">
          <h2 className="font-medium">Preview Recording</h2>
          <video
            controls
            src={videoURL}
            className="border rounded mt-2"
            style={{ width: 640 }}
          />
        </div>
      )}

      {/* Download Button */}
      {videoURL && (
        <button
          onClick={downloadRecording}
          className="px-6 py-2 bg-blue-600 text-white rounded"
        >
          Download Recording
        </button>
      )}
    </div>
  );
}

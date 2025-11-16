"use client"
import React, { useEffect, useRef } from "react";

export default function Setup() {
	const videoRef = useRef<HTMLVideoElement | null>(null);

	useEffect(() => {
		let mounted = true;
		let localStream: MediaStream | null = null;
		const videoEl = videoRef.current;

		async function start() {
			try {
				const stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: false });
				if (!mounted) return;
				localStream = stream;
				if (videoEl) {
					videoEl.srcObject = stream;
					await videoEl.play().catch(() => { });
				}
			} catch (err) {
				// intentionally minimal: log error and allow user to manage permissions
				console.error("Could not start camera", err);
			}
		}

		start();

		return () => {
			mounted = false;
			if (localStream) {
				localStream.getTracks().forEach((t) => t.stop());
			}
			if (videoEl) {
				// clear the srcObject on the same element we used
				try {
					(videoEl as HTMLVideoElement).srcObject = null;
				} catch { }
			}
		};
	}, []);

	return (
		<div className="min-h-screen flex items-center justify-center bg-black">
			<div className="flex flex-col">
				<div>Setup your </div>
				<video ref={videoRef} className="w-full max-w-3xl rounded" playsInline muted autoPlay />
				<div></div>
			</div>
		</div>
	);
}
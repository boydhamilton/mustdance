"use client"
import { useSearchParams, useRouter } from "next/navigation";
import React, { useEffect, useRef, useState } from "react";
import { PiPerson } from "react-icons/pi";

export default function Setup() {
	const videoRef = useRef<HTMLVideoElement | null>(null);
	const [danceReady, setDanceReady] = useState(false);
	const [count, setCount] = useState(0);

	const router = useRouter();

	const params = useSearchParams();
	const id = params.get("id") || "";

	useEffect(() => {
		if (danceReady) return;

		// fetch dance readiness
		const apiBase = (process.env.NEXT_PUBLIC_API_URL as string) || "http://localhost:5000";

		fetch(apiBase + '/ready/' + id)
			.then(res => res.json())
			.then(data => {
				if (data.ready) {
					setDanceReady(true);
				}
			})

		const timer = setTimeout(() => {
			setCount((c) => c + 1);
		}, 5000);

		return () => clearTimeout(timer);

	}, [count, danceReady])


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
	}, [])

	return (
		<div className="min-h-screen flex items-center justify-center p-6">
			<div className="w-full max-w-2xl bg-gray-900 border border-gray-700 rounded-2xl shadow-lg p-8">
				<h1 className="text-2xl font-semibold mb-2 text-white">Camera Setup</h1>
				<p className="text-sm text-gray-300 mb-6">Allow camera access and position yourself in the frame.</p>
				{/* video container */}
				<div className="relative w-full bg-black rounded-lg overflow-hidden">
					<video ref={videoRef} className="w-full object-cover" playsInline muted autoPlay />
					{/* Overlay text (non-interactive) */}
					<div className="absolute top-4 left-4 bg-black/50 text-white text-sm px-3 py-1 rounded pointer-events-none">Ensure your whole body is in frame</div>
				</div>
				<div className="mt-4 flex items-center gap-3">
					<button
						disabled={!danceReady}
						aria-disabled={!danceReady}
						className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed text-white rounded-md"
						onClick={() => danceReady ? router.push(`/dance?id=${id}`) : undefined}
					>
						{danceReady ? "Dance!" : "Loading..."}
					</button>
					<button onClick={() => window.history.back()} className="px-4 py-2 border border-gray-600 text-gray-200 rounded-md">Back</button>
				</div>
			</div>
		</div>
	);
}
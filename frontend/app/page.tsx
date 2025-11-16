"use client";
import React, { useEffect, useMemo, useState } from "react";

export default function HomePage() {
	const [file, setFile] = useState<File | null>(null);
	const [status, setStatus] = useState<string | null>(null);
	const [uploading, setUploading] = useState(false);

	function onFileChange(e: React.ChangeEvent<HTMLInputElement>) {
		const f = e.target.files?.[0] ?? null;
		setFile(f);
		setStatus(null);
	}

	async function upload() {
		if (!file) {
			setStatus("Please select an audio file to upload.");
			return;
		}
		if (!file.type.startsWith("audio/")) {
			setStatus("Selected file is not an audio file.");
			return;
		}

		const form = new FormData();
		form.append("file", file);

		try {
			setUploading(true);
			setStatus("Uploading...");

			const apiBase = (process.env.NEXT_PUBLIC_API_URL as string) || "http://localhost:5000";
			const res = await fetch(`${apiBase}/upload`, {
				method: "POST",
				body: form,
			});

			if (!res.ok) {
				const text = await res.text().catch(() => "");
				setStatus(`Upload failed: ${res.status} ${text}`);
			} else {
				setStatus("Upload successful.");
				setFile(null);
				const input = document.getElementById("audio-input") as HTMLInputElement | null;
				if (input) input.value = "";
			}
		} catch (err: unknown) {
			const message = err instanceof Error ? err.message : String(err);
			setStatus(`Upload error: ${message}`);
		} finally {
			setUploading(false);
		}
	}

	const previewUrl = useMemo(() => (file ? URL.createObjectURL(file) : null), [file]);

	useEffect(() => {
		return () => {
			if (previewUrl) URL.revokeObjectURL(previewUrl);
		};
	}, [previewUrl]);

	return (
		<div className="min-h-screen flex items-center justify-center p-6">
			<div className="w-full max-w-2xl bg-gray-900 border border-gray-700 rounded-2xl shadow-lg p-8">
				<h1 className="text-3xl font-semibold mb-4">Upload a song</h1>

				<p className="text-sm text-gray-300 mb-6">Drop or choose an audio file to upload. Supported types: mp3, wav, m4a, etc.</p>

				<label
					htmlFor="audio-input"
					className="block w-full p-6 mb-4 rounded-lg border-2 border-dashed border-gray-700 hover:border-indigo-500 transition-colors cursor-pointer"
				>
					<input id="audio-input" type="file" accept="audio/*" onChange={onFileChange} className="sr-only" />
					<div className="flex items-center justify-between gap-4">
						<div>
							<div className="text-lg font-medium">{file ? file.name : "Choose an audio file"}</div>
							{file && <div className="text-sm text-gray-400">{Math.round(file.size / 1024)} KB</div>}
						</div>
						<div>
							<svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8 text-indigo-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
								<path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 3v12m0 0l3-3m-3 3-3-3M21 21H3" />
							</svg>
						</div>
					</div>
				</label>

				<div className="flex items-center gap-3">
					<button
						onClick={upload}
						disabled={uploading || !file}
						className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white rounded-md"
					>
						{uploading ? "Uploading..." : "Dance!"}
					</button>

					<button
						onClick={() => {
							setFile(null);
							setStatus(null);
							const input = document.getElementById("audio-input") as HTMLInputElement | null;
							if (input) input.value = "";
						}}
						className="px-4 py-2 border border-gray-600 text-gray-200 rounded-md"
					>
						Clear
					</button>

					{status && <div className="ml-auto text-sm text-gray-300">{status}</div>}
				</div>
			</div>
		</div>
	);
}
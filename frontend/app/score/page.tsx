"use client"
import Loader from "@/components/loader";
import { useRouter, useSearchParams } from "next/navigation";
import { useEffect, useState } from "react";

function ProgressRing({ percent, size = 140, stroke = 12 }: { percent: number; size?: number; stroke?: number }) {
	const radius = (size - stroke) / 2
	const circumference = 2 * Math.PI * radius
	const offset = circumference * (1 - Math.max(0, Math.min(100, percent)) / 100)

	return (
		<svg className="mx-auto block" width={size} height={size} viewBox={`0 0 ${size} ${size}`} aria-hidden="true">
			<defs>
				<linearGradient id="ringGrad" x1="0%" x2="100%">
					<stop offset="0%" stopColor="#06b6d4" />
					<stop offset="100%" stopColor="#3b82f6" />
				</linearGradient>
			</defs>
			<g transform={`translate(${size / 2}, ${size / 2})`}>
				<circle r={radius} fill="transparent" stroke="rgba(255,255,255,0.04)" strokeWidth={stroke} />
				<circle
					r={radius}
					fill="transparent"
					stroke="url(#ringGrad)"
					strokeWidth={stroke}
					strokeLinecap="round"
					strokeDasharray={`${circumference} ${circumference}`}
					strokeDashoffset={offset}
					transform="rotate(-90)"
				/>
				<text x="0" y="4" textAnchor="middle" fontSize={size * 0.22} fontWeight={700} fill="currentColor">
					{Math.round(percent)}%
				</text>
			</g>
		</svg>
	)
}

export default function ScorePage() {

	const [scoreReady, setScoreReady] = useState(false);
	const [count, setCount] = useState(0);
	const [score, setScore] = useState<{ total_score: number; percent_score: number }>({ total_score: 0, percent_score: 0 });

	const params = useSearchParams();
	const id = params.get("id") || "";

	const router = useRouter();

	useEffect(() => {
		if (scoreReady) return;

		// fetch dance readiness
		const apiBase = (process.env.NEXT_PUBLIC_API_URL as string) || "http://localhost:5000";

		fetch(apiBase + '/scoreready/' + id)
			.then(res => res.json())
			.then(data => {
				if (data.ready) {
					fetch(apiBase + '/score/' + id)
						.then(res => res.json())
						.then(data => {
							// set score data
							setScore({
								total_score: Math.floor(data.total_score),
								percent_score: data.percent_score
							})
						})
					setScoreReady(true);
				}
			})

		const timer = setTimeout(() => {
			setCount((c) => c + 1);
		}, 5000);

		return () => clearTimeout(timer);

	}, [count, scoreReady])

	if (!scoreReady) {
		return (
			<div className="min-h-screen flex items-center justify-center p-6">
				<div className="w-full max-w-md bg-gradient-to-br from-gray-900/80 via-gray-900 to-black/60 border border-gray-800 rounded-2xl p-6 shadow-2xl">
					<div className="flex flex-col items-center gap-4">
						<h1 className="text-2xl sm:text-3xl font-bold">Calculating Your Score</h1>
						<p className="text-sm text-gray-400 text-center">This will take a moment while we analyze your performance.</p>
						<div className="mt-4">
							<Loader />
						</div>
					</div>
				</div>
			</div>
		)
	}

	return (
		<div className="min-h-screen flex flex-col items-center justify-center p-6 gap-6">
			<h1 className="text-3xl sm:text-4xl font-bold">Your Dance Score</h1>

			<div className="w-full max-w-4xl bg-gradient-to-br from-gray-900/80 via-gray-900 to-black/60 border border-gray-800 rounded-2xl p-6 grid gap-6 grid-cols-1 md:grid-cols-3 items-center shadow-2xl hover:scale-[1.01] transition-transform">
				<div className="md:col-span-2">
					<div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
						<div>
							<h2 className="text-sm font-semibold text-gray-300 uppercase tracking-wide">Total Score</h2>
							<p className="text-5xl sm:text-6xl font-extrabold text-white mt-1">{score.total_score}</p>
							<p className="mt-2 text-sm text-gray-400">Based on analyzed moves and accuracy metrics</p>
						</div>
					</div>
				</div>

				<div className="flex items-center justify-center">
					<div className="rounded-2xl p-4 bg-gradient-to-tr from-slate-900/40 to-slate-900/10 border border-gray-700 flex items-center justify-center shadow-lg text-indigo-400">
						<ProgressRing percent={score.percent_score} size={150} stroke={14} />
					</div>
				</div>
			</div>
			<button
				className="px-4 py-2 font-bold bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed text-white rounded-md hover:cursor-pointer"
				onClick={() => router.push("/")}>
				Play Again
			</button>
		</div>
	)
}
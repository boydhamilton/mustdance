"use server"
import { redirect } from "next/navigation";

export default async function loginWithSpotify() {
	const result = await fetch(process.env.BACKEND_SERVER_URL + '/login');

	const data = await result.json();

	if (!result.ok) {
		throw new Error(data.message || 'Failed to login with Spotify');
	}

	redirect(data.url);
}
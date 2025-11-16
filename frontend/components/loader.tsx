"use client"
import { useEffect } from 'react'

export default function Loader() {
	useEffect(() => {
		async function getLoader() {
			const { grid } = await import('ldrs')
			grid.register()
		}
		void getLoader()
	}, [])
	return <l-grid color={"#fff"}></l-grid>
}
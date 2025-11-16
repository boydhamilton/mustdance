import os
from silhouette import generate_silhouette_video

moves = "../backend/moves"
output = "../backend/outlines"

all_moves = os.listdir(moves)

for move in all_moves:
	generate_silhouette_video(
		os.path.join(moves, move),
		os.path.join(output, move)
	)
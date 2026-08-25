import cv2
from pathlib import Path

def run(state):
    try:
        fps = state.config["fps"]
        width = state.config["resolution"]["width"]
        height = state.config["resolution"]["height"]

        # Ensure output directory exists
        Path(state.output_video_path).parent.mkdir(parents=True, exist_ok=True)

        # Use pure software-safe OpenCV VideoWriter backend (mp4v)
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        out = cv2.VideoWriter(
            str(state.output_video_path),
            fourcc,
            fps,
            (width, height)
        )

        if not out.isOpened():
            raise RuntimeError("Failed to open OpenCV VideoWriter with mp4v codec.")

        for frame_path in state.frame_paths:
            frame = cv2.imread(str(frame_path))
            if frame is None:
                continue

            frame = cv2.resize(frame, (width, height))
            out.write(frame)

        out.release()

        state.results["status"] = "success"
        state.results["error"] = ""

    except Exception as e:
        state.results["status"] = "error"
        state.results["error"] = str(e)

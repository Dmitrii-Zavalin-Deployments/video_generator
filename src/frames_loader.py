import zipfile
from pathlib import Path

def run(state):
    zip_path = state.inputs["processed_frames_zip_path"]

    try:
        with zipfile.ZipFile(zip_path, "r") as zf:
            zf.extractall(state.frames_dir)

        for frame in sorted(state.frames_dir.glob("*.png")):
            state.frame_paths.append(frame)

        if not state.frame_paths:
            state.results["status"] = "error"
            state.results["error"] = "No frames found in processed_frames.zip"

    except Exception as e:
        state.results["status"] = "error"
        state.results["error"] = str(e)


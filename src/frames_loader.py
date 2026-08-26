# src/frames_loader.py
import zipfile


def run(state):
    zip_path = state.inputs["processed_frames_zip_path"]

    try:
        with zipfile.ZipFile(zip_path, "r") as zf:
            zf.extractall(state.frames_dir)

        # Search for both .jpg and .png frames recursively to match the compressed output format
        frame_files = list(state.frames_dir.rglob("*.jpg")) + list(state.frames_dir.rglob("*.png"))
        
        for frame in sorted(frame_files):
            state.frame_paths.append(frame)

        if not state.frame_paths:
            state.results["status"] = "error"
            state.results["error"] = "No frames found in processed_frames.zip"

    except Exception as e:
        state.results["status"] = "error"
        state.results["error"] = str(e)

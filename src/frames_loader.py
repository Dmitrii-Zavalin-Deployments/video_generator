# src/frames_loader.py
import logging
import zipfile

logger = logging.getLogger(__name__)


def run(state):
    zip_path = state.inputs["processed_frames_zip_path"]
    logger.info("Starting frames extraction from archive: %s", zip_path)

    try:
        with zipfile.ZipFile(zip_path, "r") as zf:
            zf.extractall(state.frames_dir)
        logger.debug("Successfully extracted archive contents into: %s", state.frames_dir)

        # Search for both .jpg and .png frames recursively to match the compressed output format
        frame_files = list(state.frames_dir.rglob("*.jpg")) + list(state.frames_dir.rglob("*.png"))
        
        for frame in sorted(frame_files):
            state.frame_paths.append(frame)

        logger.info("Discovered %d valid frame file(s).", len(state.frame_paths))

        if not state.frame_paths:
            error_msg = "No frames found in processed_frames.zip"
            logger.warning(error_msg)
            state.results["status"] = "error"
            state.results["error"] = error_msg
        else:
            state.results["status"] = "success"
            state.results["error"] = ""

    except (OSError, ValueError, KeyError, RuntimeError) as e:
        logger.error("Exception encountered while loading frames: %s", e, exc_info=True)
        state.results["status"] = "error"
        state.results["error"] = str(e)

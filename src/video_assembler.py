# src/video_assembler.py
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def _touch_fallback_file(target_path):
    """Safely touch the output file as a fallback safeguard without nesting."""
    try:
        out_file = Path(target_path)
        out_file.parent.mkdir(parents=True, exist_ok=True)
        if not out_file.exists():
            out_file.touch()
            logger.warning("Fallback safeguard: touched empty output file at %s", out_file)
    except OSError as fallback_err:
        logger.warning("Fallback safeguard failed to touch output file: %s", fallback_err)


def run(state):
    logger.info("Starting video assembly pipeline.")
    video_path_str = None

    # Sequential import check for mandatory OpenCV
    try:
        import cv2
    except ImportError as e:
        error_msg = f"Required dependency missing: {e}"
        logger.exception(error_msg)
        state.results["status"] = "error"
        state.results["error"] = error_msg
        return

    # Sequential check for optional PyAV
    has_av = False
    try:
        import av
        has_av = True
    except ImportError:
        logger.warning("PyAV ('av') is not installed. Falling back to OpenCV VideoWriter.")

    # Main operational block (flat try-except, zero nesting)
    try:
        # No-Default Policy: Retrieve 'fps' from config or inputs
        fps = None
        if hasattr(state, "config") and state.config and "fps" in state.config:
            fps = state.config["fps"]
        elif hasattr(state, "inputs") and state.inputs and "fps" in state.inputs:
            fps = state.inputs["fps"]
        
        if fps is None:
            raise ValueError("Required property 'fps' is missing from both config.json and input.json.")
        
        logger.debug("Resolved frame rate (fps): %s", fps)

        # No-Default Policy: Retrieve output video path across inputs and config
        if hasattr(state, "inputs") and state.inputs and "output_video_path" in state.inputs:
            video_path_str = state.inputs["output_video_path"]
        elif hasattr(state, "config") and state.config and "output_video_path" in state.config:
            video_path_str = state.config["output_video_path"]
        elif hasattr(state, "output_video_path") and state.output_video_path:
            video_path_str = str(state.output_video_path)

        if not video_path_str:
            raise ValueError("Required property 'output_video_path' is missing from both input.json and config.json.")

        output_path = Path(video_path_str)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        logger.debug("Output video path resolved to: %s", output_path)

        # Load frames and dynamically capture native resolution from the first valid frame
        processed_frames = []
        native_width, native_height = None, None

        frame_paths = getattr(state, "frame_paths", [])
        if not frame_paths:
            raise ValueError("No frame paths provided in state.")

        logger.info("Processing %d candidate frame path(s)...", len(frame_paths))
        for frame_path in frame_paths:
            frame = cv2.imread(str(frame_path))
            if frame is None:
                logger.warning("Failed to load frame with OpenCV from path: %s", frame_path)
                continue

            if native_width is None or native_height is None:
                native_height, native_width = frame.shape[:2]
                if not hasattr(state, "config") or state.config is None:
                    state.config = {}
                state.config["resolution"] = {"width": native_width, "height": native_height}
                logger.info("Captured native video resolution: %dx%d", native_width, native_height)

            processed_frames.append(frame)

        if not processed_frames or native_width is None or native_height is None:
            raise RuntimeError("No valid frames found to assemble into video.")

        # Encoding via PyAV or OpenCV fallback
        if has_av:
            logger.info("Opening PyAV container for encoding at: %s", output_path)
            container = av.open(str(output_path), mode="w", format="mp4")
            stream = container.add_stream("h264", rate=fps)
            stream.width = native_width
            stream.height = native_height
            stream.pix_fmt = "yuv420p"

            for frame in processed_frames:
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                av_frame = av.VideoFrame.from_ndarray(frame_rgb, format="rgb24")
                for packet in stream.encode(av_frame):
                    container.mux(packet)

            for packet in stream.encode():
                container.mux(packet)

            container.close()
            logger.info("Successfully encoded video via PyAV.")
        else:
            logger.info("Encoding video via OpenCV VideoWriter fallback at: %s", output_path)
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(str(output_path), fourcc, fps, (native_width, native_height))
            if not out.isOpened():
                raise RuntimeError("Failed to open OpenCV VideoWriter for output encoding.")
            
            for frame in processed_frames:
                out.write(frame)
            out.release()
            logger.info("Successfully encoded video via OpenCV fallback.")

        state.results["status"] = "success"
        state.results["error"] = ""

    except (OSError, ValueError, KeyError, RuntimeError) as e:
        logger.exception("Exception encountered during video assembly")
        target_path = video_path_str if video_path_str else getattr(state, "output_video_path", None)
        if target_path:
            _touch_fallback_file(target_path)

        state.results["status"] = "error"
        state.results["error"] = str(e)
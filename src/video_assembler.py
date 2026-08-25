import cv2
import subprocess
from pathlib import Path

def run(state):
    try:
        fps = state.config["fps"]
        width = state.config["resolution"]["width"]
        height = state.config["resolution"]["height"]

        # Ensure output directory exists
        Path(state.output_video_path).parent.mkdir(parents=True, exist_ok=True)

        # FFmpeg command for browser-native H.264 (libx264) with yuv420p pixel format
        cmd = [
            "ffmpeg", "-y",
            "-f", "rawvideo",
            "-vcodec", "rawvideo",
            "-s", f"{width}x{height}",
            "-pix_fmt", "bgr24",
            "-r", str(fps),
            "-i", "-",
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-movflags", "+faststart",
            str(state.output_video_path)
        ]

        # Start FFmpeg subprocess pipe
        process = subprocess.Popen(
            cmd, 
            stdin=subprocess.PIPE, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE
        )

        for frame_path in state.frame_paths:
            frame = cv2.imread(str(frame_path))
            if frame is None:
                continue

            # Resize to target dimensions
            frame = cv2.resize(frame, (width, height))
            
            # Write raw bytes to FFmpeg stdin
            process.stdin.write(frame.tobytes())

        # Close stdin and wait for encoding to finish
        process.stdin.close()
        stderr_output = process.stderr.read()
        process.wait()

        if process.returncode != 0:
            raise RuntimeError(f"FFmpeg encoding failed: {stderr_output.decode('utf-8', errors='ignore')}")

        state.results["status"] = "success"
        state.results["error"] = ""

    except Exception as e:
        state.results["status"] = "error"
        state.results["error"] = str(e)

import cv2

def run(state):
    try:
        fps = state.config["fps"]
        width = state.config["resolution"]["width"]
        height = state.config["resolution"]["height"]
        codec = state.config["codec"]
        bitrate = state.config["bitrate"]

        # Map preferred codecs
        codec_mapping = {
            "libx264": "avc1",
            "mpeg4": "mp4v",
            "mp4v": "mp4v",
            "avc1": "avc1"
        }
        primary_chars = codec_mapping.get(codec, codec if len(codec) == 4 else "avc1")

        # Build a prioritized list of candidates for fallback
        candidates = [primary_chars, "avc1", "mp4v", "XVID", "MJPG"]
        seen = set()
        unique_candidates = [c for c in candidates if not (c in seen or seen.add(c))]

        # Robust initialization loop across candidate codecs
        out = None
        for candidate in unique_candidates:
            try:
                fourcc = cv2.VideoWriter_fourcc(*candidate)
                temp_out = cv2.VideoWriter(
                    str(state.output_video_path),
                    fourcc,
                    fps,
                    (width, height)
                )
                if temp_out.isOpened():
                    out = temp_out
                    break
                else:
                    temp_out.release()
            except Exception:
                continue

        if out is None or not out.isOpened():
            raise RuntimeError("Failed to initialize OpenCV VideoWriter with any available software-safe codec.")

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

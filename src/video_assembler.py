import cv2

def run(state):
    try:
        fps = state.config["fps"]
        width = state.config["resolution"]["width"]
        height = state.config["resolution"]["height"]

        # Prioritize pure software codecs (mp4v) to prevent V4L2 hardware device errors in CI runners
        candidates = ["mp4v", "avc1", "XVID", "MJPG"]
        out = None

        for candidate in candidates:
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
            raise RuntimeError("Failed to initialize OpenCV VideoWriter with any available software codec.")

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

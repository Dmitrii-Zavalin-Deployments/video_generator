import cv2

def run(state):
    try:
        fps = state.config["fps"]
        width = state.config["resolution"]["width"]
        height = state.config["resolution"]["height"]
        codec = state.config["codec"]
        bitrate = state.config["bitrate"]

        # Map long codec names or ensure a valid 4-character code for OpenCV
        codec_mapping = {
            "libx264": "mp4v",
            "mpeg4": "mp4v",
            "mp4v": "mp4v",
            "avc1": "avc1"
        }
        fourcc_chars = codec_mapping.get(codec, codec if len(codec) == 4 else "mp4v")
        fourcc = cv2.VideoWriter_fourcc(*fourcc_chars)

        out = cv2.VideoWriter(
            str(state.output_video_path),
            fourcc,
            fps,
            (width, height)
        )

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

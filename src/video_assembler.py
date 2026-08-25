import cv2

def run(state):
    try:
        fps = state.config["fps"]
        width = state.config["resolution"]["width"]
        height = state.config["resolution"]["height"]
        codec = state.config["codec"]
        bitrate = state.config["bitrate"]

        # Map codecs to 'avc1' (H.264) for browser and HTML5 video compatibility
        codec_mapping = {
            "libx264": "avc1",
            "mpeg4": "avc1",
            "mp4v": "avc1",
            "avc1": "avc1"
        }
        fourcc_chars = codec_mapping.get(codec, codec if len(codec) == 4 else "avc1")
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

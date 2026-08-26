import json
import zipfile
import cv2
import numpy as np
import pytest


@pytest.fixture
def test_pipeline_dir(tmp_path):
    """Generates synthetic frames, packages a zip archive, and constructs a valid input.json."""
    data_dir = tmp_path / "testing-input-output"
    data_dir.mkdir(parents=True, exist_ok=True)

    # Generate synthetic image frames
    frame_dir = tmp_path / "raw_frames"
    frame_dir.mkdir()

    img1 = np.zeros((100, 100, 3), dtype=np.uint8)
    img1[:, :] = [255, 0, 0]  # Red frame
    img2 = np.zeros((100, 100, 3), dtype=np.uint8)
    img2[:, :] = [0, 255, 0]  # Green frame

    cv2.imwrite(str(frame_dir / "frame_001.jpg"), img1)
    cv2.imwrite(str(frame_dir / "frame_002.jpg"), img2)

    # Compress frames into test zip file
    zip_path = data_dir / "processed_frames.zip"
    with zipfile.ZipFile(zip_path, "w") as zf:
        zf.write(frame_dir / "frame_001.jpg", arcname="frame_001.jpg")
        zf.write(frame_dir / "frame_002.jpg", arcname="frame_002.jpg")

    # Write input payload
    output_video_path = data_dir / "output_video.mp4"
    input_data = {
        "processed_frames_zip_path": str(zip_path),
        "output_video_path": str(output_video_path),
        "fps": 30,
    }

    input_json_path = data_dir / "input.json"
    with open(input_json_path, "w") as f:
        json.dump(input_data, f, indent=2)

    return data_dir

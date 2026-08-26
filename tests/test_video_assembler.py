# tests/test_video_assembler.py
from pathlib import Path

import cv2
import numpy as np

from video_assembler import run


class DummyState:
    """Lightweight state mock for testing video assembler edge cases."""
    def __init__(self, inputs=None, config=None, frame_paths=None, output_video_path=None):
        self.inputs = inputs or {}
        self.config = config or {}
        self.frame_paths = frame_paths or []
        self.output_video_path = output_video_path
        self.results = {}


def test_video_assembler_success_inputs_fps_and_config_path(tmp_path):
    """Test successful video assembly when fps is in inputs and output_video_path is in config."""
    img_path = tmp_path / "frame_001.jpg"
    img = np.zeros((120, 160, 3), dtype=np.uint8)
    cv2.imwrite(str(img_path), img)

    out_video = tmp_path / "output_config.mp4"
    state = DummyState(
        inputs={"fps": 24},  # fps in inputs (covers lines 18-19)
        config={"output_video_path": str(out_video)},  # path in config (covers lines 30-31)
        frame_paths=[img_path],
        output_video_path=str(out_video)
    )

    run(state)

    assert state.results["status"] == "success"
    assert out_video.exists()
    assert out_video.stat().st_size > 0


def test_video_assembler_success_state_attribute_path(tmp_path):
    """Test successful video assembly when output_video_path is set via state attribute (covers lines 32-33)."""
    img_path = tmp_path / "frame_001.jpg"
    img = np.zeros((120, 160, 3), dtype=np.uint8)
    cv2.imwrite(str(img_path), img)

    out_video = tmp_path / "output_attr.mp4"
    state = DummyState(
        inputs={"fps": 30},
        config={},
        frame_paths=[img_path],
        output_video_path=out_video  # path in state attribute
    )

    run(state)

    assert state.results["status"] == "success"
    assert out_video.exists()


def test_video_assembler_missing_fps(tmp_path):
    """Test ValueError when 'fps' is missing from both config and inputs (covers line 22)."""
    out_video = tmp_path / "out.mp4"
    state = DummyState(
        inputs={"output_video_path": str(out_video)},
        config={},
        frame_paths=[]
    )
    run(state)

    assert state.results["status"] == "error"
    assert "fps" in state.results["error"]


def test_video_assembler_missing_output_video_path(tmp_path):
    """Test ValueError when 'output_video_path' is missing everywhere (covers line 36)."""
    state = DummyState(
        inputs={"fps": 30},
        config={},
        frame_paths=[]
    )
    state.output_video_path = None
    run(state)

    assert state.results["status"] == "error"
    assert "output_video_path" in state.results["error"]


def test_video_assembler_no_frame_paths(tmp_path):
    """Test ValueError when frame_paths list is empty (covers line 48)."""
    out_video = tmp_path / "out.mp4"
    state = DummyState(
        inputs={"fps": 30, "output_video_path": str(out_video)},
        config={},
        frame_paths=[]
    )
    run(state)

    assert state.results["status"] == "error"
    assert "No frame paths provided" in state.results["error"]


def test_video_assembler_invalid_frames_and_no_valid_frames(tmp_path):
    """Test handling of unreadable frames (lines 54-55) and RuntimeError when no valid frames remain (line 67)."""
    bad_frame = tmp_path / "corrupt.jpg"
    bad_frame.write_text("not an image binary")

    out_video = tmp_path / "out.mp4"
    state = DummyState(
        inputs={"fps": 30, "output_video_path": str(out_video)},
        config={},
        frame_paths=[bad_frame]
    )
    run(state)

    assert state.results["status"] == "error"
    assert "No valid frames found" in state.results["error"]


def test_video_assembler_fallback_safeguard_oserror(tmp_path, monkeypatch):
    """Test exception handling in fallback safeguard when file touch/mkdir raises an OSError (covers lines 106-107)."""
    out_video = tmp_path / "out.mp4"
    state = DummyState(
        inputs={"fps": 30, "output_video_path": str(out_video)},
        config={},
        frame_paths=[]  # Triggers initial ValueError
    )

    # Force Path.touch to raise OSError during fallback execution
    def mock_touch(self, *args, **kwargs):
        raise OSError("Simulated disk error during fallback touch")

    monkeypatch.setattr(Path, "touch", mock_touch)

    run(state)

    assert state.results["status"] == "error"
    assert "No frame paths provided" in state.results["error"]

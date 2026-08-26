# tests/test_frames_loader.py
import zipfile

from frames_loader import run


class DummyState:
    """Lightweight state mock matching the interface required by frames_loader.run()."""
    def __init__(self, zip_path, base_dir):
        self.inputs = {"processed_frames_zip_path": zip_path}
        self.frames_dir = base_dir / "frames"
        self.frames_dir.mkdir(parents=True, exist_ok=True)
        self.results = {}
        self.frame_paths = []


def test_frames_loader_success(tmp_path):
    """Test successful extraction and discovery of valid image frames."""
    zip_path = tmp_path / "processed_frames.zip"
    frames_dir = tmp_path / "work_frames"
    
    # Create a valid zip archive containing a mock .jpg frame
    with zipfile.ZipFile(zip_path, "w") as zf:
        zf.writestr("frame_0001.jpg", b"\xff\xd8\xff\xe0\x00\x10JFIF")

    state = DummyState(zip_path, frames_dir)
    run(state)

    assert state.results["status"] == "success"
    assert state.results["error"] == ""
    assert len(state.frame_paths) == 1
    assert state.frame_paths[0].name == "frame_0001.jpg"


def test_frames_loader_no_frames(tmp_path):
    """Test the condition where the archive contains no valid image frames (covers lines 26-29)."""
    zip_path = tmp_path / "processed_frames.zip"
    frames_dir = tmp_path / "work_frames"
    
    # Create a zip archive containing only a text file (no .jpg or .png)
    with zipfile.ZipFile(zip_path, "w") as zf:
        zf.writestr("notes.txt", b"not an image")

    state = DummyState(zip_path, frames_dir)
    run(state)

    assert state.results["status"] == "error"
    assert state.results["error"] == "No frames found in processed_frames.zip"
    assert len(state.frame_paths) == 0


def test_frames_loader_exception(tmp_path):
    """Test exception handling when the archive path does not exist or is corrupted (covers lines 34-37)."""
    non_existent_zip = tmp_path / "non_existent.zip"
    frames_dir = tmp_path / "work_frames"

    state = DummyState(non_existent_zip, frames_dir)
    run(state)

    assert state.results["status"] == "error"
    assert len(state.results["error"]) > 0

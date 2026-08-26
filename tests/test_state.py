# tests/test_state.py
from pathlib import Path

import pytest

from state import State


def test_state_initialization_and_success(tmp_path):
    """Test State initialization, to_output_json conversion, and successful JSON writing."""
    input_data = {"output_video_path": str(tmp_path / "out.mp4")}
    config_data = {"fps": 30}
    base_dir = tmp_path / "io"

    state = State(input_data, config_data, base_dir)

    # Verify attributes and directory creation
    assert state.inputs == input_data
    assert state.config == config_data
    assert state.results["status"] == "pending"
    assert state.frames_dir.exists(), "Frames directory was not created."
    assert state.output_video_path == Path(input_data["output_video_path"])

    # Test to_output_json dictionary structure
    output_dict = state.to_output_json()
    assert output_dict["inputs"] == input_data
    assert output_dict["config"] == config_data
    assert "date_time" in output_dict["results"]

    # Test successful write_output_json
    output_json_path = tmp_path / "output.json"
    state.write_output_json(output_json_path)
    assert output_json_path.exists(), "State output JSON file was not written."


def test_state_write_output_json_exception(tmp_path):
    """Test exception handling and re-raising when write_output_json fails (covers lines 49-51)."""
    input_data = {"output_video_path": str(tmp_path / "out.mp4")}
    config_data = {"fps": 30}
    base_dir = tmp_path / "io"

    state = State(input_data, config_data, base_dir)

    # Passing a directory path as the output file target causes open() to raise an OSError (IsADirectoryError)
    with pytest.raises(OSError):
        state.write_output_json(tmp_path)

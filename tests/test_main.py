# tests/test_main.py
import json
import sys
from pathlib import Path
import pytest

from main import main


def test_main_json_load_failure(tmp_path, monkeypatch):
    """Test exception handling when input JSON file cannot be loaded (covers lines 54-56)."""
    input_output_folder = tmp_path / "io"
    input_output_folder.mkdir()
    
    test_args = [
        "src/main.py",
        "--input_output_folder",
        str(input_output_folder),
        "--input_file_name",
        "non_existent_input.json",
        "--output_file_name",
        "output.json",
    ]
    monkeypatch.setattr(sys, "argv", test_args)

    with pytest.raises((OSError, FileNotFoundError)):
        main()


def test_main_schema_validation_failure(tmp_path, monkeypatch):
    """Test handling when input payload violates schema validation rules (covers lines 63-77)."""
    input_output_folder = tmp_path / "io"
    input_output_folder.mkdir()
    
    input_file = input_output_folder / "invalid_input.json"
    # Write a payload missing required fields to trigger a ValidationError
    input_file.write_text(json.dumps({"malformed_key": "value"}))

    test_args = [
        "src/main.py",
        "--input_output_folder",
        str(input_output_folder),
        "--input_file_name",
        "invalid_input.json",
        "--output_file_name",
        "output.json",
    ]
    monkeypatch.setattr(sys, "argv", test_args)

    # Execution should catch ValidationError, write error JSON state, and return gracefully
    main()

    output_json_path = input_output_folder / "output.json"
    assert output_json_path.exists(), "Error state JSON file was not written."

    with open(output_json_path, "r") as f:
        data = json.load(f)

    assert data.get("results", {}).get("status") == "error"
    assert len(data.get("results", {}).get("error", "")) > 0


def test_main_frames_loader_error_halt(tmp_path, monkeypatch):
    """Test pipeline halt and output generation when frames_loader reports an error status (covers lines 84-86)."""
    input_output_folder = tmp_path / "io"
    input_output_folder.mkdir()

    # Create a valid input payload that passes schema validation
    valid_input = {
        "processed_frames_zip_path": str(tmp_path / "dummy.zip"),
        "output_video_path": str(tmp_path / "output.mp4"),
        "fps": 30
    }
    input_file = input_output_folder / "valid_input.json"
    input_file.write_text(json.dumps(valid_input))

    test_args = [
        "src/main.py",
        "--input_output_folder",
        str(input_output_folder),
        "--input_file_name",
        "valid_input.json",
        "--output_file_name",
        "output.json",
    ]
    monkeypatch.setattr(sys, "argv", test_args)

    # Mock frames_loader.run to simulate an extraction error
    def mock_frames_loader_run(state):
        state.results["status"] = "error"
        state.results["error"] = "Simulated frames extraction failure"

    monkeypatch.setattr("frames_loader.run", mock_frames_loader_run)

    main()

    output_json_path = input_output_folder / "output.json"
    assert output_json_path.exists(), "Halted state JSON file was not written."

    with open(output_json_path, "r") as f:
        data = json.load(f)

    assert data.get("results", {}).get("status") == "error"
    assert data.get("results", {}).get("error") == "Simulated frames extraction failure"

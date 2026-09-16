# tests/test_main_coverage.py
"""
Literate Test Suite: Video Generator Orchestrator Pipeline
==========================================================
Narrative verification ensuring absolute 100% test coverage across the main
pipeline orchestrator, testing dynamic path injections, import fallbacks, file loader
exceptions, schema validations, step error halts, and successful execution paths.
"""

import importlib
import json
import logging
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

import src.main
from src.main import load_json, main


def test_sys_path_insertion_and_import_fallback():
    """
    Narrative: When the source directory is temporarily removed from sys.path,
    reloading the module exercises the dynamic path insertion guard and import fallback branches.
    """
    src_dir_str = str(Path(src.main.__file__).resolve().parent)
    original_path = list(sys.path)

    try:
        while src_dir_str in sys.path:
            sys.path.remove(src_dir_str)
        importlib.reload(src.main)
        assert src_dir_str in sys.path
    finally:
        sys.path[:] = original_path
        importlib.reload(src.main)


def test_load_json_success_and_debug(tmp_path, caplog):
    """
    Narrative: Invoking load_json on a valid file path reads the structured payload
    correctly while emitting the expected debug log entry.
    """
    caplog.set_level(logging.DEBUG, logger="src.main")
    sample_file = tmp_path / "config.json"
    sample_file.write_text('{"fps": 24}', encoding="utf-8")

    data = load_json(sample_file)
    assert data == {"fps": 24}
    assert any("Loading JSON file from" in record.message for record in caplog.records)


def test_main_file_loading_exception_rerise(tmp_path, monkeypatch):
    """
    Narrative: When a required pipeline input or configuration file cannot be found or decoded,
    the outer try-except block logs the exception and re-raises it (covering lines 68-70).
    """
    input_folder = tmp_path / "run_folder"
    input_folder.mkdir()

    test_args = [
        "main.py",
        "--input_output_folder", str(input_folder),
        "--input_file_name", "non_existent.json",
        "--output_file_name", "output.json"
    ]

    with patch.object(sys, "argv", test_args), pytest.raises(FileNotFoundError):
        main()


def test_main_schema_validation_error(tmp_path, monkeypatch):
    """
    Narrative: When input data fails schema validation, a ValidationError is caught,
    an error state dictionary is persisted to the output JSON path, and execution returns early.
    """
    input_folder = tmp_path / "run_folder"
    input_folder.mkdir(parents=True, exist_ok=True)

    # Write an invalid input payload missing required schema properties
    input_file = input_folder / "input.json"
    input_file.write_text(json.dumps({"invalid_field": 123}), encoding="utf-8")

    test_args = [
        "main.py",
        "--input_output_folder", str(input_folder),
        "--input_file_name", "input.json",
        "--output_file_name", "output.json"
    ]

    with patch.object(sys, "argv", test_args):
        main()

    output_path = input_folder / "output.json"
    assert output_path.exists()
    output_data = json.loads(output_path.read_text(encoding="utf-8"))
    assert output_data["results"]["status"] == "error"
    assert "is a required property" in output_data["results"]["error"]


def _setup_valid_run_environment(tmp_path):
    """Helper fixture to generate valid mock input parameters and files for pipeline execution."""
    input_folder = tmp_path / "run_folder"
    input_folder.mkdir(parents=True, exist_ok=True)

    input_file = input_folder / "input.json"
    input_file.write_text(json.dumps({
        "processed_frames_zip_path": str(tmp_path / "dummy.zip"),
        "output_video_path": str(tmp_path / "output.mp4")
    }), encoding="utf-8")

    return input_folder


def test_main_frames_loader_error_halt(tmp_path, monkeypatch):
    """
    Narrative: If the frames_loader execution step flags an error status, the orchestrator
    logs the failure, writes out the error state json, and halts pipeline execution.
    """
    input_folder = _setup_valid_run_environment(tmp_path)

    monkeypatch.setattr(
        src.main.frames_loader,
        "run",
        lambda state: state.results.update({"status": "error", "error": "Extraction failed"})
    )

    test_args = [
        "main.py",
        "--input_output_folder", str(input_folder),
        "--input_file_name", "input.json",
        "--output_file_name", "output.json"
    ]

    with patch.object(sys, "argv", test_args):
        main()

    output_path = input_folder / "output.json"
    assert output_path.exists()
    output_data = json.loads(output_path.read_text(encoding="utf-8"))
    assert output_data["results"]["status"] == "error"
    assert output_data["results"]["error"] == "Extraction failed"


def test_main_successful_pipeline_execution(tmp_path, monkeypatch):
    """
    Narrative: When all modules execute successfully without errors, the orchestrator
    runs through frames_loader and video_assembler, writing a successful status output JSON.
    """
    input_folder = _setup_valid_run_environment(tmp_path)

    monkeypatch.setattr(
        src.main.frames_loader,
        "run",
        lambda state: state.results.update({"status": "success", "error": ""})
    )
    monkeypatch.setattr(
        src.main.video_assembler,
        "run",
        lambda state: state.results.update({"status": "success", "error": ""})
    )

    test_args = [
        "main.py",
        "--input_output_folder", str(input_folder),
        "--input_file_name", "input.json",
        "--output_file_name", "output.json"
    ]

    with patch.object(sys, "argv", test_args):
        main()

    output_path = input_folder / "output.json"
    assert output_path.exists()
    output_data = json.loads(output_path.read_text(encoding="utf-8"))
    assert output_data["results"]["status"] == "success"
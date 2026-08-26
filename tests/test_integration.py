import json
import subprocess
import sys
from pathlib import Path


def test_pipeline_end_to_end(test_pipeline_dir):
    """Executes main.py CLI without mocking and validates state outcome and video rendering."""
    repo_root = Path(__file__).resolve().parent.parent
    main_py = repo_root / "src" / "main.py"
    input_file_name = "input.json"
    output_file_name = "output.json"
    log_file_path = "/tmp/memory_profile.log"

    cmd = [
        sys.executable,
        str(main_py),
        "--input_output_folder",
        str(test_pipeline_dir),
        "--input_file_name",
        input_file_name,
        "--output_file_name",
        output_file_name,
    ]

    # Execute pipeline redirecting stderr to /tmp/memory_profile.log
    with open(log_file_path, "w") as log_file:
        result = subprocess.run(
            cmd,
            cwd=str(repo_root),
            stderr=log_file,
            stdout=subprocess.PIPE,
            text=True,
            check=False,
        )

    assert result.returncode == 0, f"Execution failed with code {result.returncode}. STDOUT: {result.stdout}"

    # Verify output JSON payload
    output_json_path = test_pipeline_dir / output_file_name
    assert output_json_path.exists(), "output.json was not created."

    with open(output_json_path) as f:
        output_data = json.load(f)

    assert output_data.get("results", {}).get("status") == "success"
    assert output_data.get("results", {}).get("error") == ""

    # Verify generated video artifact
    video_path = Path(output_data["inputs"]["output_video_path"])
    assert video_path.exists(), "Output MP4 file was not written."
    assert video_path.stat().st_size > 0, "Generated video file is empty."

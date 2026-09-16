# src/main.py
import argparse
import json
import logging
from pathlib import Path
import sys

from jsonschema import ValidationError, validate

# Ensure module directory is in sys.path for standalone script execution
src_dir = Path(__file__).resolve().parent
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

try:
    from . import frames_loader, video_assembler
    from .state import State
except ImportError:
    import frames_loader
    import video_assembler
    from state import State

logger = logging.getLogger(__name__)

# Root directory anchor
PROJECT_ROOT = src_dir.parent
DEFAULT_CONFIG_PATH = PROJECT_ROOT / "config" / "config.json"
INPUT_SCHEMA_PATH = PROJECT_ROOT / "schema" / "input_schema.json"
CONFIG_SCHEMA_PATH = PROJECT_ROOT / "schema" / "config_schema.json"


def load_json(path: Path) -> dict:
    logger.debug("Loading JSON file from: %s", path)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def main() -> None:
    # Configure root logging for CLI / CI pipeline environments
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        force=True,
    )

    parser = argparse.ArgumentParser(description="Video generator pipeline orchestrator.")
    parser.add_argument("--input_output_folder", required=True, help="Base working directory")
    parser.add_argument("--input_file_name", required=True, help="Input state JSON filename")
    parser.add_argument("--output_file_name", required=True, help="Output state JSON filename")
    args = parser.parse_args()

    logger.info(
        "Starting pipeline run | folder: %s | input: %s | output: %s",
        args.input_output_folder,
        args.input_file_name,
        args.output_file_name,
    )

    base_dir = Path(args.input_output_folder)
    input_json_path = base_dir / args.input_file_name
    output_json_path = base_dir / args.output_file_name

    try:
        input_data = load_json(input_json_path)
        config_data = load_json(DEFAULT_CONFIG_PATH)
        input_schema = load_json(INPUT_SCHEMA_PATH)
        config_schema = load_json(CONFIG_SCHEMA_PATH)
    except (OSError, json.JSONDecodeError):
        logger.exception("Failed to load pipeline input, configuration, or schema files.")
        raise

    logger.info("Validating input data and configuration against schemas...")
    try:
        validate(instance=input_data, schema=input_schema)
        validate(instance=config_data, schema=config_schema)
        logger.info("Schema validation passed successfully.")
    except ValidationError as e:
        logger.error("Schema validation failed: %s", e)
        error_state = {
            "inputs": input_data,
            "config": config_data,
            "results": {
                "status": "error",
                "error": str(e),
            },
        }
        logger.warning("Writing error state payload to output path: %s", output_json_path)
        output_json_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_json_path, "w", encoding="utf-8") as f:
            json.dump(error_state, f, indent=2)
        return

    state = State(input_data, config_data, args.input_output_folder)

    logger.info("Executing module: frames_loader")
    frames_loader.run(state)
    if state.results.get("status") == "error":
        logger.error("Pipeline halted: frames_loader reported error: %s", state.results.get("error"))
        state.write_output_json(output_json_path)
        return

    logger.info("Executing module: video_assembler")
    video_assembler.run(state)

    logger.info("Pipeline execution completed successfully. Writing final output to: %s", output_json_path)
    state.write_output_json(output_json_path)


if __name__ == "__main__":  # pragma: no cover
    main()
# src/main.py
import argparse
import json
import logging
from pathlib import Path

from jsonschema import ValidationError, validate

import frames_loader
import video_assembler
from state import State

logger = logging.getLogger(__name__)


def load_json(path):
    logger.debug("Loading JSON file from: %s", path)
    with open(path) as f:
        return json.load(f)

def load_schema(path):
    logger.debug("Loading schema file from: %s", path)
    with open(path) as f:
        return json.load(f)

def main():
    # Configure root logging for clean output in GitHub Actions / CLI executions
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )

    parser = argparse.ArgumentParser(description="Video generator pipeline orchestrator.")
    parser.add_argument("--input_output_folder", required=True)
    parser.add_argument("--input_file_name", required=True)
    parser.add_argument("--output_file_name", required=True)
    args = parser.parse_args()

    logger.info(
        "Starting pipeline run | folder: %s | input: %s | output: %s",
        args.input_output_folder, args.input_file_name, args.output_file_name
    )

    base = Path(args.input_output_folder)

    input_json_path = base / args.input_file_name
    config_json_path = Path("config/config.json")
    output_json_path = base / args.output_file_name

    try:
        input_data = load_json(input_json_path)
        config_data = load_json(config_json_path)
    except (OSError, json.JSONDecodeError) as e:
        logger.error("Failed to load input or configuration JSON files: %s", e, exc_info=True)
        raise

    logger.info("Validating input data and configuration against schemas...")
    try:
        validate(input_data, load_schema("schema/input_schema.json"))
        validate(config_data, load_schema("schema/config_schema.json"))
        logger.info("Schema validation passed successfully.")
    except ValidationError as e:
        logger.error("Schema validation failed: %s", e)
        error_state = {
            "inputs": input_data,
            "config": config_data,
            "results": {
                "status": "error",
                "error": str(e)
            }
        }
        logger.warning("Writing error state payload to output path: %s", output_json_path)
        output_json_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_json_path, "w") as f:
            json.dump(error_state, f, indent=2)
        return

    state = State(input_data, config_data, args.input_output_folder)

    logger.info("Executing module: frames_loader")
    frames_loader.run(state)
    if state.results["status"] == "error":
        logger.error("Pipeline halted: frames_loader reported error: %s", state.results.get("error"))
        state.write_output_json(output_json_path)
        return

    logger.info("Executing module: video_assembler")
    video_assembler.run(state)
    
    logger.info("Pipeline execution completed successfully. Writing final output to: %s", output_json_path)
    state.write_output_json(output_json_path)

if __name__ == "__main__":
    main()

# src/state.py
import json
import logging
from datetime import datetime, timezone
from pathlib import Path

logger = logging.getLogger(__name__)


class State:
    def __init__(self, input_data, config_data, input_output_folder):
        logger.debug("Initializing State instance.")
        self.inputs = input_data
        self.config = config_data

        self.results = {
            "status": "pending",
            "error": "",
            "date_time": datetime.now(timezone.utc).isoformat()
        }

        self.base_dir = Path(input_output_folder)
        self.frames_dir = self.base_dir / "frames"
        self.frames_dir.mkdir(exist_ok=True)
        logger.debug("Frames directory verified/created at: %s", self.frames_dir)

        self.frame_paths = []
        self.output_video_path = Path(self.inputs["output_video_path"])
        logger.debug("Output video path set to: %s", self.output_video_path)

    def to_output_json(self):
        # Refresh date_time to reflect the precise moment output json is compiled/written
        self.results["date_time"] = datetime.now(timezone.utc).isoformat()
        logger.debug("Compiled output JSON structure. Current status: %s", self.results.get("status"))
        return {
            "inputs": self.inputs,
            "config": self.config,
            "results": self.results
        }

    def write_output_json(self, output_path):
        logger.info("Writing final output JSON state to path: %s", output_path)
        try:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "w") as f:
                json.dump(self.to_output_json(), f, indent=2)
            logger.info("Successfully wrote output JSON payload.")
        except (OSError, TypeError, ValueError) as e:
            logger.error("Failed to write output JSON to %s: %s", output_path, e, exc_info=True)
            raise

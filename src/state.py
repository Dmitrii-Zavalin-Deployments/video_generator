from pathlib import Path
import json

class State:
    def __init__(self, input_data, config_data, input_output_folder):
        self.inputs = input_data
        self.config = config_data

        self.results = {
            "status": "pending",
            "error": ""
        }

        self.base_dir = Path(input_output_folder)
        self.frames_dir = self.base_dir / "frames"
        self.frames_dir.mkdir(exist_ok=True)

        self.frame_paths = []
        self.output_video_path = Path(self.inputs["output_video_path"])

    def to_output_json(self):
        return {
            "inputs": self.inputs,
            "config": self.config,
            "results": self.results
        }

    def write_output_json(self, output_path):
        with open(output_path, "w") as f:
            json.dump(self.to_output_json(), f, indent=2)


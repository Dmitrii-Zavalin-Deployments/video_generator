import json
import unittest

class TestOutputValidation(unittest.TestCase):
    def setUp(self):
        """Load output JSON"""
        with open("data/testing-input-output/simulation_video_metadata.json") as f:
            self.output_data = json.load(f)

    def test_video_properties(self):
        """Ensure video file contains correct metadata"""
        assert self.output_data["video_length"] == "10 min", "Incorrect video length!"
        assert self.output_data["resolution"] == "1080p", "Wrong resolution!"
        assert self.output_data["frame_rate"] == 30, "Incorrect frame rate!"

if __name__ == "__main__":
    unittest.main()




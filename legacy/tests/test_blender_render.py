import os
import unittest

class TestBlenderRendering(unittest.TestCase):
    def test_blender_execution(self):
        """Ensure Blender renders video using headless mode"""
        exit_code = os.system("blender -b -P generate_video.py")
        assert exit_code == 0, "Blender failed to render!"

    def test_video_file_generated(self):
        """Ensure the final video file is created"""
        assert os.path.exists("data/testing-input-output/simulation_final_video.mp4"), "Video file not found!"

if __name__ == "__main__":
    unittest.main()




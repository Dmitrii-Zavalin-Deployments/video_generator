import cv2
import unittest
import numpy as np

class TestFluidFlowInVideo(unittest.TestCase):
    def setUp(self):
        """Load video file"""
        self.video = cv2.VideoCapture("data/testing-input-output/simulation_final_video.mp4")

    def test_water_flow_parallel_to_turbine(self):
        """Use optical flow tracking to verify fluid motion direction"""
        success, prev_frame = self.video.read()
        while success:
            success, next_frame = self.video.read()
            prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
            next_gray = cv2.cvtColor(next_frame, cv2.COLOR_BGR2GRAY)

            flow = cv2.calcOpticalFlowFarneback(prev_gray, next_gray, None, 0.5, 3, 15, 3, 5, 1.2, 0)
            avg_flow_direction = np.mean(flow[..., 1])  # Tracking Y-axis flow
            
            assert abs(avg_flow_direction) < 0.1, "Water flow deviates from turbine axis!"
            prev_frame = next_frame

if __name__ == "__main__":
    unittest.main()




import cv2
import unittest
from skimage.metrics import structural_similarity as ssim

class TestVideoComparison(unittest.TestCase):
    def test_video_similarity_to_ground_truth(self):
        """Compare generated fluid simulation video against reference video"""
        generated_video = cv2.VideoCapture("data/testing-input-output/simulation_final_video.mp4")
        ground_truth_video = cv2.VideoCapture("data/testing-input-output/ground_truth_video.mp4")

        similarity_scores = []
        success, gen_frame = generated_video.read()
        success, gt_frame = ground_truth_video.read()

        while success:
            gen_gray = cv2.cvtColor(gen_frame, cv2.COLOR_BGR2GRAY)
            gt_gray = cv2.cvtColor(gt_frame, cv2.COLOR_BGR2GRAY)

            similarity_score = ssim(gen_gray, gt_gray)
            similarity_scores.append(similarity_score)

            success, gen_frame = generated_video.read()
            success, gt_frame = ground_truth_video.read()

        avg_similarity = np.mean(similarity_scores)
        assert avg_similarity > 0.85, "Generated video deviates significantly from expected behavior!"

if __name__ == "__main__":
    unittest.main()




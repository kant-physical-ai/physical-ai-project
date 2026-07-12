import numpy as np
import pytest
from week3.transform import rotation_matrix_2d, scale_matrix_2d, translate_2d


class TestRotationMatrix2d:

    def test_0도_항등행렬(self):
        R = rotation_matrix_2d(0)
        print(f"---------->{R}<----------\n{R.shape}")
        # 2×2 단위행렬(항등행렬)을 만듭니다. 대각선이 1, 나머지 0.
        """
            np.eye(2)
            # [[1, 0],
            #  [0, 1]]
        """
        expected = np.eye(2)
        np.testing.assert_array_almost_equal(R, expected)

    def test_90도_x축이_y축으로(self):
        R = rotation_matrix_2d(90)
        result = R @ np.array([1, 0])
        expected = np.array([0, 1])
        np.testing.assert_array_almost_equal(result, expected)

    def test_180도_반전(self):
        R = rotation_matrix_2d(180)
        result = R @ np.array([1, 0])
        expected = np.array([-1, 0])
        np.testing.assert_array_almost_equal(result, expected)

    def test_360도_원래대로(self):
        R = rotation_matrix_2d(360)
        result = R @ np.array([1, 0])
        expected = np.array([1, 0])
        np.testing.assert_array_almost_equal(result, expected)

    def test_행렬크기(self):
        R = rotation_matrix_2d(45)
        assert R.shape == (2, 2)

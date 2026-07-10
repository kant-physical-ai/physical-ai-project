# 회전·스케일·이동을 NumPy로 직접 구현합니다. 라이브러리 변환 함수는 쓰지 않습니다.
"""
여기서 만든 변환 함수(rotation_matrix_2d, scale_matrix_2d, translate_2d)와 pixel_to_world는 과제 4의 통합에서 그대로 재사용되므로, 함수 단위로 깔끔하게 만드는 것이 이번 과제의 핵심입니다.
"""
import numpy as np


# 각도(도)를 라디안으로 바꿔 2×2 회전 행렬을 반환합니다
# 확인 방법: rotation_matrix_2d(90)을 [1, 0]에 곱하면 약 [0, 1]이 나오면 완료입니다.
def rotation_matrix_2d(theta_deg):
    theta_rad = theta_deg * np.pi / 180
    return np.array([[np.cos(theta_rad), -np.sin(theta_rad)], [np.sin(theta_rad), np.cos(theta_rad)]])

# 2×2 스케일 행렬을 반환합니다
def scale_matrix_2d(sx, sy):
    return np.array([[sx, 0], [0, sy]])

# 점에 (tx, ty)를 더해 반환합니다
def translate_2d(point, tx, ty):
    return point + np.array([tx, ty])
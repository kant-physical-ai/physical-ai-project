# 회전·스케일·이동을 NumPy로 직접 구현합니다. 라이브러리 변환 함수는 쓰지 않습니다.
"""
여기서 만든 변환 함수(rotation_matrix_2d, scale_matrix_2d, translate_2d)와 pixel_to_world는 과제 4의 통합에서 그대로 재사용되므로, 함수 단위로 깔끔하게 만드는 것이 이번 과제의 핵심입니다.
"""
import numpy as np
from lib import math_libs


# 각도(도)를 라디안으로 바꿔 2×2 회전 행렬을 반환합니다
# 확인 방법: rotation_matrix_2d(90)을 [1, 0]에 곱하면 약 [0, 1]이 나오면 완료입니다.
"""
기준점이 바뀌는 원리
여러분 앞에 십자(+) 모양의 좌표계가 있고, 거기에 점 하나가 있다고 상상해 보세요. 그 점을 90도 돌리고 싶습니다.
원래 가로축(X축)이었던 것은, 90도 돌리면 세로축(Y축)의 위치로 가겠죠?
원래 세로축(Y축)이었던 것은, 90도 돌리면 반대편 가로축(-X축) 위치로 갑니다.
이걸 숫자로 나타내면 X축(1, 0)은 (0, 1)이 되고, Y축(0, 1)은 (-1, 0)이 됩니다.

행렬은 "바뀐 위치를 적어놓은 표"
컴퓨터는 이 바뀐 위치를 기억하기 위해 표를 만듭니다. 그게 바로 회전 행렬입니다.
"""
def rotation_matrix_2d(theta_deg):
    # degrees * (math.pi / 180)
    theta_rad = math_libs.degrees_to_radians(theta_deg)  # 각도를 라디안으로 변환
    """
    첫 번째 열(cos, sin): "원래 가로(1,0)가 어디로 갔나?"를 나타냅니다.
    두 번째 열(-sin, cos): "원래 세로(0,1)가 어디로 갔나?"를 나타냅니다.
    
    왜 하필 cos, sin인가요?
    우리가 90도 같이 딱 떨어지는 각도만 돌리는 게 아니잖아요? 23.5도, 47.8도처럼 애매한 각도를 돌릴 때, 그 위치를 정확히 계산하기 위해 가장 좋은 도구가 삼각함수(cos, sin)이기 때문입니다.
    cos: 가로 방향으로 얼마나 이동했는지
    sin: 세로 방향으로 얼마나 이동했는지
    즉, "내가 이만큼(각도) 돌렸을 때, 원래 좌표가 어디로 밀려나는지 그 비율을 미리 표로 만들어둔 것"이 바로 저 행렬입니다.
    """
    return np.array([
        [np.cos(theta_rad), -np.sin(theta_rad)],
        [np.sin(theta_rad), np.cos(theta_rad)]
    ])


# 2×2 스케일 행렬을 반환합니다
# 스케일 행렬: 점을 크기만큼 키우거나 줄일 때 사용
def scale_matrix_2d(sx, sy):
    return np.array([
        [sx, 0],
        [0, sy]
    ])


# 점에 (tx, ty)를 더해 반환합니다
def translate_2d(point: tuple[float, float], tx: float, ty: float):
    return np.array(point) + np.array([tx, ty])
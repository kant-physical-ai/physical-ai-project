from matplotlib import pyplot as plt
import sys
from collections import deque
import cv2
import numpy as np

from week3.transform import translate_2d, scale_matrix_2d, rotation_matrix_2d
import week2.main as week2
import lib
"""
기능 1의 함수를 조합해 픽셀 좌표를 실세계 좌표로 바꿉니다. 이동 → 스케일 → 회전 순서입니다.
구현 요건:
이미지 중앙이 원점이 되도록 이동합니다 (tx = -W/2, ty = -H/2)
스케일 행렬을 곱해 픽셀 단위를 실세계 단위로 줄입니다
회전 행렬을 곱해 축 방향을 보정합니다
확인 방법: 이미지 중앙 (320, 240) 픽셀이 실세계 (0, 0) 근처로 나오면 완료입니다. (640×480 기준)
예시 (scale=0.01, angle=0): 중앙(320,240)→(0, 0), 우측(500,240)→(1.8, 0), 우하단(640,480)→(3.2, 2.4). 물체를 오른쪽으로 옮기면 world x가 커집니다.
"""
def pixel_to_world(point: tuple[float, float], image_width: int, image_height: int, scale: float, angle: float):
    # 이동: 이미지 중앙이 원점이 되도록 이동
    tx = -image_width / 2
    ty = -image_height / 2
    translated_point = translate_2d(point, tx, ty)

    # 스케일: 픽셀 단위를 실세계 단위로 줄임
    scale_matrix = scale_matrix_2d(scale, scale)
    # @ 행렬곱셈 오퍼레이터
    scaled_point = scale_matrix @ translated_point

    # 회전: 축 방향 보정
    rotation_matrix = rotation_matrix_2d(angle)
    world_point: np.ndarray = rotation_matrix @ scaled_point

    return world_point

"""
기능 4 — matplotlib 실시간 시각화
픽셀 좌표와 실세계 좌표를 산점도로 그려, 변환 결과를 눈으로 확인합니다.
구현 요건:
plt.ion()으로 인터랙티브 모드를 켭니다
좌표 이력을 deque(maxlen=100)에 쌓아 픽셀(파랑)·실세계(빨강)를 산점도로 그립니다
매 프레임이 아니라 몇 프레임에 한 번만 갱신해 부하를 줄입니다 (예: 3프레임마다)
확인 방법: 물체를 움직이면 matplotlib 창에 픽셀·실세계 점이 이력으로 찍히면 완료입니다.
창이 두 개(OpenCV+matplotlib)라 느릴 수 있습니다. 플롯을 몇 프레임에 한 번만 갱신하고 이력을 deque(maxlen=100)로 제한하면 부하가 줄어듭니다.
"""


"""
기능 5 — 키 입력으로 각도·스케일 조절 + main() 연결
회전각과 스케일을 실행 중에 바꿔 변환이 어떻게 달라지는지 확인하고, 전체를 main()에서 연결합니다.
구현 요건:
a/d로 회전각을 ±5°, +/로 스케일을 ×1.1 / ×0.9 조절합니다
현재 각도를 화면에 표시합니다
인식 → 변환 → 화면표시 → 플롯 → 키처리 순서로 루프를 돌리고, q로 종료합니다
확인 방법: python week3/main.py 실행 시 인식·좌표 변환·플롯이 함께 동작하고, 키로 각도/스케일이 바뀌며, q로 종료되면 완료입니다.
"""


"""
2주차 인식으로 얻은 중심 좌표에 변환을 적용하고, 화면·터미널에 픽셀/실세계 좌표를 함께 표시합니다.
구현 요건:
- 2주차 detect()(또는 create_mask+find_objects)로 물체를 인식합니다
- 여러 물체가 있으면 면적이 가장 큰 하나를 대상으로 삼습니다
- 그 중심 (cx, cy)에 pixel_to_world를 적용합니다
- 픽셀·실세계 좌표를 화면(cv2.putText)과 터미널에 출력합니다
확인 방법: 물체를 움직이면 화면·터미널에 픽셀·실세계 좌표가 함께 갱신되면 완료입니다.
"""
def main():
    # main() 밖 또는 main() 안 루프 전에 초기화
    pixel_history = deque(maxlen=100)
    world_history = deque(maxlen=100)
    frame_count = 0
    angle = 0
    scale = 0.01
    plt.ion()  # 인터랙티브 모드
    fig, ax = plt.subplots()

    video_captrue = lib.device_libs.first_video_capture()
    if video_captrue is None:
        print("웹캠을 찾을 수 없습니다. 프로그램을 종료합니다.")
        sys.exit(0)
        return

    frame_datas = lib.device_libs.video_read_iterator(video_captrue)
    for frame_data in frame_datas:
        if frame_data is None:
            print("웹캠에서 더 이상 프레임을 읽어올 수 없습니다. 프로그램을 종료합니다.")
            cv2.destroyAllWindows()
            break
        frame = frame_data.frame
        fps = frame_data.fps

        # frame 좌우 반전 처리
        # frame = cv2.flip(frame, 1)

        detect_draw_frame, mask, objects = week2.detect(frame)

        # draw fps
        cv2.putText(frame, f"FPS: {fps:.2f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)


        world_point = None
        # 가장 면적이 큰 물체를 찾습니다  리스트가 비어있을 경우 에러 방지
        # 리스트가 비어있으면 max() 함수는 ValueError를 발생시킵니다. 이를 방지하려면 default 인자를 사용하세요.
        largest_object = max(objects, key=lambda obj: obj.area, default=None)
        if largest_object is not None:
            frame = week2.draw_detection(frame, [largest_object])
            # draw pixel to world
            world_point: np.ndarray = pixel_to_world((largest_object.cx, largest_object.cy), frame.shape[1], frame.shape[0], scale, angle)
            # draw angle
            cv2.putText(frame, f"Angle: {angle:.2f}°", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            # draw scale
            cv2.putText(frame, f"Scale: {scale:.2f}", (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            # draw world point
            cv2.putText(frame, f"World: ({world_point[0]:.2f}, {world_point[1]:.2f})", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            print(f"pixel point: ({largest_object.cx}, {largest_object.cy})")
            print(f"world point: ({world_point[0]:.2f}, {world_point[1]:.2f})")

        cv2.imshow("Webcam", frame)
        cv2.imwrite('result.png', frame)


        if world_point is not None and largest_object is not None :
            pixel_history.append((largest_object.cx, largest_object.cy))
            world_history.append((world_point[0], world_point[1]))
            frame_count += 1
            # matplotlib window matplotlib으로 좌표 시각화 (몇 프레임마다 갱신)
            if frame_count % 3 == 0:
                """
                plt.ion()으로 인터랙티브 모드를 켭니다
                좌표 이력을 deque(maxlen=100)에 쌓아 픽셀(파랑)·실세계(빨강)를 산점도로 그립니다
                매 프레임이 아니라 몇 프레임에 한 번만 갱신해 부하를 줄입니다 (예: 3프레임마다)
                확인 방법: 물체를 움직이면 matplotlib 창에 픽셀·실세계 점이 이력으로 찍히면 완료입니다.
                """
                ax.cla()  # 이전 그림 지우기

                # 픽셀 좌표 (파랑)
                px = [p[0] for p in pixel_history]
                py = [p[1] for p in pixel_history]
                ax.scatter(px, py, c='blue', label='pixel', s=10)

                # 실세계 좌표 (빨강)
                wx = [w[0] for w in world_history]
                wy = [w[1] for w in world_history]
                ax.scatter(wx, wy, c='red', label='world', s=10)

                ax.legend()
                ax.set_title(f"frame: {frame_count}")
                # 화면갱신하는데 윈도우 포커싱은 안되게
                plt.pause(0.001)  # 화면 갱신


        # a/d, +/- 로 각도·스케일이 바뀌고 q로 종료된다
        key = cv2.waitKey(1) & 0xFF
        if key == ord('a'):
            angle -= 5
        elif key == ord('d'):
            angle += 5
        elif key == ord('+'):
            scale *= 1.1
        elif key == ord('-'):
            scale /= 1.1
        # q를 누르면(ord('q')와 일치하면) 루프를 종료합니다.
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("사용자 요청으로 프로그램을 종료합니다.")
            sys.exit(0)
if __name__ == "__main__":
    main()
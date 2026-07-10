import sys

import cv2

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
def pixel_to_world(point, image_width, image_height, scale, angle):
    # 이동: 이미지 중앙이 원점이 되도록 이동
    tx = -image_width / 2
    ty = -image_height / 2
    translated_point = translate_2d(point, tx, ty)

    # 스케일: 픽셀 단위를 실세계 단위로 줄임
    scale_matrix = scale_matrix_2d(scale, scale)
    scaled_point = scale_matrix @ translated_point

    # 회전: 축 방향 보정
    rotation_matrix = rotation_matrix_2d(angle)
    world_point = rotation_matrix @ scaled_point

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
2주차 detect()(또는 create_mask+find_objects)로 물체를 인식합니다
여러 물체가 있으면 면적이 가장 큰 하나를 대상으로 삼습니다
그 중심 (cx, cy)에 pixel_to_world를 적용합니다
픽셀·실세계 좌표를 화면(cv2.putText)과 터미널에 출력합니다
확인 방법: 물체를 움직이면 화면·터미널에 픽셀·실세계 좌표가 함께 갱신되면 완료입니다.
"""
def main():
    first_video_device = lib.device.detect_first_video_device()
    if first_video_device is None:
        print("웹캠을 찾을 수 없습니다. 프로그램을 종료합니다.")
        return

    def while_video_read(frameData: lib.device.FrameData):
        frame = frameData.frame
        if not frameData.ret:
            print("프레임을 읽어오는데 실패했습니다.")
            return

        # frame 좌우 반전 처리
        frame = cv2.flip(frame, 1)

        result_frame, mask, objects = week2.detect(frame)
        cv2.putText(result_frame, f"FPS: {frameData.fps:.2f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.imshow("Webcam", result_frame)
        cv2.imwrite('result.png', result_frame)

        # q를 누르면(ord('q')와 일치하면) 루프를 종료합니다.
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("사용자 요청으로 프로그램을 종료합니다.")
            sys.exit(0)
    def while_video_cleanup():
        cv2.destroyAllWindows()
        print("모든 웹캠 리소스가 안전하게 해제되었습니다.")

    lib.device.while_video_read_context(first_video_device, while_video_read, while_video_cleanup)

if __name__ == "__main__":
    main()
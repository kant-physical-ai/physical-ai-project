import sys
from dataclasses import dataclass
from typing import NamedTuple

import cv2
import numpy as np
import lib


class DetectedObject(NamedTuple):
    cx: int
    cy: int
    area: float
    x: int
    y: int
    w: int
    h: int


"""
기능 1 — HSV 변환 및 색 마스킹 (create_mask)
색 기반 필터링은 BGR보다 HSV 색 공간이 안정적입니다. BGR은 조명 변화에 민감하지만, HSV는 색상(H)·채도(S)·명도(V)를 분리해 조명이 조금 바뀌어도 같은 색을 잡을 수 있습니다.
구현 요건:
원본 프레임을 cv2.COLOR_BGR2HSV로 변환합니다
cv2.inRange로 지정한 색만 흰색(255), 나머지는 검정(0)인 마스크를 만듭니다
추적할 색은 코드 상단 상수로 분리해 바꾸기 쉽게 합니다

주요 색상 HSV 범위 참고표
색상|Lower|Upper
빨강|[0, 120, 70]|[10, 255, 255] (+ [170,120,70]~[180,255,255])
파랑|[100, 150, 50]|[130, 255, 255]
초록|[40, 70, 70]|[80, 255, 255]
노랑|[15, 150, 150]|[35, 255, 255]

확인 방법: Mask 창에서 추적 대상만 흰색, 배경은 검정으로 보이면 완료입니다.
빨강은 왜 범위가 둘인가요? HSV에서 빨강은 H가 0~10과 170~180에 걸쳐 있어, 두 범위를 각각 마스킹해 cv2.bitwise_or로 합칩니다. (다른 색은 한 범위면 충분합니다.)
"""


def create_mask(frame: np.ndarray):
    print('============ create_mask')
    # 원본 프레임을 cv2.COLOR_BGR2HSV로 변환합니다
    hsv = cv2.cvtColor(frame.copy(), cv2.COLOR_BGR2HSV)

    # 1. 빨간색 마스크 (0~10, 170~180)
    lower_red1 = np.array([0, 120, 70])
    upper_red1 = np.array([10, 255, 255])
    mask_red1 = cv2.inRange(hsv, lower_red1, upper_red1)

    lower_red2 = np.array([170, 120, 70])
    upper_red2 = np.array([180, 255, 255])
    mask_red2 = cv2.inRange(hsv, lower_red2, upper_red2)

    # 빨간색 영역 합치기
    red_mask = cv2.bitwise_or(mask_red1, mask_red2)

    # 2. 파란색 마스크 (100~130)
    lower_blue = np.array([100, 150, 50])
    upper_blue = np.array([130, 255, 255])
    blue_mask = cv2.inRange(hsv, lower_blue, upper_blue)

    # 3. 최종 마스크: 빨간색 OR 파란색
    final_mask = cv2.bitwise_or(red_mask, blue_mask)

    return final_mask


"""
기능 2 — Contour 검출 및 중심 좌표 (find_objects)
마스크에서 윤곽선을 찾고, 너무 작은 노이즈는 걸러낸 뒤 각 물체의 중심 좌표를 계산합니다.
구현 요건:
cv2.findContours로 윤곽을 검출합니다
면적이 기준값(예: 500px²) 미만이면 노이즈로 보고 건너뜁니다
cv2.boundingRect로 박스를 구하고, 중심을 cx = x + w//2, cy = y + h//2로 계산합니다
(cx, cy, area, (x,y,w,h)) 튜플 리스트로 반환합니다

확인 방법: 물체가 있을 때만 검출되고 배경 노이즈는 걸러지면 완료입니다.
노이즈가 많으면? MIN_AREA를 높이거나, 마스크에 cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((5,5), np.uint8))를 한 줄 적용하면 자잘한 흰 점이 줄어듭니다. (선택)

"""


def find_objects(frame: np.ndarray):
    print('============ find_objects')
    # Find contours in the mask
    contours, _ = cv2.findContours(frame, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    objects: list[DetectedObject] = []
    for contour in contours:
        if cv2.contourArea(contour) > 500:  # Filter small contours
            x, y, w, h = cv2.boundingRect(contour)
            cx = x + w // 2
            cy = y + h // 2
            objects.append(DetectedObject(cx, cy, cv2.contourArea(contour), x, y, w, h))
    return objects


"""
기능 3 — 바운딩 박스·중심 좌표 표시 (draw_detection)
검출한 물체마다 박스를 그리고 중심 좌표를 화면에 표시합니다.
구현 요건:
cv2.rectangle로 초록 박스, cv2.circle로 빨간 중심점을 그립니다
cv2.putText로 중심 좌표 (cx, cy)를 박스 위에 표시합니다
중심 좌표 (cx, cy)는 이미지 좌상단이 원점(0,0)인 픽셀 좌표계 기준입니다. 이 값이 3주차에서 실세계 좌표로 변환할 입력이 되므로, 물체를 움직였을 때 좌표가 자연스럽게 따라 변하는지 확인하세요.
확인 방법: 물체를 움직이면 박스·중심점이 따라다니고 좌표 텍스트가 실시간으로 갱신되면 완료입니다.
"""


def draw_detection(frame: np.ndarray, objects: list[DetectedObject]):
    print('============ draw_detection')
    if len(frame.shape) == 2:  # 채널이 2개(또는 1개)라면 흑백임  따라서 BGR로 바꿔서
        result_frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)
    else:
        result_frame = frame.copy()
    for obj in objects:
        cv2.rectangle(result_frame, (obj.x, obj.y), (obj.x + obj.w, obj.y + obj.h), (0, 255, 0), 2)
        cv2.circle(result_frame, (obj.cx, obj.cy), 5, (0, 0, 255), -1)
        cv2.putText(result_frame, f"({obj.cx}, {obj.cy})", (obj.cx - 10, obj.cy - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                    (0, 0, 255), 2)
    return result_frame


"""
기능 4 — 인식 파이프라인 묶기 (detect) + 수치 출력
기능 1~3을 하나로 묶고, 중심 좌표·면적을 터미널에 출력합니다.
구현 요건:
detect(frame)가 인식을 모두 수행하고 (그린 frame, mask, objects)를 반환합니다
검출된 물체의 중심 좌표·면적을 터미널에 출력합니다 (예: 중심: (340, 250) | 면적: 8000px²)
확인 방법: 물체를 움직일 때 터미널에 좌표·면적이 갱신되며 찍히면 완료입니다.
"""


def detect(frame: np.ndarray):
    print('============ detect')
    # HSV 변환 → 색 마스킹                    ← 신규
    # Contour 검출 + 면적 필터링 + 중심 좌표  ← 신규
    # objects = find_objects(frame)
    # 바운딩 박스 / 중심점 / 좌표 그리기      ← 신규
    # result_frame = draw_detection(frame, objects)
    # 중심 좌표·면적 터미널 출력             ← 신규
    # print(f"중심 좌표: {objects}")

    original_frame = frame.copy()
    mask = create_mask(original_frame)  # 1
    objects = find_objects(mask)  # 2
    result_frame = draw_detection(original_frame, objects)  # 3

    # object print
    for obj in objects:
        print(f"obj: ({obj.cx}, {obj.cy}) | 면적: {obj.area:.2f}px²")

    return result_frame, mask, objects


def combine_frames(frame: np.ndarray, result_frame: np.ndarray):
    print('============ combine_frames')
    combined = np.hstack((frame, result_frame))
    return combined


def draw_fps(frame: np.ndarray, fps: float):
    print('============ draw_fps')
    cv2.putText(frame, f"FPS: {fps:.2f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    return frame


"""
원본(인식 결과)과 마스크를 나란히 출력하고, 과제 1의 루프·FPS 구조에 인식을 얹어 완성합니다.
구현 요건:
왼쪽 원본(박스·중심점·FPS 포함), 오른쪽 마스크를 좌우로 합쳐 창 하나에 출력합니다
마스크는 1채널이므로 cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)로 3채널 변환 후 합칩니다 (과제 1의 edge 합치기와 동일 방식)
FPS는 과제 1과 동일하게 최근 30프레임 평균(deque(maxlen=30))으로 표시합니다
q 입력 시 종료하고 카메라·창을 정리합니다
확인 방법: python week2/main.py 실행 시 원본+마스크가 나란히 나오고, 박스·중심점·FPS가 표시되며 q로 종료되면 완료입니다.
"""


def main():
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

        result_frame, mask, objects = detect(frame)
        combine_frame = np.hstack((result_frame, cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)))
        cv2.putText(combine_frame, f"FPS: {fps:.2f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.imshow("Webcam", combine_frame)
        cv2.imwrite('result.png', combine_frame)

        # q를 누르면(ord('q')와 일치하면) 루프를 종료합니다.
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("사용자 요청으로 프로그램을 종료합니다.")
            sys.exit(0)


if __name__ == '__main__':
    main()

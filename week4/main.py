import sys
import time
from collections import deque

import cv2
import numpy as np
from matplotlib import pyplot as plt

import lib
import week2.main as week2
import week3.main as week3

"""
웹캠 연결 성공
sense: 3.2ms | compute: 5.1ms | act: 8.4ms | FPS: 21.3
sense: 3.1ms | compute: 4.9ms | act: 8.1ms | FPS: 22.0
"""
def main():
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
    else:
        print("웹캠 연결 성공")

    frame_datas = lib.device_libs.video_read_iterator(video_captrue)
    sense_start_time = time.time()
    for frame_data in frame_datas:
        # Sense
        if frame_data is None:
            print("웹캠에서 더 이상 프레임을 읽어올 수 없습니다. 프로그램을 종료합니다.")
            cv2.destroyAllWindows()
            break
        frame = frame_data.frame
        fps = frame_data.fps

        sense_time = time.time() - sense_start_time

        # Compute
        detect_start_time = time.time()
        detect_draw_frame, mask, objects = week2.detect(frame)
        largest_object = max(objects, key=lambda obj: obj.area, default=None)
        compute_time = time.time() - detect_start_time
        if largest_object is not None:
            frame = week2.draw_detection(frame, [largest_object])
            # draw pixel to world
            world_point: np.ndarray = week3.pixel_to_world((largest_object.cx, largest_object.cy), frame.shape[1], frame.shape[0], scale, angle)
            # draw angle
            cv2.putText(frame, f"Angle: {angle:.2f}°", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            # draw scale
            cv2.putText(frame, f"Scale: {scale:.2f}", (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            # draw world point
            cv2.putText(frame, f"World: ({world_point[0]:.2f}, {world_point[1]:.2f})", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            pixel_history.append((largest_object.cx, largest_object.cy))
            world_history.append((world_point[0], world_point[1]))
            frame_count += 1

            # Act
            # matplotlib window matplotlib으로 좌표 시각화 (몇 프레임마다 갱신)
            if frame_count % 3 == 0:
                act_start_time = time.time()
                """
                plt.ion()으로 인터랙티브 모드를 켭니다
                좌표 이력을 deque(maxlen=100)에 쌓아 픽셀(파랑)·실세계(빨강)를 산점도로 그립니다
                매 프레임이 아니라 몇 프레임에 한 번만 갱신해 부하를 줄입니다 (예: 3프레임마다)
                확인 방법: 물체를 움직이면 matplotlib 창에 픽셀·실세계 점이 이력으로 찍히면 완료입니다.
                """
                # 픽셀 좌표 (파랑)
                px = [p[0] for p in pixel_history]
                py = [p[1] for p in pixel_history]

                # 실세계 좌표 (빨강)
                wx = [w[0] for w in world_history]
                wy = [w[1] for w in world_history]
                week3.update_plot(ax, (px, py), (wx, wy), title=f"frame: {frame_count}")
                act_time = time.time() - act_start_time
                print(f"⏰ Sense: {sense_time:.2f}ms | Compute: {compute_time:.2f}ms | Act: {act_time:.2f}ms | FPS: {fps:.2f}")


        # draw fps
        cv2.putText(frame, f"FPS: {fps:.2f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.imshow("Webcam", frame)
        cv2.imwrite('result.png', frame)

        # q를 누르면(ord('q')와 일치하면) 루프를 종료합니다.
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("사용자 요청으로 프로그램을 종료합니다.")
            sys.exit(0)

        sense_start_time = time.time()



if __name__ == "__main__":
    main()
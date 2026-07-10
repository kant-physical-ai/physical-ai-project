import sys

import cv2
import numpy as np
import matplotlib
import time
import lib

def version_check():
    print('============ version_check')
    print(cv2.__version__)        # 예: 4.9.0
    print(np.__version__)         # 예: 1.26.0
    print(matplotlib.__version__) # 예: 3.8.0


# 컬러 영상을 흑백으로 변환
def to_grayscale(frame: np.ndarray):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    return gray

# 노이즈 제거
def apply_blur(frame: np.ndarray):
    print('============ apply_blur')
    blurred = cv2.GaussianBlur(frame, (5, 5), 0)
    return blurred

# 경계선 검출
def detect_edges(frame: np.ndarray):
    print('============ detect_edges')
    # cv2.namedWindow("Edges")
    # cv2.createTrackbar("Low",  "Edges", 100, 500, lambda x: None)
    # cv2.createTrackbar("High", "Edges", 200, 500, lambda x: None)

    # 루프 안에서
    # low  = cv2.getTrackbarPos("Low",  "Edges")
    # high = cv2.getTrackbarPos("High", "Edges")
    # edges = cv2.Canny(frame, low, high)
    edges = cv2.Canny(frame, 50, 150)
    return edges

# FPS 계산
def calculate_fps(prev_time: float, current_time: float):
    print('============ calculate_fps')
    # fps = 1 / (current_time - prev_time)
    # return fps
    return lib.math_libs.calculate_fps(prev_time, current_time)

def draw_fps(frame: np.ndarray, fps: float):
    print('============ draw_fps')
    cv2.putText(frame, f"FPS: {fps:.2f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    return frame


def combine_frames(frame: np.ndarray, edges: np.ndarray):
    print('============ combine_frames')
    return np.hstack((frame, edges))

def preprocess(frame: np.ndarray):
    print('============ preprocess')
    print(f"frame shape: {frame.shape}, dtype: {frame.dtype}")
    gray = to_grayscale(frame)
    blurred = apply_blur(gray)
    edges = detect_edges(blurred)
    # combined = combine_frames(frame, edges)
    return edges


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

        process_frame = preprocess(frame)
        process_frame = cv2.cvtColor(process_frame, cv2.COLOR_GRAY2BGR)
        # 결과 화면 출력 (원본 + 전처리 결과 나란히)
        combine_frame = combine_frames(frame, process_frame)
        full_fps_frame = draw_fps(combine_frame, frameData.fps)

        # full_frame = process_frame
        cv2.imshow("Webcam", full_fps_frame)


        cv2.imwrite('result.png', combine_frame)
        # cv2.waitKey(1)로 1ms 동안 키 입력을 대기합니다.
        # q를 누르면(ord('q')와 일치하면) 루프를 종료합니다.
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("사용자 요청으로 프로그램을 종료합니다.")
            sys.exit(0)
    def while_video_cleanup():
        cv2.destroyAllWindows()
        print("모든 웹캠 리소스가 안전하게 해제되었습니다.")

    lib.device.while_video_read_context(first_video_device, while_video_read, while_video_cleanup)

if __name__ == '__main__':
    main()
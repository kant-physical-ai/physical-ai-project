import cv2
import numpy as np
import matplotlib
import time

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
    fps = 1 / (current_time - prev_time)
    return fps

def draw_fps(frame: np.ndarray, fps: float):
    print('============ draw_fps')
    cv2.putText(frame, f"FPS: {fps}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    return frame


def combine_frames(frame: np.ndarray, edges: np.ndarray):
    print('============ combine_frames')
    combined = np.hstack((frame, edges))
    return combined

def preprocess(frame: np.ndarray):
    print('============ preprocess')
    print(f"frame shape: {frame.shape}, dtype: {frame.dtype}")
    gray = to_grayscale(frame)
    blurred = apply_blur(gray)
    edges = detect_edges(blurred)
    # combined = combine_frames(frame, edges)
    return edges


def main():
    cap: None | cv2.VideoCapture = None  # 발견된 웹캠을 저장할 변수 초기화

    for i in range(5):
        temp_cap = cv2.VideoCapture(i)
        if temp_cap.isOpened():
            print(f"웹캠 발견: index {i}")
            cap = temp_cap  # 발견 시 cap에 할당하고 루프 탈출
            break
        temp_cap.release()  # 열리지 않은 웹캠은 즉시 자원 해제

    # 웹캠을 하나도 찾지 못한 경우 (cap이 여전히 None인 상태)
    if cap is None:
        raise NotImplementedError("웹캠을 찾을 수 없습니다.")

    prev_time = time.perf_counter()
    try:
        # 2. 입력 -> 처리 -> 출력 반복 루프 시작
        while True:
            # cap.read()로 프레임을 읽습니다 (ret: 성공 여부, frame: 이미지 데이터)
            ret, frame = cap.read()
            # ret가 False이면 루프를 종료합니다
            if not ret:
                print("프레임을 읽어오는데 실패했습니다.")
                break

            current_time = time.perf_counter()
            fps = calculate_fps(prev_time, current_time)

            process_frame = preprocess(frame)
            process_frame = cv2.cvtColor(process_frame, cv2.COLOR_GRAY2BGR)
            # 결과 화면 출력 (원본 + 전처리 결과 나란히)
            combine_frame = combine_frames(frame, process_frame)
            full_fps_frame = draw_fps(combine_frame, fps)

            # full_frame = process_frame
            cv2.imshow("Webcam", full_fps_frame)

            prev_time = current_time

            cv2.imwrite('result.png', combine_frame)
            # cv2.waitKey(1)로 1ms 동안 키 입력을 대기합니다.
            # q를 누르면(ord('q')와 일치하면) 루프를 종료합니다.
            if cv2.waitKey(1) & 0xFF == ord('q'):
                print("사용자 요청으로 프로그램을 종료합니다.")
                break

    finally:
        # 3. 루프 종료 후 자원 해제 (예외가 발생하더라도 반드시 실행되도록 보장)
        cap.release()
        cv2.destroyAllWindows()
        print("모든 웹캠 리소스가 안전하게 해제되었습니다.")



    # to_grayscale(cap)
    # apply_blur()
    # detect_edges()
    # preprocess()
    # calculate_fps()
    # draw_fps()
    # combine_frames()

if __name__ == '__main__':
    main()
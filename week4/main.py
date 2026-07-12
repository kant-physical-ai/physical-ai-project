import sys
import cv2
import lib



def main():
    video_captrue = lib.device_libs.first_video_capture()
    if video_captrue is None:
        print("웹캠을 찾을 수 없습니다. 프로그램을 종료합니다.")
        sys.exit(0)
        return
    frame_datas = lib.device_libs.video_read_queue(video_captrue)
    for frame_data in frame_datas:
        if frame_data is None:
            print("웹캠에서 더 이상 프레임을 읽어올 수 없습니다. 프로그램을 종료합니다.")
            cv2.destroyAllWindows()
            break
        frame = frame_data.frame
        fps = frame_data.fps
        cv2.imshow("Webcam", frame)
        cv2.imwrite('result.png', frame)

        # q를 누르면(ord('q')와 일치하면) 루프를 종료합니다.
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("사용자 요청으로 프로그램을 종료합니다.")
            sys.exit(0)



if __name__ == "__main__":
    main()
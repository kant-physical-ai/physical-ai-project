[PA] 과제 4 — 전체 파이프라인 통합
===
- 제출 방법: GitHub Repository 링크를 제출 폼에 입력
- 핵심 목표: 과제 1~3의 기능(입력·전처리 / 인식 / 좌표 변환·시각화)을 하나의 실행 파일로 통합하고, sense → compute → act 흐름과 단계별 처리 시간을 확인한다


# 이번 과제에서 만드는 것
- 지금까지 주차별로 나뉘어 있던 기능을 하나의 main.py로 이어, 웹캠부터 좌표 변환·시각화까지 한 번에 도는 파이프라인을 완성합니다.
```text
웹캠 입력                          — 과제 1
→ 물체 인식 (cx, cy)             — 과제 2
→ 픽셀 → 실세계 좌표 변환         — 과제 3
→ 화면 표시 + matplotlib 시각화   — 과제 1·3
→ 단계별 처리 시간(ms) 출력

최종 실행 시 터미널 예시:
웹캠 연결 성공
sense: 3.2ms | compute: 5.1ms | act: 8.4ms | FPS: 21.3
sense: 3.1ms | compute: 4.9ms | act: 8.1ms | FPS: 22.0
...
```
- 이 과제를 마치면 [웹캠] → [인식] → [좌표 변환] → [시각화]로 이어지는 실시간 파이프라인이 완성됩니다. 이것이 로봇의 감지(sense) → 판단(compute) → 행동(act) 기본 구조입니다.


# 전체 구현 흐름
- 과제 1~3의 코드를 지우고 새로 짜는 것이 아니라, 하나의 main() 흐름으로 이어 담는 작업입니다.
```text
main()
  ↓
웹캠 연결 / 변환 함수 import (transform.py 재사용)
  ↓
while True
 ├── [Sense]   frame 읽기                      ← 과제 1
 ├── [Compute] 인식(cx,cy) → 좌표 변환(wx,wy)    ← 과제 2·3
 ├── [Act]     화면 표시 + matplotlib 플롯       ← 과제 1·3
 └── 단계별 처리 시간(ms) 측정·출력             ← 신규
  ↓
'q' 종료 / 카메라·창 정리
```
- 과제 3의 transform.py를 그대로 재사용합니다. 새로 만들지 말고 week4/로 복사해 import하세요.

# 이번 과제에서 구현해야 하는 것
- 새로 많이 만드는 것이 아니라, 과제 1~3 함수를 하나의 파일에 모으고 main()으로 연결하는 것이 핵심입니다.

| 함수                                                           |출처|역할|
|--------------------------------------------------------------|---|---|
| create_mask() / find_objects() / draw_detection() / detect() |과제 2|물체 인식|
| rotation_matrix_2d() / scale_matrix_2d() / translate_2d()    |과제 3 (transform.py)|변환 행렬|
| pixel_to_world()                                             |과제 3|픽셀 → 실세계 변환|
| update_plot()                                                |과제 3|matplotlib 시각화|
|main()|과제 4 신규|sense → compute → act 통합 + 시간 측정|


# 제출 파일 구조
- 과제 4 제출 시 저장소는 아래 구조여야 합니다.
```text
physical-ai-project/
│
├── week1/main.py
├── week2/main.py
├── week3/main.py + transform.py
├── week4/
│   ├── main.py          # 통합 파이프라인 (필수)
│   └── transform.py     # 3주차 변환 함수 재사용
```


# 기능 명세
## 기능 1 — 과제 1~3 기능 모으기
> - 과제 2의 인식 함수와 과제 3의 변환·시각화를 week4/main.py 한 파일에 모읍니다. 변환 행렬은 transform.py에서 import합니다.
> - 구현 요건:
>  - 과제 2: create_mask, find_objects, draw_detection, detect
>  - 과제 3: pixel_to_world(내부에서 transform.py의 함수 사용), update_plot
>  - 파일 상단에서 from transform import rotation_matrix_2d, scale_matrix_2d, translate_2d
> - 확인 방법: week4/에서 python main.py 실행 시 import 오류 없이 시작되면 완료입니다.

## 기능 2 — sense → compute → act 통합 루프
> - 세 단계를 명확히 드러내는 메인 루프를 만듭니다.
> - 구현 요건:
>  - Sense: cap.read()로 프레임을 읽습니다 (없으면 종료)
>  - Compute: detect()로 인식하고, 가장 큰 물체의 중심에 pixel_to_world를 적용합니다
>  - Act: 화면에 좌표·FPS를 표시하고 matplotlib으로 좌표를 그립니다
>  - q로 종료하고 카메라·창을 정리합니다
> - 확인 방법: main.py 하나만 실행해도 과제 1~3 기능(인식·변환·플롯)이 모두 동작하면 완료입니다.

## 기능 3 — 단계별 처리 시간 측정
> - 각 단계(sense / compute / act)의 처리 시간을 ms 단위로 측정해 출력합니다.
> - 구현 요건:
>  - time.time()으로 각 단계 전후 시간을 기록합니다
>  - ms 단위로 환산해 출력하고, 전체 FPS도 함께 표시합니다 (과제 1의 30프레임 평균 유지)
>  - 확인 방법: 터미널에 세 단계의 ms 수치가 매 프레임 갱신되며 출력되면 완료입니다.
> - act가 유독 크게 나오는 건 정상입니다. cv2.waitKey()나 plt.pause()의 대기 시간이 act 구간에 포함되기 때문입니다.

# (선택) ROS2 연동
> - 여유가 있고 ROS2 환경이 있다면, 실세계 좌표를 토픽으로 publish해 Turtlesim을 움직여볼 수 있습니다.
> - 필수가 아닙니다. 기능 1~3까지만 해도 이번 과제 요건은 모두 충족됩니다. (관심 있으면 geometry_msgs/Point로 (wx, wy)를 publish하고, 별도 노드에서 구독해 /turtle1/cmd_vel로 매핑하는 구조로 확장할 수 있습니다.)
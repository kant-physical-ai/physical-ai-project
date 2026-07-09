과제 1 — 실시간 영상 입력 파이프라인 구축
===
- 제출 방법: GitHub Repository 링크를 제출 폼에 입력
- 핵심 목표: 웹캠 영상을 받아 전처리하고 FPS를 측정하는 루프를 직접 완성한다

#이번 과제에서 만드는 것
 - 아래 동작을 하는 Python 프로그램 하나를 완성합니다.
```text
웹캠 영상 입력
  → Grayscale 변환
  → Gaussian Blur 적용
  → Canny Edge 검출
  → 결과 화면 출력 (원본 + 전처리 결과 나란히)
  → FPS 측정값 화면 좌상단에 표시
  → 'q' 키를 누르면 종료
  
최종 실행 화면 예시:
[Original + FPS]        [Edges]
┌─────────────────┐    ┌─────────────────┐
│ FPS: 28.4       │    │  (경계선만 보임) │
│                 │    │                 │
│  (컬러 웹캠)    │    │  흰선/검정배경   │
└─────────────────┘    └─────────────────┘  
이 파이프라인은 STEP 2~4 과제의 뼈대가 되므로 구조를 깔끔하게 잡는 것이 중요합니다.
```

# 전체 구현 흐름
- 이번 과제는 아래 순서대로 기능을 구현합니다.
```text
main()

↓
웹캠 연결

↓
while True

↓
프레임(frame) 읽기

↓
전처리(preprocess)

 ├── Grayscale
 ├── Gaussian Blur
 └── Canny Edge

↓

FPS 계산

↓

FPS 화면 출력

↓

원본 + Edge 화면 합치기

↓

화면 출력

↓

'q' 입력 시 종료

↓

카메라 및 창 종료

```

# 이번 과제에서 구현해야 하는 함수
- 아래 함수들을 직접 구현하며 최종적으로 main()에서 모두 연결합니다.
  
|함수|입력|출력|역할|
|---|---|---|---|
|to_grayscale()|frame|gray|컬러 영상을 흑백으로 변환|
|apply_blur()|gray|blur|노이즈 제거|
|detect_edges()|blur|edges|경계선 검출|
|preprocess()|frame|gray, blur, edges|전처리 전체 수행|
|calculate_fps()|시간 정보|fps|FPS 계산|
|draw_fps()|frame, fps|frame|FPS 화면 출력|
|combine_frames()|frame, edges|combined|원본과 Edge 화면 합치기|
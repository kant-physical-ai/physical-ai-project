summary
====

# 라디안(radian)과 디그리(degree)
> - 디그리: 한바퀴 360도
> - 라디안: 수학적으로 편리한 단위 1라디안은 원주호의 길이 반지름과 같은 길이가 될떄의 각도정의: 1라디안 = 57.2958...도 디그리
>   - 즉 반지름이 1일때 반원의 둘리네느 3.14(파이)
> - [참고 link](https://m.blog.naver.com/wyepark/220517029219)




# 행렬
- 행렬 곱셈의 규칙: 행렬 곱셈은 [행] × [열]로 계산된다는 점을 기억하세요!

## 왜 rotation은 cos sin으로?
- 회전 행렬은 삼각함수 cos, sin으로 표현됩니다.
-  첫 번째 열(cos, sin): "원래 가로(1,0)가 어디로 갔나?"를 나타냅니다.
- 두 번째 열(-sin, cos): "원래 세로(0,1)가 어디로 갔나?"를 나타냅니다.
- 우리가 90도 같이 딱 떨어지는 각도만 돌리는 게 아니잖아요? 23.5도, 47.8도처럼 애매한 각도를 돌릴 때, 그 위치를 정확히 계산하기 위해 가장 좋은 도구가 삼각함수(cos, sin)이기 때문입니다.
- cos: 가로 방향으로 얼마나 이동했는지
- sin: 세로 방향으로 얼마나 이동했는지
- 즉, "내가 이만큼(각도) 돌렸을 때, 원래 좌표가 어디로 밀려나는지 그 비율을 미리 표로 만들어둔 것"이 바로 저 행렬입니다.
- 행렬은 "바뀐 위치를 적어놓은 표"
- 컴퓨터는 이 바뀐 위치를 기억하기 위해 표를 만듭니다. 그게 바로 회전 행렬입니다.
  $$\begin{bmatrix} \cos\theta & -\sin\theta \\ \sin\theta & \cos\theta \end{bmatrix}$$


## 왜 스케일은 대각선으로?
- 왜 [[sx, 0], [0, sy]]인가요?
- $$\begin{bmatrix} sx & 0 \\ 0 & sy \end{bmatrix} \times \begin{bmatrix} x \\ y \end{bmatrix} = \begin{bmatrix} (sx \cdot x) + (0 \cdot y) \\ (0 \cdot x) + (sy \cdot y) \end{bmatrix} = \begin{bmatrix} sx \cdot x \\ sy \cdot y \end{bmatrix}$$
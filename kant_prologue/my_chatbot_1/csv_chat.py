import kagglehub
import pandas as pd
from pandas import DataFrame
import gradio as gr

'''
# [Mini Kaggle 프로젝트] 나만의 미니 챗봇 만들기 (1)
https://teamsparta.notion.site/Mini-Kaggle-1-f002dc3ef51482d2bec9811f9e3b296a


# [Mini Kaggle 프로젝트] 나만의 미니 챗봇 만들기 (2)
https://teamsparta.notion.site/Mini-Kaggle-2-3ac2dc3ef51480ef80dcdf1cf49634a8
'''

def format_answer(results:DataFrame | None, title_column:str, search_columns:list[str]) -> None | str:
    """
    검색 결과를 챗봇 말투로 변환하는 함수
    title_column: 이름/제목 컬럼명 (본인 데이터에 맞게 수정)
    """
    if results is None:
        return "음... 관련된 정보를 찾지 못했어요 😥 다른 키워드로 물어봐 주실래요?"

    answer = f"이런 걸 찾았어요! 총 {len(results)}개를 보여드릴게요 👇\n\n"
    for idx, row in results.iterrows():
        answer += f"🔹 **{row[title_column]}**\n"
        for col in search_columns:
            answer += f"   - {col}: {row[col]}\n"
        answer += "\n"
    return answer



def chatbot(df: DataFrame, user_input:str, title_column: str, search_columns:list[str]) -> None | str:
    results = search_data(df, user_input, search_columns)
    return format_answer(results, title_column, search_columns)

def search_data(df: DataFrame, keyword: str, search_columns: list[str], top_n: int = 3) -> None | DataFrame:
    """
     keyword: 사용자가 입력한 검색어
     top_n: 최대 몇 개까지 결과를 보여줄지
     """
    keyword = keyword.lower()

    # 특징 컬럼들에서 keyword가 포함된 행을 찾기
    mask = df[search_columns].apply(
        lambda col: col.astype(str).str.lower().str.contains(keyword, na=False)
    ).any(axis=1)

    results = df[mask]

    if len(results) == 0:
        return None
    else:
        return results.head(top_n)


def main(isGUI: bool = False):
    # Download latest version
    # path = kagglehub.dataset_download("shuyangli94/food-com-recipes-and-user-interactions")
    # print("Path to dataset files:", path)
    '''
    Step 3️⃣ pandas로 데이터 열어보기

    새 코드 칸에서 pandas로 CSV 파일을 불러온 뒤, 아래 3가지를 출력해보세요.

    >
    >
    > 1. 데이터의 행/열 개수 (shape)
    > 2. 전체 컬럼 목록
    > 3. 상위 5개 행 미리보기
    > - **힌트**: `pd.read_csv()`, `.shape`, `.columns.tolist()`, `.head()`
    '''
    df = pd.read_csv('../archive/RAW_recipes.csv')
    print("Shape of the dataset:", df.shape)
    print("Columns in the dataset:", df.columns.tolist())
    print("First 5 rows of the dataset:")
    print(df.head())
    # 각 컬럼에 결측치(빈 값)가 몇 개 있는지 확인
    print("Missing values in each column:")

    ## Step 4️⃣ 결측치, Q&A 챗봇답게 다루기
    # 결측치(빈 값)를 "에러"로 취급하지 않고, **챗봇이 정직하게 대답하는 방식**으로 처리할 거예요.
    print(df.isnull().sum())

    # 1. 먼저 각 컬럼에 결측치가 몇 개 있는지 확인하세요.
    # 2. Step 3에서 고른 "특징 컬럼"들을 리스트로 정리하세요. (본인 데이터에 맞게!)
    # 3. 그 컬럼들의 빈 값을 `"정보없음"` 같은 문자열로 채워서, 검색 시 에러 없이 자연스럽게 처리되도록 만드세요.
    # - **힌트**: `df.isnull().sum()`, `df[col].fillna(...)`

    # Step 3에서 고른 "특징 컬럼"들을 리스트로 정리하세요 (본인 데이터에 맞게 수정!)
    search_columns = ['ingredients', 'name', 'description']  # 예시입니다. 본인 컬럼명으로 바꾸세요

    # 빈 값을 "정보없음"이라는 문자열로 채워서, 검색 시 에러 없이 "몰라요"라고 답할 수 있게 준비
    for col in search_columns:
        df[col] = df[col].fillna("정보없음")

    print("결측치 처리 완료!")
    print(df[search_columns].isnull().sum())  # 모두 0이 나오면 성공


    ## Step 5️⃣ 챗봇의 두뇌 만들기 (검색 함수)
    # 이제 사용자가 키워드를 입력하면, 데이터에서 관련된 행을 찾아주는 함수 `search_data(keyword, top_n=3)`를 만들어보세요.
    # > 함수가 해야 할 일:
    # >
    # > 1. 입력받은 키워드를 소문자로 통일
    # > 2. `search_columns`에 지정한 특징 컬럼들 중 하나라도 키워드를 포함하는 행을 찾기
    # > 3. 결과가 없으면 `None` 반환, 있으면 최대 `top_n`개까지만 반환
    # > - **힌트**: `.str.lower()`, `.str.contains(..., na=False)`, `.any(axis=1)`
    test_result = search_data(df,"chicken", search_columns)
    print(f'search-->{test_result}')


    ## Step 6️⃣ Q&A 챗봇 완성하기
    ### 6-1. 대화하는 것처럼 보이게 세팅하기
    # <aside>
    # Step 5에서 만든 검색 함수를 가지고, 실제로 대화하듯 질문하고 답하는 Q&A 챗봇을 완성해봅시다. 아래 세 가지를 순서대로 만들어보세요.
    #
    # > 1. `format_answer(results, title_column)` — 검색 결과(데이터프레임)를 사람이 읽기 좋은 챗봇 말투 문자열로 바꿔주는 함수. 결과가 `None`이면 "못 찾았어요" 같은 안내 문구를, 결과가 있으면 제목 + 특징 컬럼 값들을 이모지와 함께 보여주세요.
    # > 2. `chatbot(user_input, title_column)` — `search_data()`로 검색하고, `format_answer()`로 포맷팅해서 반환하는 함수.
    # > 3. `while` 반복문으로 사용자 입력을 계속 받다가, `"종료"`를 입력하면 멈추도록 만들기.
    # > - **힌트**: 이 단계에서는 `title_column` 변수를 본인 데이터의 실제 "이름/제목" 컬럼명으로 반드시 지정해야 해요.
    #
    # </aside>

    # ===== 챗봇 실행 (반복 대화) =====
    title_column = 'name'  # ⚠️ 본인 데이터의 "이름/제목" 컬럼명으로 반드시 수정하세요!
    if not isGUI:
        print("🤖 안녕하세요! 무엇이든 물어보세요. (종료하려면 '종료' 입력)")

        while True:
            user_input = input("\n👤 나: ")
            if user_input == "종료":
                print("🤖 챗봇을 종료합니다. 안녕히 가세요!")
                break
            answer = chatbot(df, user_input, title_column, search_columns)
            print(f"\n🤖 챗봇: {answer}")
    else:
        def callback(message, history):
            print(f'input {message}')
            answer = chatbot(df, message, title_column, search_columns)
            print(f"\n🤖 챗봇: {answer}")
            return answer
        demo = gr.ChatInterface(
            fn=callback,
            title="🤖 나만의 CSV 챗봇",
            description="궁금한 걸 물어보세요! (데이터: 본인 데이터셋 이름 적어두기)",
            examples=["curry", "PG", "LAL"], #이 부분도 마찬가지로 본인 데이터에 포함된 내용 적어두기!
        )
        demo.launch(share=True)

if __name__ == '__main__':
    main(True)
#!pip install -q -U google-genai
import os

from google import genai





import pandas as pd
from pandas import DataFrame
import gradio as gr
## env variable
GEMINI_API_KEY =  os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = 'gemini-3.5-flash-lite'
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






def extract_keyword(user_input):
    print(f'GEMINI_API_KEY: {GEMINI_API_KEY[:5]}')
    client = genai.Client(api_key=GEMINI_API_KEY)
    """
    자연어 질문에서 데이터 검색에 쓸 핵심 키워드(영어 or 데이터에 쓰인 언어)를 추출
    """
    prompt = f"""다음은 사용자가 데이터에서 무언가를 찾기 위해 입력한 질문입니다.
이 질문에서 검색에 사용할 핵심 키워드 1개만 뽑아주세요.
설명 없이 키워드 단어(또는 짧은 구)만 출력하세요.

질문: "{user_input}"
"""
    print(f'Request prompt: {prompt}')

    try:
        response = client.models.generate_content(
            model=GEMINI_MODEL,  # 짧은 작업이라 가벼운 모델로 충분해요
            contents=prompt
        )
        keyword = response.text.strip()
        return keyword
    except Exception as e:
        print("키워드 추출 오류:", e)
        return user_input  # 실패하면 원래 입력 그대로 사용


def ask_gemini(user_input, results, title_column, search_columns):

    print(f'GEMINI_API_KEY: {GEMINI_API_KEY[:5]}')
    client = genai.Client(api_key=GEMINI_API_KEY)

    """
    user_input: 사용자의 원래 질문
    results: search_data()로 찾은 데이터프레임 (또는 None)
    title_column: 이름/제목 컬럼명
    """
    if results is None:
        # 검색 결과가 아예 없으면 Gemini를 호출할 필요 없이 바로 안내
        return "음... 관련된 정보를 찾지 못했어요 😥 다른 키워드로 물어봐 주실래요?"

    # 검색된 행들을 Gemini가 읽기 좋은 텍스트로 변환
    context = ""
    for idx, row in results.iterrows():
        context += f"-{row[title_column]}: "
        context += ", ".join([f"{col}={row[col]}" for col in search_columns])
        context += "\n"

    prompt = f"""당신은 친절한 Q&A 챗봇입니다. 아래는 사용자의 질문과 관련해서 데이터베이스에서 찾은 정보입니다.

[사용자 질문]
{user_input}

[검색된 데이터]
{context}

[답변 규칙]
1. 반드시 위 데이터에 있는 내용만 근거로 답변하세요. 데이터에 없는 내용은 지어내지 마세요.
2. 친근하고 자연스러운 말투로, 이모지를 적절히 섞어 설명해주세요.
3. 데이터에 있는 항목들을 나열만 하지 말고, 사용자 질문에 맞춰 요약하거나 비교해주세요.
4. 답변은 5문장 이내로 간결하게 작성하세요.
"""
    print(f"Request Prompt: {prompt}")
    try:
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt
        )
        return response.text
    except Exception as e:
        # Gemini 호출이 실패해도 챗봇이 멈추지 않도록 안전장치
        print("Gemini 호출 오류:", e)
        return format_answer(results, title_column)  # 어제 만든 함수로 대체

def main():
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
    df = pd.read_csv('../../archive/RAW_recipes.csv')
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
    # 테스트 (본인 데이터에 맞는 키워드로 바꿔서 테스트하세요!)
    # user_keyword = 'chicken'
    # test_results = search_data(df, user_keyword, search_columns)
    # print(ask_gemini("치킨 들어간 요리 뭐 있어?", test_results, title_column, search_columns))

    # 1차: 자연어 질문에서 키워드 추출 시도
    user_input = '매운 음식 추천해줘 (메뉴명 영어로 알려줘)'
    keyword = extract_keyword(user_input)
    print(f'Gemini recommended keyword: {keyword}')
    results = search_data(df, keyword, search_columns)

    # 2차: 키워드로 못 찾았으면 원래 입력으로 한 번 더 시도
    if results is None:
        results = search_data(df, 'chicken', search_columns)

    # 3차: 그래도 없으면 정직하게 못 찾았다고 안내
    if results is None:
        return "음... 관련된 정보를 찾지 못했어요 😥 다른 키워드로 물어봐 주실래요?"

    # Gemini에게 자연스러운 답변 생성 요청
    result = ask_gemini(keyword, results, title_column, search_columns)
    print(result)


    # while True:
    #     user_input = input("\n👤 나: ")
    #     if user_input == "종료":
    #         print("🤖 챗봇을 종료합니다. 안녕히 가세요!")
    #         break
    #     answer = chatbot(df, user_input, title_column, search_columns)
    #     print(f"\n🤖 챗봇: {answer}")
    #


if __name__ == '__main__':
    main()


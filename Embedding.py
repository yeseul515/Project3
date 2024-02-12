import os
from dotenv import load_dotenv
from openai import OpenAI
import pandas as pd

load_dotenv()

api_key = os.getenv('OPEN_API_KEY')

# 모델 불러오기
client = OpenAI()

def get_embedding(text, model="text-embedding-ada-002"):
   return client.embeddings.create(input = [text], model=model).data[0].embedding

# 웹스크래핑한 데이터 불러오기
cafe = pd.read_csv(r'C:\Users\kimye\OneDrive\바탕 화면\sba\final_cleaned_data.csv', encoding='cp949', index_col=0)

# Open AI의 Embedding model을 활용하여 embedding
result = []
for text in cafe.columns:
    print(text)
    embedding_result = get_embedding(text)
    result.append(embedding_result)

embedding_df = pd.DataFrame(result).T
embedding_df.columns = cafe.columns
embedding_df.to_csv('final_embedding.csv')

# 각 카페를 임베딩 벡터 공간에 표현하는 새로운 행렬을 생성
# 카페명 X 분위기 matrix와 분위기 X 임베딩 벡터 matrix를 내적
resul_dot = cafe.dot(embedding_df.T)
resul_dot.to_csv('final_cafe_embedding.csv')

# 임베딩 벡터와 쿼리로 들어오는 text를 임베딩하여 유사도 계산 후 입력한 text와 가장 유사한 TOP5 리스트
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

def cal_sim_cafe(text):
    query = get_embedding(text)
    resul_dot = pd.read_csv(r'C:\Users\kimye\OneDrive\바탕 화면\sba\final_cafe_embedding.csv', index_col= 0)
    # 데이터프레임을 NumPy 배열로 변환
    df_array = resul_dot.to_numpy()

    # 비교 벡터를 2차원 배열로 변환 (cosine_similarity는 2차원 배열을 요구함)
    comparison_vector_reshaped = np.array(query).reshape(1, -1)

    # 코사인 유사도 계산
    cosine_similarities = cosine_similarity(df_array, comparison_vector_reshaped)

    # 결과를 데이터프레임에 추가
    resul_dot['cosine_similarity'] = cosine_similarities.flatten()
    TOP5 = resul_dot['cosine_similarity'].sort_values(ascending=False).index[:5]
    # 결과 출력
    return TOP5

cal_sim_cafe('오래 앉아있을 수 있는 곳')
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import pandas as pd
import os
from dotenv import load_dotenv
from openai import OpenAI
from PIL import Image
import folium
from streamlit_folium import folium_static
from geopy.geocoders import Nominatim

st.title('댕냥아 카페가자 :dog::cat:')

st.header('1. 위치 선택하기   :earth_asia:')

# 셀렉트박스 : 여러개중에 한개를 선택할 때
location = ['서울 동남(강남구, 강동구, 서초구, 송파구)', '서울 동북(광진구, 동대문구, 성동구, 중랑구)', '서울 북동(강북구, 노원구, 도봉구, 성북구)',
            '서울 서남(강서구, 관악구, 구로구, 금천구, 양천구, 영등포구)', '서울 서북(마포구, 서대문구, 은평구)', '서울 중부(용산구, 종로구, 중구)']
my_choice = st.selectbox('**사용자의 위치를 선택해주세요:point_down:**', location)

st.write('**사용자님의 위치는 {}입니다.**'.format(my_choice))

load_dotenv()

api_key = os.getenv('OPENAI_API_KEY')

client = OpenAI()


def get_embedding(text, model="text-embedding-ada-002"):
    return client.embeddings.create(input=[text], model=model).data[0].embedding


def cal_sim_cafe(text):
    query = get_embedding(text)
    result_dot = pd.read_csv(r'C:\Users\kimye\Project\final_cafe_embedding.csv', index_col=0)
    # 데이터프레임을 NumPy 배열로 변환
    df_array = result_dot.to_numpy()

    # 비교 벡터를 2차원 배열로 변환 (cosine_similarity는 2차원 배열을 요구함)
    comparison_vector_reshaped = np.array(query).reshape(1, -1)

    # 코사인 유사도 계산
    cosine_similarities = cosine_similarity(df_array, comparison_vector_reshaped)

    # 결과를 데이터프레임에 추가
    result_dot['cosine_similarity'] = cosine_similarities.flatten()
    TOP5 = result_dot['cosine_similarity'].sort_values(ascending=False).index[:5]
    # 결과 출력
    return TOP5


def find_location(Top5):
    loc = pd.read_csv(r'C:\Users\kimye\Project\Pjt3\cafe_address.csv', encoding='cp949')
    df_loc = loc.set_index(loc.columns[0])
    df = pd.DataFrame(columns=['카페', '주소'])
    for idx, cafe in enumerate(Top5):
        if cafe in df_loc.index:
            df.loc[idx, '카페'] = cafe
            df.loc[idx, '주소'] = df_loc.loc[cafe, '주소']
        else:
            print('다른 키워드를 입력하세요.')
    df['순위'] = df.reset_index()['index'].rank().astype(int)
    df['순위'] = df['순위'].apply(lambda x: str(x))
    df = df.set_index('순위')
    return df


def print_img():
    col1, col2, col3 = st.columns(3)
    image_local = Image.open(r'C:\Users\kimye\Project\Pjt3\walking_dog.png')

    with col1:
        st.write(' ')

    with col2:
        st.image(image_local, width=300)

    with col3:
        st.write(' ')
    # st.image(image_local, width = 200)


def geocoding(address):
    geolocoder = Nominatim(user_agent='South Korea', timeout=None)
    geo = geolocoder.geocode(address)

    return geo.latitude, geo.longitude


def merged(split_address):
    merged_addresses = []
    for idx_address in range(len(split_address)):
        merged = ' '.join(split_address[:-(idx_address + 1)])
        merged_addresses.append(merged)
    return merged_addresses


def get_from_address(address):
    try:
        latitude, longitude = geocoding(address)
    except AttributeError:
        split_address = address.split()
        merged_addresses = merged(split_address)
        for i in merged_addresses:
            try:
                latitude, longitude = geocoding(i)
                if latitude is not None and longitude is not None:
                    break
            except:
                continue
    return latitude, longitude


################################################################################################################################################

def main():
    st.header('2. 원하는 카페 분위기 입력하기 :coffee:')

    # 사용자로부터 텍스트 입력 받기
    user_input = st.text_input("분위기를 입력하세요:", "")

    # 입력된 텍스트를 출력
    if user_input:
        print_img()
        Top5 = cal_sim_cafe(user_input)
        result = find_location(Top5)
        result['위도'], result['경도'] = zip(*result['주소'].apply(get_from_address))
        st.write("**추천 카페 리스트**")
        st.table(result)  # 인덱스와 컬럼 명이 함께 출력됨

        # 1. mapcenter 구하기
        # 1-1. 위도, 경도 받기
        map_center_locations = [result['위도'].values, result['경도'].values]

        # 1-2. 5개의 위도, 5개의 경도 평균 뽑기
        map_center = [map_center_locations[0].mean(), map_center_locations[1].mean()]

        # 2. 평균을 기준으로 지도 그리기
        my_map = folium.Map(location=map_center, zoom_start=12)

        # 3. 표시할 위도, 경도 5개 받기
        target_loc = []
        for i in range(5):
            lat = map_center_locations[0][i]
            lon = map_center_locations[1][i]
            target_loc.append([lat, lon])

        # 4. 입력된 5개의 좌표를 지도에 마커로 표시
        for i, location in enumerate(target_loc):
            folium.Marker(location=target_loc[i]).add_to(my_map)

        # 5. Folium 지도를 Streamlit 앱에 표시
        folium_static(my_map)


if __name__ == "__main__":
    main()
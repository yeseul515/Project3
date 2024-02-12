# 네이버 '갈수있어 강아지도' 웹스크래핑 코드
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import ActionChains
from selenium import webdriver
import time
from selenium.webdriver.common.keys import Keys
import pandas as pd

driver = webdriver.Chrome()
driver.get('https://map.naver.com/p/favorite/myPlace/folder/e6e01cdc5b8d4c07a672b93f7d35d907?c=12.00,0,0,0,dh')
driver.maximize_window()
time.sleep(2)

# iframe으로 접속
iframe = driver.find_element(By.CSS_SELECTOR, 'iframe#myPlaceBookmarkListIframe') # iframe 선택
driver.switch_to.frame(iframe)

# 페이지 다운
def page_down(num):
    body = driver.find_element(By.CSS_SELECTOR, 'body')
    body.click()
    for i in range(num):
        body.send_keys(Keys.PAGE_DOWN)

page_down(600)

def find_address():
    address_btn = driver.find_elements(By.CSS_SELECTOR, 'div.place_section_content > div > div.O8qbU.tQY7D > div')
    address = address_btn[0].find_elements(By.TAG_NAME, 'a')
    return address[0].text

search_list_box = driver.find_element(By.CSS_SELECTOR, '#__next > div > div > div._2qKjD2._2Rfog3 > div > div._3ObMW8 > ul')
search_list = search_list_box.find_elements(By.TAG_NAME, 'li')
result_list = [sample.find_element(By.CSS_SELECTOR, 'span._2gfp-T').text for sample in search_list]
result_list

WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, '#__next > div > div > div._2qKjD2._2Rfog3 > div > div._3ObMW8 > ul')))

search_list_box = driver.find_element(By.CSS_SELECTOR, '#__next > div > div > div._2qKjD2._2Rfog3 > div > div._3ObMW8 > ul')
search_list = search_list_box.find_elements(By.TAG_NAME, 'li')

def find_review_button():
    for i in range(1, 6):
        try:
            review_btn = driver.find_element(By.CSS_SELECTOR, f'#app-root > div > div > div > div.place_fixed_maintab > div > div > div > div > a:nth-child({i})')
            review_text = driver.find_element(By.CSS_SELECTOR, f'#app-root > div > div > div > div.place_fixed_maintab > div > div > div > div > a:nth-child({i}) > span').text
            if review_text == "리뷰":
                return review_btn
        except:
            continue
    return None

def get_review():
    review_space = driver.find_elements(By.CSS_SELECTOR, '#app-root > div > div > div')
    role_box = review_space[0].find_elements(By.TAG_NAME, 'ul')
    review_list = role_box[0].find_elements(By.TAG_NAME, 'li')
    return len(review_list), review_list

def click_detail_btn():
    while True:
        detail_btn = driver.find_elements(By.CSS_SELECTOR, 'div.place_section.no_margin.mdJ86 > div > div > div.k2tmh > a')
        if detail_btn:
            new_count, review_list = get_review()
            review_contents = [review.text.split('\n')[0][1:-1] for review in review_list]
            review_counts = [int(review.text.split('\n')[2]) for review in review_list]
            detail_btn[0].click()
            time.sleep(1)
            # print(review_contents)
            # print(review_counts)
            if any(count <= 5 for count in review_counts):
                break
        else:
            continue
    return review_list, review_contents, review_counts

total_review = []
total_review_cnt = []
cafe_list = []
address_list = []
for i in range(300, 330):
    print(i)
    actions = ActionChains(driver)
    actions.move_to_element(search_list[i]).click().perform()
    close = driver.find_elements(By.CSS_SELECTOR, '#modal-root > div.place_modal_content_web.afAvNc._6EdYRV > div._29rZGD > button')
    if close:
        print("폐업한 가게입니다. 통과합니다.")
        close[0].click()
        time.sleep(2)
        continue
    else:
        driver.switch_to.default_content()
        time.sleep(2)

        res_iframe = driver.find_element(By.CSS_SELECTOR, 'iframe#entryIframe')
        driver.switch_to.frame(res_iframe)
        time.sleep(2)

        address = find_address()

        review_btn = find_review_button()
        if review_btn is None:
            print(f"리뷰 버튼을 찾을 수 없습니다: 카페 {i+1}")
            driver.switch_to.default_content()
            iframe = driver.find_element(By.CSS_SELECTOR, 'iframe#myPlaceBookmarkListIframe')
            driver.switch_to.frame(iframe)
            continue
        else:
            review_btn.click()

        time.sleep(2)

        find_cafe_name = driver.find_elements(By.CSS_SELECTOR, '#_title > div > span.Fc1rA')
        join_review = driver.find_elements(By.CSS_SELECTOR, 'div.rWbYE > a')
        keyword_review = driver.find_elements(By.CSS_SELECTOR, 'div.place_section.no_margin.mdJ86 > h2')

        if keyword_review:
            if not join_review:
                cafe_name = find_cafe_name[0].text
                cafe_list.append(cafe_name)
                address_list.append(address)
                print(cafe_name, address)
                review_list, review_contents, review_counts = click_detail_btn()
            else:
                print('review가 10개 이하입니다. 통과합니다')
                driver.switch_to.default_content()
                iframe = driver.find_element(By.CSS_SELECTOR, 'iframe#myPlaceBookmarkListIframe') # iframe 선택
                driver.switch_to.frame(iframe)
                continue
        else:
            print('방문자 리뷰가 없습니다. 통과합니다.')
            driver.switch_to.default_content()
            iframe = driver.find_element(By.CSS_SELECTOR, 'iframe#myPlaceBookmarkListIframe') # iframe 선택
            driver.switch_to.frame(iframe)
            continue

        time.sleep(2)

        driver.switch_to.default_content()

        total_review.append(review_contents)
        total_review_cnt.append(review_counts)
        print(total_review, total_review_cnt)
        iframe = driver.find_element(By.CSS_SELECTOR, 'iframe#myPlaceBookmarkListIframe') # iframe 선택
        driver.switch_to.frame(iframe)
        time.sleep(2)

# 수집된 데이터를 데이터 프레임으로 만들기
df_list = []
for i in range(len(total_review)):
    review_data = dict(zip(total_review[i], total_review_cnt[i] ))
    df = pd.DataFrame([review_data])  # 딕셔너리를 사용하여 데이터프레임 생성
    df_list.append(df)
final_df = pd.concat(df_list, ignore_index=True)  # 리스트에 저장된 모든 데이터프레임을 합침
final_df = final_df.fillna(0)
final_df.index = cafe_list

final_df
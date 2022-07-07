import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup as bs
import requests as rq
import re , os , pyautogui

from typing import Union , Optional


# 클래스내의 모든 멤버변수를 유연하게 사용하고 싶다 => 클래스 상속
# 클래스내의 특정 멤버변수만을 가져와서 사용하고 싶다 => 클래스 내의 멤버변수만 추출

class ChromeDriver:
    # ChromeDriver class의 생성자 정의
    # - 매개변수는 따로 받지 않도록 함
    def __init__(self):
        # - 멤버변수 정의

        # - options 객체
        self.chrome_options = Options()

        # headless Chrome
        self.chrome_options.add_argument('--headless')

        # 브라우저 꺼짐 방지
        self.chrome_options.add_experimental_option('detach',True)

        # User-Agent
        self.chrome_options.add_argument(
            'user-agent=Mozilla/5.v0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.104 Whale/3.13.131.36 Safari/537.36'
         )

        # 불필요한 에러메시지 제거
        self.chrome_options.add_experimental_option('excludeSwitches',['enable-logging'])

        # Service 객체
        self.service = Service(executable_path=ChromeDriverManager().install())

        # Driver 객체
        self.browser = webdriver.Chrome(service=self.service,options=self.chrome_options)
        self.browser.maximize_window()


# ChromeDriver class는 상속받지 않고 멤버변수에 ChromeDriver에 대한 객체 생성
class Application:
    # Crawling class의 생성자 정의
    # - 매개변수는 따로 받지 않도록 함
    def __init__(self):
        # - 멤버변수 정의

        # translate_keword 함수 실행 및 리턴 값 멤버변수로 정의
        self.keword : str = self.translate_keword()

        # 타겟 사이트 url
        self.url : str = f"https://eletronicos.mercadolivre.com.br/{self.keword}"

        # ChromeDriver class 객체 생성
        self.chrome_driver = ChromeDriver()

        # driver 객체 정의
        self.browser = self.chrome_driver.browser

        # header 정보
        self.headers : dict = {
            'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.57 Whale/3.14.133.23 Safari/537.36'
                        }

        # run 메소드 실행
        self.run()


    # 타겟 데이터 추출 메소드 정의
    def run(self) -> list :
        self.browser.get(url=self.url)
        self.browser.implicitly_wait(10)

        # 상위 3개의 링크 뽑는 메소드 호출
        links : list = self.get_three_link()

        # 상세페이지 내의 데이터 추출
        results = [self.get_content(link=link) for link in links]

        return results

    # 상위 3개의 링크 추출하는 메소드 정의
    def get_three_link(self) -> list:
        soup = bs(self.browser.page_source,'html.parser')

        # 상위 3개의 링크만 가져옴
        link_list : list = soup.select('a.ui-search-result__content.ui-search-link',limit=3)

        links : list = []
        for link in link_list :
            links.append(link.attrs['href'])

        return links

    # 각 링크별 추출 데이터 가져오기
    def get_content(self,link: str) -> list:
        save_data : list = []

        response = rq.get(link,headers=self.headers)
        html = response.text
        soup = bs(html,'html.parser')


        # 데이터정보 추출
        # - 타이틀
        try :
            title : str = soup.select_one('h1.ui-pdp-title').text
        except :
            title : str = '-'

        # 가격
        try :
            price : Union[str,int]   = soup.select('div.ui-pdp-price__second-line span.andes-money-amount__fraction')[0].text.strip()
            price : int  = int(re.sub('[^0-9]','',price))
        except :
            price : int  = 0

        # 리뷰수
        try :
            review_count : Union[str , int] = soup.select_one('span.ui-pdp-review__amount').text.strip()
            review_count : int = int(re.sub('[^0-9]','',review_count))
        except:
            review_count = 0

        # 이미지 사진
        try :
            img = soup.select('figure.ui-pdp-gallery__figure > img')[0]
            img = img.attrs['src']

            # 이미지 저장
        except :
            pass

        # 데이터 리스트 변수에 저장
        save_data.append([title,price,review_count])

        # 추출데이터 출력
        print(f"제목 : {title}\n가격 : {price}\n리뷰 수 : {review_count}\n")

        # 저장된 데이터 return
        return save_data


    # keword 입력값 replace 처리하는 메소드 정의
    def translate_keword(self) -> str:
        keword : str = input('키워드를 입력해주세요ㅕ\n\nEx ) smart tv samsung (각 word별 띄어쓰기 구분 O)\n\n:')
        keword = keword.replace(' ', '-')
        return keword


if __name__ == '__main__' :
    app = Application()

    app.run()



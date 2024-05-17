import requests
from bs4 import BeautifulSoup       # 웹에서 가져온 HTML코드를 파이썬에서 편하게 분석해주는 라이브러리
import re
from datetime import datetime, timedelta

"""
def google_news_crawler(query):
    # 구글 뉴스 검색 URL
    url = "https://news.google.com/search?q={}&hl=ko&gl=KR&ceid=KR%3Ako".format(query)      # URL 내에 query 변수명을 그대로 입력했더니 'query'라는 문자열을 검색한 결과가 나옴. 전에는 멀쩡했는데 왜 이러는지 모르겠음

    # HTTP 요청 보내기
    response = requests.get(url)

    # HTTP 요청 성공하면 HTML 파싱
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 뉴스 제목과 링크 가져오기
        allNews = soup.select('c-wiz.XBspb')

        for news in allNews:
            # 언론사 추출
            press = news.select_one('div.vr1PYe').text

            # 제목 추출
            title = news.select_one('a.JtKRv')     # 클래스가 'JtKRv'인 a태그를 선택하고 내용 반환

            # 날짜 추출
            datetime_str = news.select_one('div.UOVeFe time.hvbAAd')['datetime']

            # datetime 값을 파싱
            dt = datetime.strptime(datetime_str, '%Y-%m-%dT%H:%M:%SZ')

            # 9시간을 더해 한국 시간으로 변환
            korean_time = dt + timedelta(hours = 9)

            # 분까지만 출력 (strftime으로 포맷)
            formatted_time = korean_time.strftime('%Y-%m-%d %H:%M')

            # 링크 추출
            link = news.select_one('a.JtKRv')['href']
            link = link.lstrip('.')

            print(press)
            print(title)
            print(formatted_time)
            print("https://news.google.com"+link)
            print("")

    else:
        print("HTTP 요청 실패")

if __name__ == "__main__":
    query = "게임"
    google_news_crawler(query)

"""

def news_crawler():
    # 구글 뉴스 검색 URL
    url = "https://www.gamevu.co.kr/news/articleView.html?idxno=32810"

    # HTTP 요청 보내기
    response = requests.get(url)
    d_response = response.content.decode('cp949','replace')
    # 한글 폰트 깨짐. html 인코딩이 enc-kr로 되어있으면 크롤링할 때 글씨가 깨질 수 있음
    # 그래서 utf-8이나 cp949로 인코딩을 바꿔야 함. utf-8은 그대로 깨져서 나오길래 cp949로 인코딩했더니 성공함

    # HTTP 요청 성공하면 HTML 파싱
    if response.status_code == 200:
        soup = BeautifulSoup(d_response, 'html.parser')
        
        # 제목 추출
        news_title = soup.select_one('font.headline-title').text
        # 제목 텍스트만 출력하기 위해 .text를 사용함

        # 기사 본문 추출
        # news_d = soup.select('div.cont-body')
        # 본문의 텍스트만 출력하고 싶은데 html의 태그까지 출력됨. 해결방안을 찾아야 할 듯
        news_d = soup.select('div.cont-body > p')
        # div 클래스가 cont-body인 부분 중에서 태그가 p인 것만 추출. 근데 태그까지 출력됨. 쉽지않음
        # news_d의 타입이 list인데 이걸 이용하면 어케 해결할 수 있지 않을까 싶음. news_d의 각 인덱스에 담긴 string의 앞과 뒤를 지워주면 태그가 제거될 것 같음!
        i = 0
        ns = []
        while i < len(news_d):
            ns.append(news_d[i].text.replace(u'\xa0', u' '))
            i = i + 1
        # 진짜 다 좋은데 \xa0 이거 뭔데 공백이 왜 이걸로;;
        # 비 공백 공간 문자라고 함. 위에 문제 고치려고 replace(u'\xa0', u' ')를 사용함! 

        # 날짜 추출
        datetime_str = soup.select_one('li.date').get_text()
        datetime_str = datetime_str[3:]
        # datetime_str의 문자열에 '승인' 글씨를 제거하고 날짜만 남기기 위해 앞의 3개의 문자를 제거함

        # datetime 값을 파싱
        dt = datetime.strptime(datetime_str, '%Y.%m.%d %H:%M')

        # 9시간을 더해 한국 시간으로 변환
        korean_time = dt + timedelta(hours = 9)

        # 분까지만 출력 (strftime으로 포맷)
        formatted_time = korean_time.strftime('%Y-%m-%d %H:%M')

        print(news_title)
        print(formatted_time)
        print(ns)
        print("")
        

    else:
        print("HTTP 요청 실패")

if __name__ == "__main__":
    news_crawler()



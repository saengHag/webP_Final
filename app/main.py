import requests
from bs4 import BeautifulSoup       # 웹에서 가져온 HTML코드를 파이썬에서 편하게 분석해주는 라이브러리
import re
from datetime import datetime, timedelta

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
import requests
from bs4 import BeautifulSoup       # 웹에서 가져온 HTML코드를 파이썬에서 편하게 분석해주는 라이브러리
import re
from datetime import datetime, timedelta

def google_news_crawler(query):
    # 구글 뉴스 검색 URL
    url = "https://news.google.com/search?q={query}&hl=ko&gl=KR&ceid=KR%3Ako"

    # HTTP 요청 보내기
    response = requests.get(url)

    # HTTP 요청 성공하면 HTML 파싱
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        print(soup)

    else:
        print("HTTP 요청 실패")

if __name__ == "__main__":
    query = "게임"
    google_news_crawler(query)
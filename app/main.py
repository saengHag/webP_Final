from typing import Union
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.encoders import jsonable_encoder
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import requests
import re
from datetime import datetime, timedelta
from bs4 import BeautifulSoup       # 웹에서 가져온 HTML코드를 파이썬에서 편하게 분석해주는 라이브러리

app = FastAPI()

app.mount("/static", StaticFiles(directory="app"), name="static")       # 이미지 출력을 원활하게 하기 위한 명령어. app 디렉토리 안에서 탐색

templates = Jinja2Templates(directory = "app/htmls")        #'htmls' 디렉토리 내의 html 코드를 참조

def google_news_crawler(keyword):
    # 구글 뉴스 검색 URL
    url = "https://news.google.com/search?q={}&hl=ko&gl=KR&ceid=KR%3Ako".format(keyword)      # URL 내에 query 변수명을 그대로 입력했더니 'query'라는 문자열을 검색한 결과가 나옴. 전에는 멀쩡했는데 왜 이러는지 모르겠음

    # HTTP 요청 보내기
    response = requests.get(url)

    # HTTP 요청 성공하면 HTML 파싱
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 언론사 추출
        press = soup.select_one('div.vr1PYe').text

        # 제목 추출
        title = soup.select_one('a.JtKRv').text

        # 날짜 추출
        datetime_str = soup.select_one('div.UOVeFe time.hvbAAd')['datetime']

        # datetime 값을 파싱
        dt = datetime.strptime(datetime_str, '%Y-%m-%dT%H:%M:%SZ')

        # 9시간을 더해 한국 시간으로 변환
        korean_time = dt + timedelta(hours = 9)

        # 분까지만 출력 (strftime으로 포맷)
        formatted_time = korean_time.strftime('%Y-%m-%d %H:%M')

        # 링크 추출
        link = soup.select_one('a.JtKRv')['href']
        link = link.lstrip('.')

        # 본문 링크를 새 변수에 저장
        article_url = "https://news.google.com" + link

        # 본문 크롤링을 위해 HTTP 요청 보내기
        response_2 = requests.get(article_url)

        if response_2.status_code == 200:
            soup2 = BeautifulSoup(response_2.text, 'html.parser')

            # 기사 전문 추출
            news_main = soup2.select('div')
            i = 0
            ns = []
            while i < len(news_main):
                if title in news_main[i] :
                    ns.append(str(news_main[i].text.replace(u'\xa0', u' ')).replace('\n', '<br>').replace('\r', ''))
                i = i + 1

        """
        # 뉴스 제목과 링크 가져오기
        allNews = soup.select('c-wiz.XBspb')
        
        # 언론사 추출
        press = allNews.select_one('div.vr1PYe').text

        # 제목 추출
        title = allNews.select_one('a.JtKRv')     # 클래스가 'JtKRv'인 a태그를 선택하고 내용 반환

        # 날짜 추출
        datetime_str = allNews.select_one('div.UOVeFe time.hvbAAd')['datetime']

        # datetime 값을 파싱
        dt = datetime.strptime(datetime_str, '%Y-%m-%dT%H:%M:%SZ')

        # 9시간을 더해 한국 시간으로 변환
        korean_time = dt + timedelta(hours = 9)

        # 분까지만 출력 (strftime으로 포맷)
        formatted_time = korean_time.strftime('%Y-%m-%d %H:%M')

        # 링크 추출
        link = allNews.select_one('a.JtKRv')['href']
        link = link.lstrip('.')

        # time.sleep(10)
        """
        """
        a = 0
        for news in allNews:
            if a > 5:
                break
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
            
            a = a + 1
        
            print(press)
            print(title)
            print(formatted_time)
            print("https://news.google.com"+link)
            print("")
            """
            
    else:
        print("HTTP 요청 실패")

    return ( press, title, formatted_time, "https://news.google.com"+link, ns )
# press, title, formatted_time, "https://news.google.com"+link

@app.get("/")
def root():
    return {"message":"Hello World"}

@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}

@app.post("/search")
def get_keyword():
    return {"message":"Search whatever you want"}

@app.get("/search/{keyword}", response_class=HTMLResponse)
def print_news(keyword: str, request: Request):
    #press, title, time, link = whole_google_news_crawler(keyword)
    #return { "press": press, "title": title, "formatted_time": time, "link": link }
    press, title, date, link, detail = google_news_crawler(keyword)
    #return { "언론사": press, "제목": title, "작성일자": time, "링크": link }   # press, title, time, link
    return templates.TemplateResponse("news.html", { "request": request, "keyword": keyword, "press": press, "title": title, "date": date, "link": link, "detail": detail })
# "언론사": press, "제목": title, "작성일자": time, "링크": link
from typing import Union
from fastapi import FastAPI, Request, Form
from fastapi.staticfiles import StaticFiles
from fastapi.encoders import jsonable_encoder
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import requests
from datetime import datetime, timedelta
from bs4 import BeautifulSoup, Comment       # 웹에서 가져온 HTML코드를 파이썬에서 편하게 분석해주는 라이브러리


app = FastAPI()

app.mount("/static", StaticFiles(directory="app"), name="static")       # 이미지 출력을 원활하게 하기 위한 명령어. app 디렉토리 안에서 탐색

templates = Jinja2Templates(directory = "app/htmls")        #'htmls' 디렉토리 내의 html 코드를 참조

last_keyword = ["리그오브레전드", "배틀그라운드", "로스트아크"]

def google_news_crawler(keyword):
    # 구글 뉴스 검색 URL
    url = "https://news.google.com/search?q={}&hl=ko&gl=KR&ceid=KR%3Ako".format(keyword)      # URL 내에 query 변수명을 그대로 입력했더니 'query'라는 문자열을 검색한 결과가 나옴. 전에는 멀쩡했는데 왜 이러는지 모르겠음

    # HTTP 요청 보내기
    response = requests.get(url)

    # HTTP 요청 성공하면 HTML 파싱
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        # 언론사 추출
        all_press = soup.select('div.vr1PYe')
        
        # 제목 추출
        all_title = soup.select('a.JtKRv')
        
        # 날짜 추출
        all_datetime_str = soup.select('div.UOVeFe time.hvbAAd')

        # 링크 추출
        all_link = soup.select('a.JtKRv')

        count = 0   # while문에서 다음 기사로 넘어가기 위해 카운트를 해주는 변수
        while(1):   # 해당 기사가 크롤링이 되지 않을 경우 
            press = all_press[count].text
            
            title = all_title[count].text

            datetime_str = all_datetime_str[count]['datetime']

            # datetime 값을 파싱
            dt = datetime.strptime(datetime_str, '%Y-%m-%dT%H:%M:%SZ')

            # 9시간을 더해 한국 시간으로 변환
            korean_time = dt + timedelta(hours = 9)

            # 분까지만 출력 (strftime으로 포맷)
            formatted_time = korean_time.strftime('%Y-%m-%d %H:%M')

            link = all_link[count]['href']
            link = link.lstrip('.')

            # 본문 링크를 새 변수에 저장
            article_url = "https://news.google.com" + link
            print(article_url)

            # 본문 크롤링을 위해 HTTP 요청 보내기
            response_2 = requests.get(article_url)
            response_2.encoding = 'utf-8'

            # 본문 html을 스크랩하는 과정에서 데이터의 크기를 줄이기 위해 웹사이트에 남아있는 html 주석을 제거하는 함수
            if response_2.status_code == 200:
                soup2 = BeautifulSoup(response_2.text, 'html.parser')
                def remove_comments(soup2):
                    for element in soup(text=lambda text: isinstance(text, Comment)):
                        element.extract()

                remove_comments(soup2)

                # 뉴스 사이트마다 html의 태그가 다르기 때문에 웹사이트에서 자주 사용하는 뉴스 본문 태그를 리스트로
                # 만들어서 본문이 리스트에 입력될 때까지 반복문을 돌리는 것으로 본문의 텍스트를 가져옴
                tag_list = ['#container', '#news-contents' '#wrap', '#news-wrap', '#article-view-content-div', '#content']

                # 기사 전문 추출
                news_main = []
                for i in tag_list:
                    #print(i)   # 확인용
                    if news_main != []:
                        print("입력 성공")
                        break
                    news_main = soup2.select(i)
                #print(news_main)

                if not news_main:
                    count += 1
                    continue
                
                news_main_text = []
                for i in range(len(news_main)):
                    news_main_text.append(news_main[i].get_text(separator = ' ', strip = True).replace("\'", "'"))
                news_detail = news_main_text[0].split('@')[:1]      # 이메일 앞부분이 남음
                final_news_detail = news_detail[0].split('.')[:-1]  # '.'기호를 기준으로 글씨를 싹 잘라서 news_detail의 마지막 인덱스만 제거
                if final_news_detail == []:
                    count += 1
                    continue

                news_detail_text_real_final_last = ""
                news_detail_text_real_final_last = news_detail_text_real_final_last + final_news_detail[i]
                for i in range(1, len(final_news_detail)):
                    news_detail_text_real_final_last = news_detail_text_real_final_last + "." + final_news_detail[i]
                news_detail_text_real_final_last = news_detail_text_real_final_last + "."

                if news_detail_text_real_final_last != "":
                    break

                # 텍스트 확인용 코드
                #print(news_main_text)
                #print(final_news_detail)        # 뉴스 기사 웹사이트를 그대로 크롤링하면 아래의 필요없는 부분까지 출력되는 이슈가 있었는데 보통 뉴스 기사의 끝에는 이메일이 온다는 특징을 이용했다
                #print(news_detail_text_real_final_last)     #'@'기호를 기준으로 문자열을 자르고, 그 앞의 '.'기호를 기준으로 잘라서 이메일을 완전히 제거하는 것으로 깔끔한 본문을 가져옴
            
            
    else:
        print("HTTP 요청 실패")

    return ( press, title, formatted_time, "https://news.google.com"+link, news_detail_text_real_final_last )      


@app.get("/")       # 메인 페이지
def root():
    return {"message":"Hello World"}

@app.get("/search", response_class=HTMLResponse)
def input_keyword(request: Request):
    return templates.TemplateResponse("search.html", {"request": request})

@app.post("/search/result", response_class=HTMLResponse)
def print_news(request: Request, keyword: str = Form(...)):
    print(keyword)
    if not keyword in last_keyword:
        last_keyword.insert(0, keyword)     # 최근 검색어 리스트 맨앞에 keyword 추가
    print(last_keyword)
    press, title, date, link, detail = google_news_crawler(keyword)
    return templates.TemplateResponse("news.html", { "request": request, "keyword": keyword, "press": press, "title": title, "date": date, "link": link, "detail": detail, "last_key1": last_keyword[0], "last_key2": last_keyword[1], "last_key3": last_keyword[2], "last_key4": last_keyword[3] })
# "언론사": press, "제목": title, "작성일자": time, "링크": link



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
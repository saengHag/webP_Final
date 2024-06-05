from typing import Union
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.encoders import jsonable_encoder
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import requests
from datetime import datetime, timedelta
from bs4 import BeautifulSoup, Comment       # 웹에서 가져온 HTML코드를 파이썬에서 편하게 분석해주는 라이브러리
from openai import OpenAI



client = OpenAI()
client
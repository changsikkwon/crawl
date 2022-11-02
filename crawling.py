import requests
import time
import math
import datetime
import random

from bs4 import BeautifulSoup

from selenium import webdriver


USER_AGENT = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64; rv:103.0) Gecko/20100101 Firefox/103.0",
]


class Crawler:
    def __init__(self):
        self.driver = None

    def close(self):
        pass

    def login(self):
        URL = 'https://instagram.com/'

        # mac의 경우 brew를 사용해서 chromedriver 설치 후
        # 해당 경로에서 아래 명령어 실행
        # xattr -d com.apple.quarantine chromedriver
        options = webdriver.ChromeOptions()
        user_agent = random.choice(USER_AGENT)
        options.add_argument('user-agent=' + user_agent)
        options.add_argument("--proxy-server=socks5://127.0.0.1:9150")

        # self.driver = webdriver.Chrome(executable_path='./chromedriver', options=options)
        self.driver = webdriver.Chrome(executable_path='./chromedriver.exe')

        # 윈도우는 아래 코드 실행
        # self.driver = webdriver.Chrome(executable_path='./chromedriver.exe')
        self.driver.implicitly_wait(3)
        self.driver.get(URL)

    def start(self, instagram_id, artist_id):
        insta_profile_url = f"https://www.instagram.com/{instagram_id}"
        self.driver.get(insta_profile_url)
        time.sleep(3)
        data = self.get_data()
        # 좋아요 크롤링 함수
        # post_list = self.get_post_like(data["postCount"])
        now = datetime.datetime.now()

        print("수집완료 : Submit API 호출")
        # https://api.artpickhaso.co.kr/v1/artist/instagram_data/submit/
        requests.post(
            "https://api.artpickhaso.co.kr/v1/artist/instagram_data/submit/",
            data={
                "artist": artist_id,
                "targetDate": now.strftime("%Y-%m-%d"),
                "followerCount": data["followerCount"],
                "postCount": data["postCount"],
                "likeCount": 0,
                # "postCount": post_list["postCount"],
                # "likeCount": post_list["likeCount"],
            }
        )

    # 게시물, 팔로워 데이터 가져오기
    def get_data(self):
        page_source = self.driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        result = []
        for element in soup.select('main header section li'):
            value = element.get_text().split(' ')[1].replace(',', '')
            if "K" in value:
                result.append(float(value.replace('K', '')) * 1000)
            elif "M" in value:
                result.append(float(value.replace('M', '')) * 1000000)
            else:
                result.append(int(value))
        print(f"result : {result}")
        return {
            "postCount": result[0],
            "followerCount": result[1],
        }

    # 게시글 좋아요 가져오기
    def get_post_like(self, count):
        # 12개씩 불러옴
        for i in range(math.ceil(count/12) + 1):
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(0.2)

        time.sleep(0.5)
        page_source = self.driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')

        posts = soup.select('article a')
        # 좋아요 크롤링 로직
        post_like_count = 0
        for element in posts:
            link = f"https://www.instagram.com{element['href']}"
            self.driver.get(link)
            time.sleep(random.random() + 1)
            self.driver.execute_script(f"window.scrollTo(0, {random.randrange(200, 400)});")
            time.sleep(random.random() + random.randrange(4, 10))
            like_value = self.get_like()
            post_like_count += like_value
        return {
            "postCount": len(posts),
            "likeCount": post_like_count
        }

    def get_like(self):
        while True:
            source = self.driver.page_source
            soup = BeautifulSoup(source, 'html.parser')
            like = soup.select('article div section a')
            if len(like) > 0:
                value = int(like[0].get_text().split(' ')[1].rstrip("개"))
                return value
            else:
                print("크롤링 실패! 재시도..")
                time.sleep(0.5)

# eigheivheoshci
# rlarjsgh6230
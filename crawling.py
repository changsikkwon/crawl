import datetime
import math
import random
import time

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

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
        URL = "https://instagram.com/"

        self.driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))

        self.driver.implicitly_wait(3)
        self.driver.get(URL)
        self.driver.implicitly_wait(10)

        self.driver.implicitly_wait(10)

    def start(self, instagram_id, artist_id):
        insta_profile_url = f"https://www.instagram.com/{instagram_id}"
        self.driver.get(insta_profile_url)
        self.driver.implicitly_wait(30)
        data = self.get_data()
        self.driver.implicitly_wait(30)
        # 좋아요 크롤링 함수
        # post_list = self.get_post_like(data["postCount"])
        now = datetime.datetime.now()

        # print("수집완료 : Submit API 호출")
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
            },
        )
        self.driver.implicitly_wait(30)

    # 게시물, 팔로워 데이터 가져오기
    def get_data(self):
        result = []
        for i in self.driver.find_elements(by=By.CLASS_NAME, value="_ac2a"):
            text = i.text.replace(",", "")
            if "백만" in i.text:
                text = int(i.text.replace("백만", "")) * 1000000
            elif "십만" in i.text:
                text = int(i.text.replace("십만", "")) * 100000
            elif "만" in i.text:
                text = int(i.text.replace("만", "")) * 10000
            elif "K" in i.text:
                text = int(i.text.replace("K", "")) * 1000
            elif "M" in i.text:
                text = int(i.text.replace("M", "")) * 1000000

            result.append(int(text))

        print(f"result : {result}")
        return {
            "postCount": result[0],
            "followerCount": result[1],
        }

    # 게시글 좋아요 가져오기
    def get_post_like(self, count):
        # 12개씩 불러옴
        for i in range(math.ceil(count / 12) + 1):
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(0.2)

        time.sleep(0.5)
        page_source = self.driver.page_source
        soup = BeautifulSoup(page_source, "html.parser")

        posts = soup.select("article a")
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
        return {"postCount": len(posts), "likeCount": post_like_count}

    def get_like(self):
        while True:
            source = self.driver.page_source
            soup = BeautifulSoup(source, "html.parser")
            like = soup.select("article div section a")
            if len(like) > 0:
                value = int(like[0].get_text().split(" ")[1].rstrip("개"))
                return value
            else:
                print("크롤링 실패! 재시도..")
                time.sleep(0.5)

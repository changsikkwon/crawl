import tkinter as tk
from tkinter import ttk
from crawling import Crawler
import requests


crawler = Crawler()
window = tk.Tk()
window.title("아트픽하소")
window.geometry("640x400")
window.resizable(False, False)


frm = ttk.Frame(window, padding=10)
frm.pack()

show = tk.Label(frm, text="작가를 선택해주세요", font=("Arial", 20), padx=10, pady=10)
show.pack()

artists = requests.get("https://api.artpickhaso.co.kr/v1/artist/").json()

listbox = tk.Listbox(frm, width=100, height=10, selectmode=tk.EXTENDED)
listbox.pack(padx=10, pady=10, expand=tk.YES, fill="both")

for i in artists:
    listbox.insert(tk.END, f'ID : {i["id"]}   -   작가명 : {i["korean_name"]}   -   인스타계정 : {i["instagram_id"]}')


def login():
    crawler.login()


def select_all():
    listbox.select_set(0, tk.END)


def start_crawling():
    selected = []
    cname = listbox.curselection()

    for item in cname:
        op = listbox.get(item)
        selected.append(op)
    for val in selected:
        artist_id = val.split("   -   ")[0].split(" : ")[1]
        # artist_name = val.split("   -   ")[1].split(" : ")[1]
        instagram_id = val.split("   -   ")[2].split(" : ")[1]
        print(f"artist_id : {artist_id}")
        print(f"instagram_id : {instagram_id}")
        try:
            crawler.start(instagram_id, artist_id)
            # lable1.pack_forget()
        except:
            pass


# widget.pack()
select_all_btn = ttk.Button(frm, text="전체 선택", width=20, command=select_all)
select_all_btn.pack()
login_btn = ttk.Button(frm, text="인스타 로그인", width=20, command=login)
login_btn.pack()
start_crawling_btn = ttk.Button(frm, text="크롤링 실행", width=20, command=start_crawling)
start_crawling_btn.pack()


window.mainloop()


# https://api.artpickhaso.co.kr/v1/artist/
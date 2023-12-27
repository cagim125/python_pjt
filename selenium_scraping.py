from selenium import webdriver
from bs4 import BeautifulSoup
import re
import pymysql.cursors
import time

### DB Connection ###
conn = pymysql.connect(host="127.0.0.1", port=3306, user="root", password="1234", db="data", charset="utf8")
date = time.strftime("%Y%m%d", time.localtime())

## 셀레니움 스크래핑 기본정보 ##
option = webdriver.ChromeOptions()
option.headless = True
option.add_argument('window-size=1920,1080')
option.add_argument('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Safari/537.36')
browser = webdriver.Chrome()
browser.maximize_window()

# 퀘이사존 스크래핑 함수 제작
def quasarzone(url):
    # 데이터 가공
    browser.get(url)
    soup = BeautifulSoup(browser.page_source, "lxml")
    # 필요한 데이터 가져오기. 원하는 데이터가 모두 포함된 가장 적절한 태그는 tr 이다.
    # 그 위의 <tbody>를 하지 않는 이유는, 데이터가 리스트화되지 않고 한개의 뭉텅이가 되어서 스크래핑시 하나밖에 못가져온다.
    datas = soup.find_all("tr")
    # print(datas)
    # 스크래핑 시작
    for data in datas:
        # 각 데이터에 대한 변수 선언
        dealTitle = data.find("a", attrs={"class": "subject-link"})  # 제목
        dealLink = data.find("a", attrs={"class": "subject-link"})  # 글링크
        dealDate = data.find("span", attrs={"class": "date"})  # 날짜
        # dealprice = data.find("span", attrs={"class": "text-orange"}) # 가격
        dealBlind = data.find("i", attrs={"class": "fa fa-lock"})  # 블라인드 처리된 글

        # 전체 데이터 중 None이 발생할 수 있어 None을 제거함
        if dealTitle is not None:

            # 각 게시물 중 "블라인드 처리된 글입니다." 라는 글이 있는데, 해당 글은 제외함
            if dealBlind:
                # 즉, dealBlind가 있다면 아무것도 안하고 그냥 넘어감.
                continue

            finalDealTitle = dealTitle.text.strip()
            finalDealLink = "https://quasarzone.com/" + dealLink["href"]
            finalDealDate = dealDate.text.strip()
            # finalDealPrice = dealprice.text.strip()

            print(finalDealTitle)
            print(finalDealLink)
            print(finalDealDate)
            # print(finalDealPrice)

            with conn.cursor() as curs:
                sql = "insert into product_data(title, link, date, source) values(%s, %s, %s, %s)"
                curs.execute(sql, (finalDealTitle, finalDealLink, finalDealDate, 'quasarzone'))

                conn.commit()


    conn.close()


def fmkorea(url):
    browser.get(url)
    soup = BeautifulSoup(browser.page_source, 'lxml')
    datas = soup.find_all("tr")

    # 스크래핑 시작
    for data in datas:
        # 각 데이터에 대한 변수 선언
        dealTitle = data.find("td", attrs={"class": "title hotdeal_var8"})  # 제목
        # 참고로, 에펨코리아는 품절된 제품은 아예 제목의 클래스를 바꿔버리므로 품절된 제품은 아예 검색에서 빠진다. 편하네. (품절제품 클래스명 : hotdeal_var8Y)
        dealLink = data.find("a", attrs={"class": "hx"})  # 글링크
        dealDate = data.find("td", attrs={"class": "time"})  # 날짜

        # 데이터 중 None 이 있다면 None 부분은 skip 하도록 함.
        if dealTitle is not None:
            finalDealTitle = dealTitle.find("a").text.strip().replace("(무료)", "").replace("(0원)", "")
            finalDealLink = "https://www.fmkorea.com/" + dealLink["href"]
            finalDealDate = dealDate.text.strip()

            print(finalDealTitle)  # 배송비 (무료), (0원) 부분은 없어도 되므로 제거함.
            print(finalDealLink)
            print(finalDealDate)

# 당일이면 시간, 당일이 아니면 날짜로 가져온다.
def extractDate(a):
    if ":" in a:
        return a[0:5]
    else:
        if len(a) > 6:
            ## 섹션1 : (\d{4}|\d{2}) 중간값 :
            ## (\d{4}|\d{2})[\/|.|-](\d{2})[\/|.|-](\d{2})
            date = re.findall('(\d{4}|\d{2})[\/|.|-](\d{2})[\/|.|-](\d{2})')
            parseddate = "+" + date[0][1] + "-" + date[0][2]
            return parseddate
        else:
            return "+" + a

# 페이지별 스크래핑
addr1 = "https://quasarzone.com/bbs/qb_saleinfo?page=1"
# addr2 = "https://quasarzone.com/bbs/qb_saleinfo?page=2"
quasarzone(addr1)
# quasarzone(addr2)
# curs.close()
# address1 = "https://www.fmkorea.com/index.php?mid=hotdeal&listStyle=list&page=1"
# fmkorea(address1)
# addr = "https://store.kakao.com/home/best"
# kakao(addr)


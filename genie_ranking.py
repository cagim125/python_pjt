import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient

######DB Connection #########
client = MongoClient('localhost', 27017)
db = client.geniemusic


headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
music_data = requests.get('https://www.genie.co.kr/chart/top200?ditc=D&rtm=N&ymd=20200713', headers=headers)
soupped_data = BeautifulSoup(music_data.text, 'html.parser')
music_list = soupped_data.select('#body-content > div.newest-list > div > table > tbody > tr')

db.chart_ranking.delete_many({})

print(music_list)

# 데이터 추출
for music in music_list:
    rank = music.select_one('td.number').text[0:2].strip()
    title = music.select_one('td.info > a.title.ellipsis').text.strip()
    artist = music.select_one('td.info > a.artist.ellipsis').text.strip()
    print(rank,"|", title, "|" ,artist)
#
#     db.chart_ranking.insert_one({'rank': rank, 'title': title, 'artist': artist})
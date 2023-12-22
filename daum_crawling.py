import requests
from  bs4 import BeautifulSoup
from pymongo import MongoClient

client = MongoClient('localhost', 27017)
db = client.daum_movie

daum_url = 'https://movie.daum.net/ranking/reservation'

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
data = requests.get(daum_url, headers=headers)
soup = BeautifulSoup(data.text, 'html.parser')


daum_movie = list(soup.select("#mainContent > div > div.box_ranking > ol.list_movieranking > li "))
# print(daum_movie)


for movie in daum_movie:
    movie_title = movie.select_one("div.thumb_cont > strong > a").text
    movie_image = movie.select_one("div.poster_movie > img")['src']
    movie_year = movie.select_one("span.txt_info > span").text
    movie_url = movie.select_one("div > div.thumb_item > div.poster_info > a")['href']

    doc ={
        "title": movie_title,
        "year": movie_year,
        "image": movie_image,
        "url": movie_url,
        "like": 0
    }

    db.movie.insert_one(doc)

    # print(movie_title, movie_image, movie_year, movie_url)

import requests
from  bs4 import BeautifulSoup
from pymongo import MongoClient

client = MongoClient('localhost', 27017)
db = client.movieDB

base_url = 'https://movie.daum.net'

def get_urls():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
    data = requests.get(base_url, headers=headers)
    soup = BeautifulSoup(data.text, 'html.parser')
    rank_url = soup.select_one('#gnbContent > ul > li.ranking > a')['href']
    rank_url = base_url + rank_url
    # print(rank_urls)
    return rank_url

def insert_movie(rank_url):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
    data = requests.get(rank_url, headers=headers)
    soup = BeautifulSoup(data.text, 'html.parser')

    movie_rank = list(soup.select("#mainContent > div > div.box_ranking > ol.list_movieranking > li "))
    # print(daum_movie)


    for movie in movie_rank:
        movie_title = movie.select_one("div.thumb_cont > strong > a").text
        movie_image = movie.select_one("div.poster_movie > img")['src']
        movie_year = movie.select_one("span.txt_info > span").text
        movie_url = movie.select_one("div > div.thumb_item > div.poster_info > a")['href']

        doc ={
            "title": movie_title,
            "year": movie_year,
            "image_url": movie_image,
            "url": movie_url,
            "like": 0
        }

        db.movie.insert_one(doc)

        # print(movie_title, movie_image, movie_year, movie_url)
def insert_all():
    db.movies.drop() #movies 컬렉션 초기화
    rank_url = get_urls()
    insert_movie(rank_url)

### 실행하기
insert_all()
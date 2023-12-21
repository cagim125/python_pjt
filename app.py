import requests
from bs4 import BeautifulSoup
from flask import Flask, render_template, jsonify, request
from pymongo import MongoClient

app = Flask(__name__)
DB_HOST = 'localhost:27017'
client = MongoClient(DB_HOST)
db = client.sparta

## HTML을 주는 부분
@app.route('/')
def home(): #함수명수정-이름만보고접속되는페이지를확인할수있게!
    return render_template('index.html')

## API 역할을 하는 부분
@app.route("/memo", methods=['POST'])
def write_memo():
    # 1.클라이언트로부터 데이터 받기
    url_recieve = request.form['url_give'] # url_recieve로 클라이언트가 준 url 가져오기
    comment_recieve = request.form['comment_give'] # comment_recieve로 클라이언트가 준 commnet 가져오기

    # 2.meta tag를 스크래핑하기
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
    data = requests.get(url_recieve, headers=headers)
    soup = BeautifulSoup(data.text, 'html.parser')

    og_image = soup.select_one('meta[property="og:image"]')
    og_title = soup.select_one('meta[property="og:title"]')
    og_description = soup.select_one('meta[property="og:description"]')

    url_image = og_image['content']
    url_title = og_title['content']
    url_description = og_description['content']

    article = {
        'url': url_recieve,
        'title': url_title,
        'desc': url_description,
        'image': url_image,
        'comment': comment_recieve
    }
    print(article)
    # 3. mongoDB에 데이터 넣기
    db.articles.insert_one(article)

    return jsonify({'result': 'success'})

@app.route('/memo', methods=['GET'])
def get_memo():
    # 1.mongoDB에서 _id 값을 제외한 모든 데이터 조회해오기 (Read)
    result = list(db.articles.find({}, {'_id':0}))
    # 2. article라는 키 값으로 article 정보 보내주기
    return jsonify({'result':'success', 'article': result})

@app.route('/review', methods=['POST'])
def write_review():
    # title_recieve로 클라이언트가 준 title 가져오기
    title_recieve = request.form['title_give']
    # author_recieve로 클라이언트가 준 author 가져오기
    author_recieve = request.form['author_give']
    # review_recieve 로 클라이언트가 준 review 가져오기
    review_recieve = request.form['review_give']

    # DB에 삽입할 review 만들기
    # DB에 데이터를 삽입하려면 딕셔너리 형태로 만들어야 함
    review = {
        'title': title_recieve,
        'author': author_recieve,
        'review': review_recieve
    }
    # reviws에 review 저장하기
    db.book_reviews.insert_one(review)
    return jsonify({'result': 'success', 'msg': '리뷰가 성공적으로 작성되었습니다.'})

@app.route('/review', methods=['GET'])
def read_review():
    reviews = list(db.book_reviews.find({},{'_id': 0}))
    # print(reviews)
    if reviews is not None:
        return jsonify({'result': 'success', 'reviews': reviews})

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
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
##여기접속하고get방식일때,아래함수를작동해라.
@app.route('/review', methods=['POST'])
def write_review():
    # title_recieve로 클라언트가 준 title 가져오기
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
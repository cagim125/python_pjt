import requests
from bs4 import BeautifulSoup
from flask import Flask, render_template, jsonify, request
import pymysql
import lxml

app = Flask(__name__)
### DB Connection ###
conn = pymysql.connect(host="127.0.0.1", port=3306, user="root", password="1234", db="data", charset="utf8")

# daum_url = "https://movie.daum.net/ranking/reservation"

## HTML을 주는 부분
@app.route('/')
def home(): #함수명수정-이름만보고접속되는페이지를확인할수있게!
    return render_template('index.html')

@app.route('/get_spdb')
def get_spdb():
    # cursor() 생성
    curs = conn.cursor()
    # product_data 테이블에서 모든 데이터를 가져온다, date 기준 내림차순으로 정렬한다.

    removeDuptitle = "DELETE a FROM product_data a, product_data b WHERE a.id > b.id AND a.title = b.title;"
    curs.execute(removeDuptitle)
    removeDupLink = "DELETE a FROM product_data a, product_data b WHERE a.id > b.id AND a.link = b.link;"
    curs.execute(removeDupLink)
    removeShortTitle = "DELETE from product_data where char_length(title) <= 8;"
    curs.execute(removeShortTitle)
    conn.commit()
    # sql 문 실행
    sql = "SELECT * FROM product_data ORDER BY date DESC"
    curs.execute(sql)
    # 데이터 가져오기
    datas = list(curs.fetchall())
    # DB 접속 종료

        # 최종 결과물을 담을 리스트 변수를 선언한다.
    result = []

        # DB 검색 결과를 딕셔너리 형태로 재생성한다.
    for data in datas:
        parsed_data = {'id': data[0], 'title': data[1], 'link': data[2], 'source': data[3], 'date': data[4],
                           'thumbnail': data[5]}
        result.append(parsed_data)


    return jsonify({'result': 'success', 'product_data': result})

@app.route('/api/list', methods=['GET'])
def api_list():

    # {} : DB에 있는 값을 다 가지고 오라는 뜻
    # {'_id':False} : _id컬럼은 가지고 오지 않는다
    # .sort('like',-1) : 1 : 오름차순, -1 : 내림차순
    movie = list(db.movie.find({},{'_id':False}).sort('like',-1))
    return jsonify({'result':'success','data': movie})

@app.route('/api/like', methods=['POST'])
def like_up():
    # 1. 클라이언트가 전달한 name_give를 name_receive 변수에 넣습니다.
    title_receive = request.form['title_give']
    # 2. mystar 목록에서 find_one으로 name이 name_receive와 일치하는 star를 찾습니다.
    star = db.movie.find_one({'title': title_receive})
    # 3. star의 like 에 1을 더해준 new_like 변수를 만듭니다.
    new_like = star['like'] + 1
    # 4. mystar 목록에서 name이 name_receive인 문서의 like 를 new_like로 변경합니다.
    # 참고: '$set' 활용하기!
    db.movie.update_one({'title': title_receive}, {'$set': {'like': new_like}})
    # 5. 성공하면 success 메시지를 반환합니다. 성공했따는것을 알려주기 위함.
    return jsonify({'result': 'success'})

@app.route("/order", methods=['POST'])
def write_order():
    # 1.클라이언트로 부터 넘어온 데이터 받기
    name_receive = request.form["name_give"]
    addr_receive = request.form["addr_give"]
    phone_receive = request.form["phone_give"]
    # count_receive = request.form["count_give"]

    order = {
        "name": name_receive,
        "address": addr_receive,
        "phone": phone_receive,
        # "count": count_receive
    }
    db.orders.insert_one(order)

    return jsonify({'result': 'success', 'msg': '주문이 정상적으로 완료되었습니다.'})
@app.route("/order", methods=['GET'])
def get_orders():
    order_list = list(db.orders.find({},{'_id': 0}))
    return jsonify({'result': 'success', 'data': order_list})
## API 역할을 하는 부분
@app.route("/memo", methods=['POST'])
def write_memo():
    # 1.클라이언트로부터 데이터 받기
    url_receive = request.form['url_give'] # url_recieve로 클라이언트가 준 url 가져오기
    comment_receive = request.form['comment_give'] # comment_recieve로 클라이언트가 준 commnet 가져오기

    # 2.meta tag를 스크래핑하기
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
    data = requests.get(url_receive, headers=headers)
    soup = BeautifulSoup(data.text, 'html.parser')

    og_image = soup.select_one('meta[property="og:image"]')
    og_title = soup.select_one('meta[property="og:title"]')
    og_description = soup.select_one('meta[property="og:description"]')

    url_image = og_image['content']
    url_title = og_title['content']
    url_description = og_description['content']

    article = {
        'url': url_receive,
        'title': url_title,
        'desc': url_description,
        'image': url_image,
        'comment': comment_receive
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
    conn.close()
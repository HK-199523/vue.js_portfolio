from flask import Flask,render_template,request,session,redirect,jsonify,current_app,g
import sqlite3
import json
from datetime import datetime

from sqlalchemy import create_engine,Column,Integer,String,Text,DateTime,ForeignKey, engine
from sqlalchemy.ext import declarative
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker,relationship
from sqlalchemy.orm.session import Session
import datetime
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.sql.sqltypes import DATETIME, INTEGER, TEXT
#下記QRコード関係
import qrcode as qr
from PIL import Image
import base64
from io import BytesIO

app = Flask(__name__)
app.secret_key = b'HirokiKondo'

engine = create_engine('sqlite:///selfwebsite.sqlite3')

Base = declarative_base()


#ここからテーブルごとにモデルインスタンス
class Book(Base):
    __tablename__ = 'book'
    id = Column(Integer(),primary_key=True)
    b_n = Column(Text())
    ca = Column(Text())
    book_pic_ad = Column(Text())
    page = Column(Integer())
    impre = Column(Text())
    create =Column(DateTime())
    la_id =Column(Integer(),ForeignKey('la_na.id'))

    language = relationship('Language')

    def to_dict(self):
        return{
            'id':int(self.id),
            'b_n':str(self.b_n),
            'ca':str(self.ca),
            'book_pic_ad':str(self.book_pic_ad),
            'page':int(self.page),
            'impre':str(self.impre),
            'create':str(self.create),
            'la_id':int(self.la_id),
            'language':str(self.language.pr_la)
        }

class Error(Base):
    __tablename__ = 'error'
    id = Column(Integer(),primary_key=True)
    la_id = Column(Integer(),ForeignKey('la_na.id'))
    err_na = Column(Text())
    err_body = Column(Text())
    err_de = Column(Text())
    created = Column(DateTime())

    language = relationship('Language')

    def to_dict(self):
        return{
            'id':int(self.id),
            'la_id':int(self.la_id),
            'err_na':str(self.err_na),
            'err_body':str(self.err_body),
            'err_de':str(self.err_de),
            'created':str(self.created),
            'language':str(self.language.pr_la)
        }


class Language(Base):
    __tablename__ = 'la_na'
    id = Column(Integer(),primary_key=True)
    pr_la = Column(Text())

    def to_dict(self):
        return{
            'id':int(self.id),
            'pr_la':str(self.pr_la)
        }


class ProgTech(Base):
    __tablename__ = 'prog_tech'
    id = Column(INTEGER,primary_key=True)
    la_id = Column(Integer,ForeignKey('la_na.id'))
    bo_id = Column(Integer,ForeignKey('book.id'))
    la_na = Column(Text())
    le_level = Column(Integer)
    la_code = Column(Text())
    explain = Column(Text())
    created = Column(DateTime())

    book = relationship('Book')
    language = relationship('Language')

    def to_dict(self):
        return{
            'id':int(self.id),
            'la_id':int(self.la_id),
            'bo_id':int(self.bo_id),
            'la_na':str(self.la_na),
            'le_level':int(self.le_level),
            'la_code':str(self.la_code),
            'explain':str(self.explain),
            'created':str(self.created),
            'language':str(self.language.pr_la),
            'book':str(self.book.b_n)
        }
#ここまで

#ここで言語ごとにレコードを取得
def get_sepa_data(list):
    data_list = ["HTML","CSS","bootstrap","javascript","Vue.js","python","Anaconda","openCV","SQLalchemy","その他","アルゴリズム関係"]
    Session = sessionmaker(bind=engine)
    ses = Session()
    for num in range(1,12):
        if(num >= 11):
            y = data_list[10]
            num = 11 + 1
            re1 = ses.query(ProgTech).filter(ProgTech.la_id == num).join(Language).order_by(ProgTech.created.desc())[:20]
            dict_tech = get_by_list(re1)

            re2 = ses.query(Error).filter(Error.la_id == num).join(Language).order_by(Error.created.desc())[:20]
            dict_error = get_by_list(re2)

            x = [y,dict_tech,dict_error]
            list.append(x)
        else:
            z = num -1
            re1 = ses.query(ProgTech).filter(ProgTech.la_id == num).join(Language).order_by(ProgTech.created.desc())[:20]
            dict_tech = get_by_list(re1)

            re2 = ses.query(Error).filter(Error.la_id == num).join(Language).order_by(Error.created.desc())[:20]
            dict_error = get_by_list(re2)

            x = [data_list[z],dict_tech,dict_error]
            list.append(x)

    return


def get_by_list(arr):
    res = []
    for item in arr:
        res.append(item.to_dict())
    return res

@app.route('/',methods=['GET']) #URLの後の数字を基に下記のrender_templateの値を返す。
def index():
    return render_template('top_content.html',
                            title='CHACON',
                            )
'''
@app.route('/book',methods=['GET']) #URLの後の数字を基に下記のrender_templateの値を返す。
def index():
    return render_template('book.html',
                            title='CHACON',
                            )
'''

@app.route('/get_list',methods=['POST'])
def get_data_book():
    Session = sessionmaker(bind=engine)
    ses = Session()
    re1 = ses.query(Book).join(Language).all()
    all_booK = get_by_list(re1)

    re2 = ses.query(Book).filter(Book.ca == '小説').join(Language).order_by(Book.create.desc())[:20]
    novel = get_by_list(re2)

    re3 = ses.query(Book).filter(Book.ca == 'IT参考書').join(Language).order_by(Book.create.desc())[:20]
    it_book = get_by_list(re3)

    re4 = ses.query(Book).filter(Book.ca == 'その他').join(Language).order_by(Book.create.desc())[:20]
    etc_booK = get_by_list(re4)

    book_list = [all_booK,novel,it_book,etc_booK]

    return jsonify(book_list)



@app.route('/book_detil',methods=['POST'])
def get_record():
    id = request.form.get('id')
    Session = sessionmaker(bind=engine)
    ses = Session()
    re = ses.query(Book).filter(Book.id == id).one()
    record = re.to_dict()
    return jsonify(record)

@app.route('/tech_detil',methods=['POST'])
def get_record_tech():
    id = request.form.get('id')
    Session = sessionmaker(bind=engine)
    ses = Session()
    re = ses.query(ProgTech).filter(ProgTech.id == id).one()
    record = re.to_dict()
    return jsonify(record)

@app.route('/error_detil',methods=['POST'])
def get_record_error():
    id = request.form.get('id')
    Session = sessionmaker(bind=engine)
    ses = Session()
    re = ses.query(Error).filter(Error.id == id).one()
    record = re.to_dict()
    return jsonify(record)



@app.route('/get_list_prog',methods=['POST'])
def get_data_prog():
    sepa_prog_list = []
    get_sepa_data(sepa_prog_list)

    Session = sessionmaker(bind=engine)
    ses = Session()
    re3 = ses.query(ProgTech).join(Language).all()
    dict_tech1 = get_by_list(re3)
    re4 = ses.query(Error).join(Language).all()
    dict_error1 = get_by_list(re4)
    all_prog_info = [dict_tech1,dict_error1]

    prog_list = [sepa_prog_list,all_prog_info]
    return jsonify(prog_list)



@app.route('/post_book',methods=["POST"])
def get_msg_book():
    book_name = request.form.get('b_n')
    book_category  = request.form.get('ca')
    la_id = request.form.get('la_id')
    book_pic  = request.form.get('book_pic_ad')
    book_page = request.form.get('page')
    book_impre = request.form.get('impre')
    create = datetime.date.today()
    Session = sessionmaker(bind=engine)
    ses = Session()
    book_obj = Book(b_n=book_name,
                    ca=book_category,
                    book_pic_ad=book_pic,
                    la_id=la_id,
                    page=book_page,
                    impre=book_impre,
                    create=create)
    ses.add(book_obj)
    ses.commit()
    ses.close()
    return 'True'

@app.route('/post_tech',methods=["POST"])
def get_msg_tech():
    la_id = request.form.get('la_id')
    bo_id  = request.form.get('bo_id')
    la_na  = request.form.get('la_na')
    le_level = request.form.get('le_level')
    la_code = request.form.get('la_code')
    explain = request.form.get('explain')
    created = datetime.date.today()
    Session = sessionmaker(bind=engine)
    ses = Session()
    tech_obj = ProgTech(la_id=la_id,
                        bo_id=bo_id,
                        la_na = la_na,
                        le_level=le_level,
                        la_code=la_code,
                        explain=explain,
                        created=created)
    ses.add(tech_obj)
    ses.commit()
    ses.close()
    return 'True'

@app.route('/post_error',methods=["POST"])
def get_msg_erro():
    la_id = request.form.get('la_id')
    err_na  = request.form.get('err_na')
    err_body  = request.form.get('err_body')
    err_de = request.form.get('err_de')
    created = datetime.date.today()
    Session = sessionmaker(bind=engine)
    ses = Session()
    error_obj = Error(la_id=la_id,
                        err_na=err_na,
                        err_body = err_body,
                        err_de=err_de,
                        created=created)
    ses.add(error_obj)
    ses.commit()
    ses.close()
    return 'True'

if __name__=='__main__':
    app.debug = True
    app.run(host='localhost')
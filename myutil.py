#!python3.9.1
#from flask import Flask, session
    #redirect, jsonify, current_app, g
#import psycopg2
from socket import NI_MAXHOST
import openpyxl # 外部ライブラリ　pip install openpyxl
import sqlite3
#import json
from datetime import datetime
import datetime
import pprint
import pytz
import os
import pathlib

from sqlalchemy import create_engine, Column, Integer, String, \
    Text, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.orm.exc import NoResultFound


#　↓　herokuのpostgreSQL接続用URI 
# ※ただし、割り当てられたURIそのままでは接続エラー
#　「postgres://・・・」から「postgresql://・・・」に変更しなければ解消されない
#参考（heroku公式リファレンス）⇒Why is SQLAlchemy 1.4.x not connecting to Heroku Postgres? - Heroku Help
###engine = create_engine('postgresql://gnxzzavntcwtpn:2d7224a390d7ea18712db3c0d3d5a676b8255452aae23bd2dd920c4a95da2a37@ec2-52-3-2-245.compute-1.amazonaws.com:5432/dib5jng6kbpqr')

#　↓　ローカルのSQLite接続用パス 
# パスの書き方は、参照⇒https://yasumonoe.hateblo.jp/entry/2018/09/07/220742
engine = create_engine('sqlite:///treasurehuntdb.sqlite3')

# base model
Base=declarative_base()


# ①タイムゾーン付きの時刻は、タイムゾーンのついていない時刻との加算・減算ができない。
# ②このタイムゾーン付きの時刻を、データベースに記録した場合、データ型が自動的にdatetime型からstr型に変換される。
# ③そうすると、残念ながら「タイムゾーンの情報」は削除されるらしい。
# ④さらに、データベースから取り出すときにデータ型を変更する（str型⇒datetime型）必要がある。参照⇒https://note.nkmk.me/python-datetime-isoformat-fromisoformat/
# ⑤データ型をうまくdatetime型に変更できたとしても、①の制約のため、計算ができない。計算相手もタイムゾーン付きのdatetime型に、そろえる必要がある。

# 対策
# ①データベースのSQLにて「time_stamp」値のdatetime属性をstr属性に変更（myutil.pyにて）
# ②タイムゾーン付きの時刻データを、datetime型からstr型に変換（.isoformat()メソッドを使用）
# ③データベースから取り出した時刻データを、str型からdatetime型に変換（datetime.datetime.fromisoformat()関数を使用）

#model classes
class Mydata(Base):
    __tablename__='mydata'
    input_id=Column(Integer,primary_key=True, autoincrement=True)
    #user_id=Column(Integer),ForeignKey('userid.user_id')
    user_id=Column(Integer)
    group=Column(String(255))
    name=Column(String(255))
    input_key=Column(String(255))
    current_stage=Column(String(255))
    time_stamp=Column(String(255))
  

    # get Dict data
    def to_dict(self):
        return{
            'input_id':int(self.input_id),
            'user_id':int(self.user_id),
            'group':str(self.group),
            'name':str(self.name),
            'input_key':str(self.input_key),
            'current_stage':str(self.current_stage),
            'time_stamp':str(self.time_stamp)

        }
    # def update_dictの説明
    # Culdulateモデルクラスのインスタンスに辞書をぶっこんでテーブルへ
    # 　一括更新するためのメソッドをあらかじめ用意しておく。
    # 参考　http://motomizuki.github.io/blog/2015/05/20/sqlalchemy_update_20150520/
   
    # ↑　のとおりにやると、エラーが出る
    # 【1】__dict__という特殊メソッドは、使用を推奨されないので、わざわざkeyListというリストに、
    # 　「属性」【オブジェクトの変数・・・例）このテーブルのクラスオブジェクトの場合、name = Column(String(255))
    #   の左辺の「name」など】をリスト形式にして保管しておく
    # 【2】setattr()という関数は　右を参照　https://techacademy.jp/magazine/28372
    
    # それでも　↓　下記のようなエラーが出る
    #   typeError: update_dict() takes 1 positional argument but 2 were givenというエラー　
    #   なので、右を参考に　https://teratail.com/questions/27380
    #   def update_dict(dict): を修正して⇒　def update_dict(self,dict):　としたら動いた
    def update_dict(self,dict):
        keyList=[ 
            'input_id',\
            'user_id',\
            'group',\
            'name',\
            'input_key',\
            'current_stage',\
            'time_stamp']
        for key1, value in dict.items():
            if key1 in keyList:
                setattr(self, key1, value)

class Userid(Base):
    __tablename__='userid'

    user_id=Column(Integer,primary_key=True, autoincrement=True)
    group=Column(String(255))
    name=Column(String(255))
    st1_finish_timestamp=Column(String(255))
    st2_finish_timestamp=Column(String(255))
    st3_finish_timestamp=Column(String(255))
    st4_finish_timestamp=Column(String(255))
    st5_finish_timestamp=Column(String(255))
    st6_finish_timestamp=Column(String(255))

 

    # get Dict data
    def to_dict(self):
        return{
            'user_id':int(self.user_id),
            'group':str(self.group),
            'name':str(self.name),
            'st1_finish_timestamp':str(self.st1_finish_timestamp),
            'st2_finish_timestamp':str(self.st2_finish_timestamp),
            'st3_finish_timestamp':str(self.st3_finish_timestamp),
            'st4_finish_timestamp':str(self.st4_finish_timestamp),
            'st5_finish_timestamp':str(self.st5_finish_timestamp),
            'st6_finish_timestamp':str(self.st6_finish_timestamp),

        }
    def update_dict(self,dict):
        keyList=[ 
            'user_id',\
            'group',\
            'name',\
            'st1_finish_timestamp',\
            'st2_finish_timestamp',\
            'st3_finish_timestamp',\
            'st4_finish_timestamp',\
            'st5_finish_timestamp',\
            'st6_finish_timestamp']
        for key1, value in dict.items():
            if key1 in keyList:
                setattr(self, key1, value)

class Stage_key(Base):
    __tablename__='stage_key'
    stage=Column(Integer,primary_key=True)
    key=Column(String(255))
    
  

    # get Dict data
    def to_dict(self):
        return{
            'stage':int(self.stage),
            'key':str(self.key)
        }



def get_data_test():
    Session = sessionmaker(bind=engine)
    ses = Session()
    mydata = ses.query(Mydata).all()
    mydata = get_by_list(mydata)
    #pprint.pprint('mydata.myutil={}'.format(mydata))
    ses.close()# 終わったら必ずセッションを閉じておかないと、SQLalchemy内でのエラーが出る（それでも動作は完遂してくれるが）
    return mydata

def get_data_from_table_object(gr_st,nm,tbnm):
    Session = sessionmaker(bind=engine)
    ses = Session()
    #pprint.pprint('group_name,name.myutil={}'.format(gr+','+nm))
    if tbnm=='userid':
        try:
            user_datum = ses.query(Userid).filter(Userid.group==gr_st , Userid.name==nm).one()
            # mydata テーブルのデータが、groupごとにセレクトできるようになっていない⇒要改良
            res = user_datum.to_dict()
        except NoResultFound:
            res = False
    elif tbnm=='mydata':
        if gr_st=='admin':
            try:
                user_group_data = ses.query(Mydata).all()
                res = get_by_list(user_group_data)
            except NoResultFound:
                res = False
        else:
            try:
                user_group_data = ses.query(Mydata).filter(Mydata.group==gr_st ).all()
                res = get_by_list(user_group_data)
            except NoResultFound:
                res = False
    elif tbnm=='stage_key':
        try:
            stage_key_datum = ses.query(Stage_key).filter(Stage_key.stage==gr_st ).one()
            res = stage_key_datum.to_dict()
        except NoResultFound:
            res = False
    
    #pprint.pprint('res.myutil={}'.format(res))
    
    ses.close()# 終わったら必ずセッションを閉じておかないと、SQLalchemy内でのエラーが出る（それでも動作は完遂してくれるが）
    return res

# ↓　get_by_list()関数にて個々の検索条件を「辞書」に。
# そして複数の辞書をまとめて、リスト化する。
def get_by_list(arr):
    res = []
    for item in arr:
        res.append(item.to_dict())
    return res 

#Userid テーブルから、user_idに一致するレコードを取り、辞書形式で返す関数
def get_data_from_user_table(user_id):
    Session = sessionmaker(bind=engine)
    ses = Session()
    user_datum = ses.query(Userid).filter(Userid.user_id==user_id).one()
    # mydata テーブルのデータが、groupごとにセレクトできるようになっていない⇒要改良
    res = user_datum.to_dict()    
    ses.close()# 終わったら必ずセッションを閉じておかないと、SQLalchemy内でのエラーが出る（それでも動作は完遂してくれるが）
    return res

# フォームで入力された内容を、Mydataテーブルに更新するプロシージャ
#　user_idをもとに、Useridテーブルからいちいちgroup,nameを調べ上げてMydata
#  に、入力している
def post_msg_to_sql(user_id,msg,str_timestamp,stage,seikai_flg):
    user_datum = get_data_from_user_table(user_id)
    group=user_datum['group']
    name=user_datum['name']
    
    dict_msg={}
    dict_msg['input_key']=msg
    dict_msg['group']=group
    now_timestamp=datetime.datetime.fromisoformat(str_timestamp)
    if seikai_flg=='':
        dict_msg['name']=name+'/'+group+'チーム／クリア🌸'+'／第'+stage+'ステージ／'+str(now_timestamp.hour).zfill(2)+':' \
             + str(now_timestamp.minute).zfill(2) 
    else:
        dict_msg['name']=name+'/'+group+'チーム／ハズレ😞'+'／第'+stage+'ステージ／'+str(now_timestamp.hour).zfill(2)+':' \
             + str(now_timestamp.minute).zfill(2) 

    dict_msg['user_id']=user_id
    dict_msg['time_stamp']=now_timestamp
    dict_msg['current_stage']=stage

    Session = sessionmaker(bind=engine)
    ses = Session()
    MyD_obj = Mydata()
    MyD_obj.update_dict(dict_msg)
    ses.add(MyD_obj)
    ses.commit()
    ses.close()

# フォームで入力された内容が、正解だった時に、
#　useridテーブルに、ステージをクリアした時刻を打刻する。
#  正解した本人だけでなく、その人の所属するグループ全員に打刻する。
#  {クリアしたuser名: ? ,クリアした時刻: ? } という形の、
# 　「辞書」を、文字列に変換した形で、データベースに入れていく
def post_stageClear_timestamp(user_id,stage,str_timestamp):
    user_datum = get_data_from_user_table(user_id)
    group=user_datum['group']
    name=user_datum['name']
    
    dic1={}
    dic1['name']=name
    dic1['time_stamp']=str_timestamp
    
    Session = sessionmaker(bind=engine)
    ses = Session()
    User_objs = ses.query(Userid).filter(Userid.group==group).all()
       
    for user_obj in User_objs :
        # ↓↓　右参照によると　https://shigeblog221.com/python-sqlalchemy-update/
        #  user_obj.st1_finish_timestamp = dic1　と、したいところだが、
        #  引数として渡された　stage 番号を反映させるために、setattr関数を用いて
        # +str(stage)+を反映させた。
        # 参照⇒https://www.python.ambitious-engineer.com/archives/1432

        # また、dic1の辞書は、そのままデータベースに入力しようとすると、
        # SQLサーバーから嫌われてエラーがでるので、
        # 組み込み関数であるstr()を用いて、python内で　辞書⇒文字列　に変換させて更新した。
        # また、逆に、python内で　文字列⇒辞書　に変換するには、
        # import ast して、ast.literal_eval(文字列オブジェクト)という関数を使う
        # 参照⇒https://www.delftstack.com/ja/howto/python/dict-to-string-in-python/
        # 参照⇒https://qiita.com/lamplus/items/b5d8872c76757b2c0dd9

        setattr(user_obj,"st"+str(stage)+"_finish_timestamp",str(dic1)) 
     
    ses.commit()
    ses.close()

def alldata_delete():
    Session = sessionmaker(bind=engine)
    ses = Session()
    ses.query(Mydata).delete()
    ses.commit()
    ses.close()
    Session = sessionmaker(bind=engine)
    ses = Session()
    myUserDatum = ses.query(Userid).all()
    
    for myUserData in myUserDatum:
        myUserData.st1_finish_timestamp=None
        myUserData.st2_finish_timestamp=None
        myUserData.st3_finish_timestamp=None
        myUserData.st4_finish_timestamp=None
        myUserData.st5_finish_timestamp=None
        myUserData.st6_finish_timestamp=None
        ses.commit()
    ses.close()


#class TestBoolean(Base):
#    __tablename__='testtable'

#    id=Column(Integer,primary_key=True)
    
    # ※"True"もしくは"False"をテキスト形式でいれてあるもの
#    boolean = Column(String(255))
#    def to_dict(self):
#        return{
#            'id':int(self.id),
#            'boolean':str(self.boolean),#　"True"もしくは"False"
#                }


#※"True"もしくは"False"をtestBoolean DBのtesttableテーブルから
#つくりだした、TestBooleanクラスから引き出し、リスト化する。

#def get_boolean():
#    Session = sessionmaker(bind=engine)
#    ses = Session()
#    mydata = ses.query(TestBoolean).filter(TestBoolean.id==1).one()
#    pprint.pprint('mydata.boolean={}'.format(mydata.boolean)) 
#    mydata.boolean="False"
#    ses.add(mydata)
#    ses.commit()
#    ses.close()# 終わったら必ずセッションを閉じておかないと、SQLalchemy内でのエラーが出る（それでも動作は完遂してくれるが）
#    return


#!python3.9.1
#from flask import Flask, session
    #redirect, jsonify, current_app, g
#import psycopg2
from socket import NI_MAXHOST
import openpyxl # 外部ライブラリ　pip install openpyxl
import sqlite3
#import json
from datetime import datetime
import pprint

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
engine = create_engine('postgresql://gnxzzavntcwtpn:2d7224a390d7ea18712db3c0d3d5a676b8255452aae23bd2dd920c4a95da2a37@ec2-52-3-2-245.compute-1.amazonaws.com:5432/dib5jng6kbpqr')

#　↓　ローカルのSQLite接続用パス 
###engine = create_engine('sqlite:///treasurehuntdb.sqlite3')


# base model
Base=declarative_base()

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
    time_stamp=Column(DateTime)
  

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
    st1_finish_timestamp=Column(DateTime)
    st2_finish_timestamp=Column(DateTime)
    st3_finish_timestamp=Column(DateTime)
    st4_finish_timestamp=Column(DateTime)
    st5_finish_timestamp=Column(DateTime)
    st6_finish_timestamp=Column(DateTime)

 

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
    pprint.pprint('mydata.myutil={}'.format(mydata))
    ses.close()# 終わったら必ずセッションを閉じておかないと、SQLalchemy内でのエラーが出る（それでも動作は完遂してくれるが）
    return mydata

def get_data_from_table_object(gr,nm,tbnm):
    Session = sessionmaker(bind=engine)
    ses = Session()
    #pprint.pprint('group_name,name.myutil={}'.format(gr+','+nm))
    if tbnm=='userid':
        try:
            user_datum = ses.query(Userid).filter(Userid.group==gr , Userid.name==nm).one()
            # mydata テーブルのデータが、groupごとにセレクトできるようになっていない⇒要改良
            res = user_datum.to_dict()
        except NoResultFound:
            res = False
    elif tbnm=='mydata':
        try:
            user_group_data = ses.query(Mydata).filter(Mydata.group==gr ).all()
            res = get_by_list(user_group_data)
        except NoResultFound:
            res = False
    elif tbnm=='stage_key':
        try:
            stage_key_datum = ses.query(Stage_key).filter(Stage_key.stage==gr ).one()
            res = stage_key_datum.to_dict()
        except NoResultFound:
            res = False
    
    pprint.pprint('res.myutil={}'.format(res))
    
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
def post_msg_to_sql(user_id,msg,now_timestamp):
    user_datum = get_data_from_user_table(user_id)
    group=user_datum['group']
    name=user_datum['name']
    
    dict_msg={}
    dict_msg['input_key']=msg
    dict_msg['group']=group
    dict_msg['name']=name
    dict_msg['user_id']=user_id
    dict_msg['time_stamp']=now_timestamp

    Session = sessionmaker(bind=engine)
    ses = Session()
    MyD_obj = Mydata()
    MyD_obj.update_dict(dict_msg)
    ses.add(MyD_obj)
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


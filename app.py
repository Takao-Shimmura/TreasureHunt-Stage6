#!python3.9.1
from flask import Flask, render_template,request,session, redirect, jsonify
import pickle

import ast
import pandas as pd
#import numpy as np

import json
from datetime import datetime
import datetime

import os
import pathlib
import pytz
import pprint
import copy #　リストや辞書などのミュータブル（更新可能）オブジェクトをコピーする際に必要
# ↑　参照　https://note.nkmk.me/python-copy-deepcopy/


from myutil import get_data_test,get_data_from_table_object,post_msg_to_sql,\
    post_stageClear_timestamp,get_data_from_user_table,alldata_delete

app=Flask(__name__)


app.secret_key = b'random shimmura code'

# access top page.
@app.route('/',methods=['GET'])
def index():
    
        #test_message=get_data_test()
    return render_template('messages.html',\
            login=False,\
            title='宝探しゲーム　in経絡経穴概論　',\
            #message=test_message
            )

# login form sended.
@app.route('/login',methods=['POST'])
def login_post():
    
    group=request.form.get('group_name')
    nameid=request.form.get('name_id')
    tablename='userid'
    #pprint.pprint('group.app={}'.format(group+','+nameid))
    #dic1=get_data_from_table_object(group)
    res=get_data_from_table_object(group,nameid,tablename,)
    if res:
        flg='True'
        session['name'] = res['name']
        session['user_id'] = res['user_id']
        session['group'] = res['group']
        now_stage=0
        for i in range(6):
            pprint.pprint('st'+str(i+1)+'_finish_timestamp ={}'.format(res['st'+str(i+1)+'_finish_timestamp'] ))
            
            if res['st'+str(i+1)+'_finish_timestamp'] != 'None' :
                now_stage=i+1
        session['stage'] = now_stage+1
        pprint.pprint('session[stage]  ={}'.format(session['stage'] ))


    else:
        flg='False'
        session['name'] = ''
        session['user_id'] =''
        session['group'] = ''
    
    #pprint.pprint('session[user_id,group]={}'.format(str(session['user_id']) +','+session['group']))        
    return jsonify(flg,session['name'],session['group'],session['user_id'],session['stage'] )

# get messages.
@app.route('/messages',methods=['POST'])
def getMsg():
    # ↓↓　ステージをクリアしたユーザー名を「仮に」入れておく→送信エラー防止のため
    cleared_user_name=''

    group=session['group'] 
    nameid=session['name']
    tablename='mydata'
    #　pprint.pprint('getMsg.app={}'.format(group+','+nameid))
    #dic1=get_data_from_table_object(group)
    # ↓↓　myutil内のget_data_from_table_object()関数 を呼び出して、
    # 入力履歴を返してもらう
    res = get_data_from_table_object(group,nameid,tablename)

    if session['name']=='admin':
        current_stege=''
        seikai_flg=''
        cleared_user_name=''
    else:
        # ↓↓　現在のステージNoを送信する
        current_stege=str(session['stage'])
        # ↓↓　myutil内のget_data_from_table_object()関数 を呼び出して、
        # stageのkey(正解)を返してもらう
        
        if current_stege!='7':#ステージ6もクリアしたならば、seikai_flg=''にしてフォアグラウンドに返す
            gr_st=str(session['stage'] )
            nameid='key'
            tablename='stage_key'
            ans = get_data_from_table_object(gr_st,nameid,tablename)
            # ↓↓　まったく投稿がないときは、最新の投稿（res[len(res)-1]）自体に中身がないので、
            # if ans['key']==res[len(res)-1]['input_key']:節でエラーが出てしまう。
            # それを回避するために、まずは無投稿でないことを確認する。
            if res != []:
                # ↓↓　res[len(res)-1]['input_key']は、最新の投稿（res[len(res)-1]）で
                # 入力された内容（['input_key']）のこと。これが正解（ans['key']）とあっているかどうか？
                if ans['key']==res[len(res)-1]['input_key']:
                    user_datum = get_data_from_user_table(session['user_id'] )
                    # ↓↓　st'+gr_st+'_finish_timestamp　内に格納されているのは、
                    # {クリアしたuser名: ? ,クリアした時刻: ? } という形の、「辞書」を、文字列に変換したもの
                    
                    if user_datum['st'+gr_st+'_finish_timestamp'] != 'None':
                        # python内で　文字列⇒辞書　に変換するには、
                        # import ast して、ast.literal_eval(文字列オブジェクト)という関数を使う
                        # 参照⇒https://www.delftstack.com/ja/howto/python/dict-to-string-in-python/
                        # 参照⇒https://qiita.com/lamplus/items/b5d8872c76757b2c0dd9
                        timestamp_Dic_from_userdatum = ast.literal_eval(user_datum['st'+gr_st+'_finish_timestamp'])
                        # ↓↓　とりだした辞書から、ステージをクリアしたユーザー名を引き出す
                        cleared_user_name=timestamp_Dic_from_userdatum['name']
                        # ↓↓　とりだした辞書から、ステージをクリアした時刻を引き出し、.fromisoformat()　メソッドにて
                        # ISO8601形式の文字列⇒時刻　へと変換する
                        # 参照⇒https://note.nkmk.me/python-datetime-isoformat-fromisoformat/
                        pprint.pprint('clear_name={}'.format(timestamp_Dic_from_userdatum['name']))
                        #pprint.pprint('time_stamp={}'.format(timestamp_Dic_from_userdatum['time_stamp']))
                        claer_time = datetime.datetime.fromisoformat(timestamp_Dic_from_userdatum['time_stamp'] )
                        flg = datetime.datetime.now(pytz.timezone('Asia/Tokyo')) - claer_time
                        if flg < datetime.timedelta(seconds=10):
                            seikai_flg='atari'
                            # ↓↓　正解した時は、ステージNoを一つプラスしておく
                            session['stage'] = session['stage']  +1
                            current_stege=str(session['stage'])
                        else:
                            seikai_flg=''
                    else:
                        seikai_flg='time stamp error'
                else:
                    seikai_flg=''
            else:
                seikai_flg=''
        else:
             seikai_flg=''

    return jsonify(res,seikai_flg,current_stege,cleared_user_name) 

    # post message
@app.route('/post',methods=['POST'])
def postMsg():
    user_id = session['user_id']
    msg=request.form.get('comment')
    #　↓　SQLiteのデータベースを操作
    
    if msg !='':
        # ↓↓　現在の時刻を　'Asia/Tokyo'のタイムゾーンで取得
        now_timestamp = datetime.datetime.now(pytz.timezone('Asia/Tokyo'))
        # ↓↓　現在の時刻を　.isoformat()　メソッドにて　時刻　⇒　ISO8601形式の文字列　へと変換する
        # 参照⇒https://note.nkmk.me/python-datetime-isoformat-fromisoformat/
        str_timestamp = now_timestamp.isoformat()

        stage=str(session['stage'] )

    # ↓↓　myutil内のget_data_from_table_object()関数 を呼び出して、
    # stegeのkey(正解)を返してもらう
        
        nameid='key'
        tablename='stage_key'
        ans = get_data_from_table_object(stage,nameid,tablename)
        if ans['key'] == msg:
            seikai_flg=''
            post_stageClear_timestamp(user_id,stage,str_timestamp)
        else:
            seikai_flg='hazure'
        post_msg_to_sql(user_id,msg,str_timestamp,stage,seikai_flg)

    else :
        seikai_flg=''
    return jsonify('True',seikai_flg)

# get all mydata record
#def getAll():
#    Session = sessionmaker(bind=engine)
#    ses = Session()
#    res = ses.query(Mydata).all()
#    ses.close()
#    return res






#@app.route('/ajax/',methods=['GET'])
#def ajax():
#    mydata = getAll()
#    return jsonify(getByList(mydata))

#@app.route('/form',methods=['POST'])
#def form():
#    name = request.form.get('name')
#    mail = request.form.get('mail')
#    age = int(request.form.get('age'))
#    mydata = Mydata(name=name,mail=mail,age=age)
#    Session = sessionmaker(bind=engine)
#    ses = Session()
#    ses.add(mydata)
#    ses.commit()
#    ses.close()
#    return 'OK'



# member_data=[]
# message_data=[]
# member_data_file='member_data.dat'
# message_data_file='message_data.dat'


# load member_data from file.
# try:
#     with open(member_data_file,"rb")as f:
#         list=pickle.load(f)
#         if list !=None:
#             member_data=list
# except:
#     pass

# load message_data from file.
# try:
#     with open(message_data_file,"rb")as f:
#         list=pickle.load(f)
#         if list !=None:
#            　message_data=list
# except:
#     pass




# delete message
@app.route('/delete',methods=['POST'])
def delMsg():
    alldata_delete()

    return 'True'











if __name__=='__main__':
    app.debug = True
    app.run(host='localhost') #ローカルホスト接続時
    #app.run(host='0.0.0.0') #サーバにデプロイ時
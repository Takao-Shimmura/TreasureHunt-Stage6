#!python3.9.1
from flask import Flask, render_template,request,session, redirect, jsonify
import pickle


import pandas as pd
#import numpy as np

import json
from datetime import datetime

import os
import pathlib
import pytz
import pprint
import copy #　リストや辞書などのミュータブル（更新可能）オブジェクトをコピーする際に必要
# ↑　参照　https://note.nkmk.me/python-copy-deepcopy/


from myutil import get_data_test,get_data_from_table_object,post_msg_to_sql

app=Flask(__name__)


app.secret_key = b'random shimmura code'

# access top page.
@app.route('/',methods=['GET'])
def index():
    session['stage'] = 1
        #test_message=get_data_test()
    return render_template('messages.html',\
            login=False,\
            title='経絡経穴概論　Treasure Hunting',\
            #message=test_message
            )

# login form sended.
@app.route('/login',methods=['POST'])
def login_post():
    
    group=request.form.get('group_name')
    nameid=request.form.get('name_id')
    tablename='user'
    pprint.pprint('group.app={}'.format(group+','+nameid))
    #dic1=get_data_from_table_object(group)
    res=get_data_from_table_object(group,nameid,tablename,)
    if res:
        flg='True'
    else:
        flg='False'
    session['name'] = res['name']
    session['user_id'] = res['user_id']
    session['group'] = res['group']
    pprint.pprint('session[user_id,group]={}'.format(str(session['user_id']) +','+session['group']))        
    return jsonify(flg,session['name'],session['group'],session['user_id'])

# get messages.
@app.route('/messages',methods=['POST'])
def getMsg():
    group=session['group'] 
    nameid=session['name']
    tablename='mydata'
    #　pprint.pprint('getMsg.app={}'.format(group+','+nameid))
    #dic1=get_data_from_table_object(group)
    # ↓↓　myutil内のget_data_from_table_object()関数 を呼び出して、
    # 入力履歴を返してもらう
    res = get_data_from_table_object(group,nameid,tablename)
    now_timestamp = datetime.now(pytz.timezone('Asia/Tokyo'))

    ans=session['stage']
    return jsonify(res) 

    # post message
@app.route('/post',methods=['POST'])
def postMsg():
    user_id = session['user_id']
    msg=request.form.get('comment')
    #　↓　SQLiteのデータベースを操作
    
    if msg !='':
        now_timestamp = datetime.now(pytz.timezone('Asia/Tokyo'))
    #    pprint.pprint('now.app={}'.format(now_timestamp))
    #    pprint.pprint('now.type={}'.format(type(now_timestamp)))
        post_msg_to_sql(user_id,msg,now_timestamp)
        group=str(session['stage'] )
        nameid='key'
        tablename='stage_key'
    # ↓↓　myutil内のget_data_from_table_object()関数 を呼び出して、
    # sutegeのkey(正解)を返してもらう
        res = get_data_from_table_object(group,nameid,tablename)
        if res['key']==msg:
            seikai_flg='atari'
        else:
            seikai_flg='hazure'
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
#@app.route('/delete',methods=['POST'])
#def delMsg():
#    global message_data
#    message_data.clear()
#    try:
#        with open(message_data_file,'wb')as f:
#            pickle.dump(message_data,f)
#    except:
#        pass
#    return 'True'











if __name__=='__main__':
    app.debug = True
    #app.run(host='localhost') #ローカルホスト接続時
    app.run(host='0.0.0.0') #サーバにデプロイ時
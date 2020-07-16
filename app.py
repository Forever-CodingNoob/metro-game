from flask import Flask,url_for,redirect,render_template,flash,Request,request,session
import sqlite3
from scripts import Station
import random
import time
import datetime

app=Flask(__name__)
app.config['SECRET_KEY']="".join([chr(random.randint(21,126)) for i in range(10)])
print(app.secret_key)
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(minutes=2)



@app.route('/<string:station>/<int:number>')
def show_station(station,number):
    station=station.replace('_','/')#為避免'台北101/世貿'不能作為網址，故連結會導向'台北101_世貿'進入此函數，在此換成'台北101/世貿'!!!!!!!!!
    print(f"station:{station}" , f"number:{number}")
    station=Station(station,number)
    return render_template('station.html',station=station)
@app.route('/station/<string:station>')
def just_show_station(station):
    return redirect(url_for('show_station',station=station,number=0))




# @app.route('/favicon.ico')
# def img():
#     print("brower is getting favortie icon....")
#     return "nope"
@app.route('/')
def home():
    return render_template('index.html')
@app.route('/johnnysucks',methods=('POST',))
def johnnysucks():
    if 'timestamp' in session:
        timedelta=time.time()-session['timestamp']
        flash('林致中已經被電爆ㄌ，請再等%d秒' % int(120-timedelta))

    else:
        flash('你不費吹灰之力就電爆林致中ㄌ')
        session['timestamp']=time.time()
    print(request.headers.get("Referer"))
    return redirect(request.headers.get("Referer"))
if __name__=='__main__':
    app.run()




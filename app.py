from flask import Flask,url_for,redirect,render_template,flash,Request,request,session,abort
import sqlite3
from scripts import Station,startGame,Game,config_db_url,STATIONS_DB_NAME,GAMES_DB_NAME,STATIONOWNED_DB_NAME,DB_NAMES,executeSQL_fetchall
import random
import time
import datetime

app=Flask(__name__)
app.config['SECRET_KEY']="".join([chr(random.randint(32,126)) for i in range(10)])
config_db_url(app)
print(app.secret_key)



@app.route('/<path:station>')#?number=problem number
def show_station(station):
    number=int(request.args.get('number','0'))#get the number of problem of this station, if the number is None then it is set to 0


    #station=station.replace('_','/')#為避免'台北101/世貿'不能作為網址，故連結會導向'台北101_世貿'進入此函數，在此換成'台北101/世貿'!!!!!!!!!
    print(f"station:{station}" , f"number:{number}")
    station=Station(station,number)
    return render_template('station.html',station=station)
@app.route('/station/<path:station>')
def just_show_station(station):
    return redirect(url_for('show_station',station=station,number=0))

@app.route('/startgame/<int:players>')
def startgame(players):
    startGame(players)
    return redirect(url_for('home'))
@app.route('/games/<string:gameid>')
def showgame(gameid):
    try:
        game=Game(gameid)
    except Game.GameNotFoundError as e:
        print(str(e))
        return redirect(url_for('showgames'))
    return render_template('game.html',game=game)
@app.route('/games/<string:gameid>/join')
def joingame(gameid):
    return render_template('login.html')
@app.route('/games/<string:gameid>/join',methods=('POST',))
def joingame_submit(gameid):
    player_name=request.form['player_name']
    if not player_name:
        flash('還敢匿名加入遊戲啊?')
        return render_template('login.html')
    password=request.form['password']
    if not password:
        flash('還敢不設密碼啊?')
        return render_template('login.html')
    Game.join(gameid,player_name,password)
    return redirect(url_for('home'))
@app.route('/games')
def showgames():
    games=Game.getAllGames()
    return render_template('games.html',games=games)

# @app.route('/favicon.ico')
# def img():
#     print("brower is getting favortie icon....")
#     return redirect(url_for('static',filename='img/favicon.ico'))
@app.route('/')
def home():
    return render_template('index.html')
@app.route('/johnnysucks',methods=('POST',))
def johnnysucks():
    PRESS_TIME_DELTA=30
    if 'timestamp' in session:
        timedelta=time.time()-session['timestamp']
        if timedelta>=PRESS_TIME_DELTA:
            flash('你又不費吹灰之力就電爆林致中ㄌ')
            session['timestamp'] = time.time()
        else:
            flash('林致中已經被電爆ㄌ，請再等%d秒' % int(PRESS_TIME_DELTA-timedelta))
    else:
        flash('你不費吹灰之力就電爆林致中ㄌ')
        session['timestamp']=time.time()
    print(request.headers.get("Referer"))
    return redirect(request.headers.get("Referer"))
@app.route('/sql')
def sql_query_editor():
    return render_template('sql.html',logs='',db_names=DB_NAMES,auth=session.get('auth'))
@app.route('/sql',methods=('POST',))
def sql_query_execute():
    sql=request.form['sql']
    db_filename=request.form['db']
    command=sql.split()[0].upper()
    ALLOWED_COMMAND=['SELECT']
    print('sql:',sql,',','db_filename:',db_filename,',','command:',command)
    if command in ALLOWED_COMMAND:
        if sql.lower().find(command.lower())!=-1:
            print(f'find command {command}!!!')
            results = executeSQL_fetchall(sql, db_filename)
            if type(results) is list:
                results='[\t'+",\n\t".join([str(dict(row)) for row in results])+'\t]'
    else:
        results=f'COMMAND "{command}" IS NOT ALLOED OR INVALID'
    logs=request.form['sql-log']+'\n\n('+db_filename+')>>'+sql+'\noutput:\n'+results
    return render_template('sql.html',logs=logs,db_names=DB_NAMES,auth=session.get('auth'))
@app.route('/auth',methods=('POST','GET'))
def auth():
    if request.method=='POST':#POST
        referer = request.args.get('referer')
        if request.form['secret_key']==app.config['SECRET_KEY']:
            flash('successfully authorized!')
            session['auth']='admin'
            return redirect(referer)
        else:
            flash('SECRET_KEY is not correct.')
            session['auth']='visitor'
            return render_template('auth.html',referer=referer)
    else:#GET
        referer = request.headers.get("Referer")  # 導向來源路徑
        if referer is None:
            abort(403)
        return render_template('auth.html',referer=referer)

if __name__=='__main__':
    app.run()




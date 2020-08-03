from flask import Flask,url_for,redirect,render_template,flash,Request,request,session,abort
from scripts import Station,startGame,Game,config_db_url,DB_NAMES,executeSQL_fetchall,executeSQL_terminal_inhtml,Player
import time,pytz
from flask_session import Session

app=Flask(__name__)
app.config.from_object('config.Config')
config_db_url(app)
print(app.secret_key)

sess=Session()
sess.init_app(app)

app.jinja_env.globals.update(Player=Player)
app.jinja_env.globals.update(Game=Game)
app.jinja_env.globals.update(getEverOwnedStations=Player.getEverOwnedStations)
app.jinja_env.globals.update(hasSolvedProblem=Player.hasSolvedProblem)
app.jinja_env.globals.update(hasSolvedAllProblems=Player.hasSolvedAllProblems)

@app.before_request
def check_if_game_exits():
    if gameid:=session.get('game'):
        try:
            game = Game(gameid)
        except Game.GameNotFoundError:
            print(f"detected game {gameid} doesn't exist but it's in session.  Try quitting the game...")
            Game.quitgame()

def check_if_is_player(func):
    def wrapped(*args,**kwargs):
        if not session.get('player_id'):#user is not player
            flash('請先加入遊戲並成為玩家')
            return redirect(request.headers.get("Referer"))
        return func(*args,**kwargs)
    wrapped.__name__=func.__name__
    return wrapped
def check_if_in_game(func):
    def wrapped(*args,**kwargs):
        if not session.get('game'):#user is not in game
            flash('請先加入遊戲')
            return redirect(request.headers.get("Referer"))
        return func(*args,**kwargs)
    wrapped.__name__=func.__name__
    return wrapped

@app.route('/<path:station>')#?number=problem number
def show_station(station):
    number=int(request.args.get('number','0'))#get the number of problem of this station, if the number is None then it is set to 0
    gameid=session.get('game',None)

    #station=station.replace('_','/')#為避免'台北101/世貿'不能作為網址，故連結會導向'台北101_世貿'進入此函數，在此換成'台北101/世貿'!!!!!!!!!
    print(f"station:{station}" , f"number:{number}", f"gameid:{gameid}")
    station=Station(station,number,gameid=gameid)
    return render_template('station.html',station=station)
@app.route('/<path:station>',methods=('POST',))#?number=problem number
@check_if_is_player
def occupy_station(station):#解題||佔領
    number = int(request.args.get('number','0'))  # get the number of problem of this station, if the number is None then it is set to 0
    gameid = session['game']
    player_id=session['player_id']

    Player(player_id).success(Station(station,number,gameid=gameid))
    return redirect(url_for('show_station',station=station,number=number))

@app.route('/<path:station>/fail',methods=('POST',))#?number=problem number
@check_if_is_player
def fail_station(station):#解題失敗
    number = int(request.args.get('number','0'))  # get the number of problem of this station, if the number is None then it is set to 0
    gameid = session['game']
    player_id=session['player_id']

    Player(player_id).fail(Station(station,number,gameid=gameid))
    return redirect(url_for('home'))
@app.route('/station/<path:station>')
def just_show_station(station):
    return redirect(url_for('show_station',station=station,number=0))






@app.route('/startgame',methods=('POST','GET'))
def startgame():
    if request.method=='GET':#GET
        return render_template('create.html')
    else:#POST
        player_amount=int(request.form['player_amount_limit'])
        gamename=request.form['game_name']
        game_secret_key=startGame(players_amount=player_amount,gamename=gamename)
        flash(f"密鑰=={game_secret_key}，還不快記下來ㄚ")
        return redirect(url_for('home'))
@app.route('/games/<string:gameid>')
def showgame(gameid):
    try:
        game=Game(gameid)
    except Game.GameNotFoundError as e:
        print(str(e))
        return redirect(url_for('showgames'))
    return render_template('game.html',game=game)

@app.route('/games/<string:gameid>/login')
def login(gameid):
    return render_template('login.html',gameid=gameid)
@app.route('/games/<string:gameid>/login',methods=('POST',))
def login_submit(gameid):
    player_name = request.form['player_name']
    password = request.form['password']
    try:
        Game.login(gameid, player_name, password)
    except Game.LoginError as e:
        flash(str(e))
        return render_template('login.html',gameid=gameid)
    return redirect(url_for('home'))

@app.route('/games/<string:gameid>/register')
def register(gameid):
    return render_template('register.html',gameid=gameid)
@app.route('/games/<string:gameid>/register',methods=('POST',))
def register_submit(gameid):
    player_name = request.form['player_name']
    if not player_name:
        flash('還敢匿名加入遊戲啊?')
        return render_template('register.html', gameid=gameid)
    password = request.form['password']
    if not password:
        flash('還敢不設密碼啊?')
        return render_template('register.html', gameid=gameid)
    try:
        Game.register(gameid, player_name, password)
    except Game.LoginError as e:
        flash(str(e))
        return render_template('register.html',gameid=gameid)
    return redirect(url_for('home'))
@app.route('/logout',methods=('POST',))
@check_if_is_player
def logout():#need to check if the player exists(user will have playerid while the player doesn't exist if the game has been deleted)
    try:
        Game.logout(player:=Player(session['player_id']))
        flash(f'logged out from player {player.name}({player.id}).')
    except Player.PlayerNotFoundError as e:
        flash(str(e))
        session.pop('player_id')

    return redirect(url_for('home'))
@app.route('/quitgame',methods=('POST',))
@check_if_in_game
def quitgame():#no matter whether the game exists, just clear the session
    gameid=session['game']
    Game.quitgame()
    flash(f"quitted game {gameid}.")
    return redirect(url_for('home'))
@app.route('/games/<string:gameid>/end',methods=('POST','GET'))
def endgame(gameid):
    try:
        game = Game(gameid)
    except Game.GameNotFoundError:
        flash('找不到此遊戲')
        return redirect(url_for('home'))

    if request.method=='POST' or session.get('auth_id')=='admin':
        game.end()
        return redirect(url_for('home'))
    else:
        return start_auth(
            description='enter GAME KEY or SECRET KEY',
            correct_keys=[game.secret_key,app.config['SECRET_KEY']],
            referer=url_for('endgame',gameid=gameid),
            method='post',
            setSession=False
        )

@app.route('/games/<string:gameid>/delete',methods=('POST','GET'))
def deletegame(gameid):
    try:
        game = Game(gameid)
    except Game.GameNotFoundError:
        flash('找不到此遊戲')
        return redirect(url_for('home'))

    if request.method=='POST' or session.get('auth_id')=='admin':
        game.delete()
        flash('successfully deleted game %s!'%gameid)

        return redirect(url_for('home'))
    else:
        return start_auth(
            description='enter GAME KEY or SECRET KEY',
            correct_keys=[game.secret_key,app.config['SECRET_KEY']],
            referer=url_for('deletegame',gameid=gameid),
            method='post',
            setSession=False
        )


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
    if gameid:=session.get('game'):
        records=Game(gameid).getAllPlayersRecords(app.config['TIMEZONE'])
    else:
        records=None
    return render_template('index.html',records=records)
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
    return render_template('sql.html',logs='',output_in_html='',db_names=DB_NAMES,auth=session.get('auth_id'))
@app.route('/sql',methods=('POST',))
def sql_query_execute():
    sql=request.form['sql']
    db_filename = request.form['db']
    prettyprint = bool(request.form.get('pretty-output'))
    output_in_html = ''  # 額外顯示html版的output
    if not sql:
        flash('打些東東ㄅ')
        return render_template('sql.html', output_in_html='', db_names=DB_NAMES,
                               auth=session.get('auth'))

    print([command.split() for command in sql.split(';')])
    commands=[command.split()[0].upper() for command in sql.split(';') if command]
    ALLOWED_COMMANDS={'SELECT'}
    print('sql:',repr(sql),',','db_filename:',db_filename,',','commands:',commands,',','pretty-print:',prettyprint)
    if [command for command in commands if command not in ALLOWED_COMMANDS]==[] or session.get('auth_id')=='admin':
        print(f'find command {commands}!!!')
        if not prettyprint:
            results = executeSQL_fetchall(sql, db_filename)
            if type(results) is list:
                results='[\t'+",\n\t".join([str(dict(row)) for row in results])+'\t]'
        else:
            results = executeSQL_terminal_inhtml(sql,db_filename)
            output_in_html = results
    else:#there is a prohibited command in sql commands
        results=f'COMMAND {[command for command in commands if command not in ALLOWED_COMMANDS]} IS NOT ALLOWED OR INVALID'
    logs=request.form['sql-log']+'\n\n('+db_filename+')>>'+sql+'\noutput:\n'+results
    return render_template('sql.html',logs=logs,output_in_html=output_in_html,db_names=DB_NAMES,auth=session.get('auth_id'))
@app.route('/system_auth')
def system_auth():
    referer=request.args.get('referer',request.headers.get("Referer"))
    return start_auth(
                description='enter SECREY KEY',
                correct_keys=[app.config['SECRET_KEY']],
                referer=referer,
                method='get',
                setSession=True,
                session_key='auth_id',
                correct_value='admin',
                wrong_value='visitor'
            )

@app.route('/auth',methods=('POST','GET'))
def auth():
    if not session.get('auth'):
        abort(404)
    if request.method=='POST':#POST
        referer = request.args.get('referer')
        if request.form['secret_key'] in session['auth']['keys']:
            flash('successfully authorized!')
            if session['auth']['setSession']:
                session[session['auth']['session_key']]=session['auth']['correct_value']

            method=session['auth']['method'].lower()
            session.pop('auth')
            if method=='post':
                return redirect(referer,code=307)#post
            elif method=='get':
                return redirect(referer)#get
            raise ConnectionAbortedError('method needs to be post or get!')
        else:
            flash('SECRET_KEY is not correct.')
            if session['auth']['setSession']:
                session[session['auth']['session_key']]=session['auth']['wrong_value']
            #session['auth']='visitor' admin
            return render_template('auth.html',referer=referer,description=request.args.get('description'))
    else:#GET
        referer = request.args.get('referer')  # 導向來源路徑
        if referer is None:
            abort(403)
        description=request.args.get('description')
        return render_template('auth.html',referer=referer,description=description)

def start_auth(*,description,correct_keys,referer,method,setSession,session_key=None,correct_value=None,wrong_value=None):
    session['auth']={'keys':correct_keys,
                     'method':method,
                     'setSession':setSession,
                     'session_key':session_key,
                     'correct_value':correct_value,
                     'wrong_value':wrong_value}
    return redirect(url_for('auth',description=description,referer=referer))

@app.route('/history')
def gameplay_history():
    player_id=request.args.get('playerid')
    if not player_id:
        abort(404)
    records=(player:=Player(player_id)).getRecord(app.config['TIMEZONE'])
    return render_template('record.html',records=records,player=player)
if __name__=='__main__':
    app.run()




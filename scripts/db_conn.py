import sqlite3, os, subprocess
import psycopg2, psycopg2.extras


class DB_NAMES:
    STATIONS_DB_NAME = 'STATIONS_INFO_DB'  # 題目db
    GAMES_DB_NAME = 'GAMES_DB'  # 每局資料db
    STATIONOWNED_DB_NAME = 'STATIONS_OWNED_DB'  # 每局佔領概況db
    PROBLEMSSOLVED_DB_NAME = 'PROBLEMS_SOLVED_DB'  # 每局解題概況db
    CARDS_DB_NAME = 'CARDS_DB'  # 擁有特殊卡db
    SESSION_REDIS = 'REDIS'  # session(using redis to save data)


SQLITE_NAME = {DB_NAMES.STATIONS_DB_NAME: 'Stations.sqlite',
               DB_NAMES.GAMES_DB_NAME: 'Games.sqlite',
               DB_NAMES.STATIONOWNED_DB_NAME: 'StationsOwned.sqlite',
               DB_NAMES.CARDS_DB_NAME: 'Cards.sqlite',
               DB_NAMES.PROBLEMSSOLVED_DB_NAME: 'ProblemsSolved.sqlite'}
APP_NAME = "metro-game"

# x)記錄connection objects以免之後又要connect一遍太花時間
# 但要每次conn.close()是好習慣，卻造成connection object不能再用，
HEROKU_DB_URL = {DB_NAMES.STATIONS_DB_NAME: None,
                 DB_NAMES.GAMES_DB_NAME: None,
                 DB_NAMES.STATIONOWNED_DB_NAME: None,
                 DB_NAMES.CARDS_DB_NAME: None,
                 DB_NAMES.PROBLEMSSOLVED_DB_NAME: None}


def config_db_url(app):
    # app.config['HEROKU_DB_URL']=HEROKU_DB_URL
    pass


# execute postgresql command using psycopg2
def executeSQL_fetchall(sql, db_filename):
    conn = get_db_connection(db_filename, cursor_factory=psycopg2.extras.RealDictCursor)
    cur = conn.cursor()
    try:
        cur.execute(sql)
        results = cur.fetchall()
    except Exception as e:
        results = str(e)
    finally:
        cur.close()
        conn.close()

    return results


# execute postgresql in terminal
def executeSQL_terminal_inhtml(sql, db_filename):
    db_url = getDBurl(db_filename)
    sql = sql.replace('\n', ' ')  # 使用psql不能有換行符
    sql = sql.replace('\r', ' ')  # 使用psql不能有換行符
    try:
        # 利用terminal=>subprocess.Popen，用communicate() output
        # 注意：psql指令中不要出現換行符號\n，不然會程式卡住，另外，psql -c只會讀最後一句PostgreSQL指令
        # 但psycopg2輸入的postgresql指令可以有換行符號\n也不會出錯
        process = subprocess.Popen(f'psql --command "{sql}" --html {db_url}', stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE, encoding='utf-8', shell=True)
        output, error = process.communicate()  # 成功執行時在output輸出，反則在error輸出錯誤資訊
        print('output:', repr(output), ',', 'error:', repr(error))
        results = output if not error else error
    except Exception as e:  # 若上方python語句執行有問題會到這，但若是sql指令有問題(terminal中的問題)並不會報錯，而是輸出在stderr
        results = f"{e.__class__}:{e}"
        raise e
    print('results:', repr(results))
    return results


def getDBurl(db_filename):
    # get db url=>windows:heroku cli in terminal, heroku:env variables
    try:  # running on heroku
        db_config_name = os.environ[db_filename]
        # print('running on heroku...')
        # print('db_config_name:', repr(db_config_name))

        db_url = os.environ[db_config_name]
    except KeyError:  # running on windows
        # print('running on local...')
        # print(f'heroku config:get {db_filename} --app {APP_NAME}')
        # get db congif name takes much time
        db_config_name = os.popen(f'heroku config:get {db_filename} --app {APP_NAME}').read()[:-1]  # 去掉換行符號\n
        # print('db_config_name:', repr(db_config_name))

        db_url = os.popen(f"heroku config:get {db_config_name} --app {APP_NAME}").read()[:-1]  # 去掉換行符號\n
    except Exception as e:
        raise OSError("cannot get sql database's url from system.")

    return db_url


# local sqlite files connection
def get_local_sqlite_db_connection(db_filename):
    # print(__file__) #此.py檔絕對路徑
    # print(os.path.sep) #路徑分隔符"\"
    # print(__file__.split(os.path.sep)) #split the path=>list
    # print(__file__.split(os.path.sep)[:-2]) #去掉最後2個子目錄
    # print(os.sep.join(__file__.split(os.sep)[:-2])) #list組回path
    path = os.path.join(os.sep.join(__file__.split(os.sep)[:-2]),
                        'data' + os.sep + db_filename)  # 加上.splite3的路徑(\data\stations.sqlite)
    print('getting local conn....')
    print('filepath=', __file__)
    print('db_path=', path)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    print(f'tables in {db_filename}:',
          [i[0] for i in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()])
    return conn


# remote heroku postgresql connection
# manipulation db using psycopg2
# (db_url needed, get it from either environment variables(heroku) or heroku cli(windows))
def get_db_connection(db_filename, cursor_factory=psycopg2.extras.DictCursor):
    # print(f"getting heroku postgresql conn for {db_filename}....")
    if HEROKU_DB_URL[db_filename]:
        # print('find stored db url!!!')
        db_url = HEROKU_DB_URL[db_filename]
    else:
        # print('no db url stored, getting a new one...')
        db_url = getDBurl(db_filename)
        HEROKU_DB_URL[db_filename] = db_url  # save db url

    # db的url中已經有host,port,password,user,database等資訊，只要把整坨放入connect()中它就會知道了
    # 當然亦可把資料拆開，再以parameter的形式丟進去(但這裡採用整坨放)
    # print('db_url:',repr(db_url))
    conn = psycopg2.connect(db_url, sslmode='require', cursor_factory=cursor_factory)
    cur = conn.cursor()
    cur.execute(
        "SELECT tablename FROM pg_catalog.pg_tables WHERE schemaname != 'pg_catalog' AND schemaname != 'information_schema';")
    # type(conn)==psycopg2.extensions.connection
    # type(cur) ==psycopg2.extras.DictCursor
    # type(Row) ==psycopg2.extras.DictRow
    # print(f'tables in {db_filename}:',[i['tablename'] for i in cur.fetchall()])
    cur.close()
    return conn


# conn=get_db_connection(STATIONS_DB_NAME)
# cur=conn.cursor()
# cur.execute('sql query')
# print(cur.fetchall())
# conn.close()


def getREDISurl():
    # get redis url=>windows:heroku cli in terminal, heroku:env variables
    try:  # running on heroku
        redis_url = os.environ[DB_NAMES.SESSION_REDIS]
    except KeyError:  # running on windows
        redis_url = os.popen(f"heroku config:get {DB_NAMES.SESSION_REDIS} --app {APP_NAME}").read()[:-1]  # 去掉換行符號\n
    except Exception as e:
        raise OSError("cannot get redis url from system.")
    print('redis_url:', redis_url)
    return redis_url

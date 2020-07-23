import sqlite3,os
import psycopg2,psycopg2.extras
STATIONS_DB_NAME= 'STATIONS_INFO_DB'#題目db
GAMES_DB_NAME= 'GAMES_DB'#每局資料db
STATIONOWNED_DB_NAME= 'STATIONS_OWNED_DB'#每局佔領概況db
SQLITE_NAME={'STATIONS_INFO_DB':'Stations.sqlite','GAMES_DB':'Games.sqlite','STATIONS_OWNED_DB':'StationsOwned.sqlite'}
APP_NAME="metro-game"

#x)記錄connection objects以免之後又要connect一遍太花時間
#但要每次conn.close()是好習慣，卻造成connection object不能再用，
HEROKU_DB_URL={'STATIONS_INFO_DB':None,'GAMES_DB':None,'STATIONS_OWNED_DB':None}


#local sqlite files connection
def get_local_sqlite_db_connection(db_filename):
    # print(__file__) #此.py檔絕對路徑
    # print(os.path.sep) #路徑分隔符"\"
    # print(__file__.split(os.path.sep)) #split the path=>list
    # print(__file__.split(os.path.sep)[:-2]) #去掉最後2個子目錄
    # print(os.sep.join(__file__.split(os.sep)[:-2])) #list組回path
    path=os.path.join(os.sep.join(__file__.split(os.sep)[:-2]),'data'+os.sep+db_filename)#加上.splite3的路徑(\data\stations.sqlite)
    print('getting local conn....')
    print('filepath=',__file__)
    print('db_path=',path)
    conn=sqlite3.connect(path)
    conn.row_factory=sqlite3.Row
    print(f'tables in {db_filename}:',[i[0] for i in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()])
    return conn
#remote heroku postgresql connection
def get_db_connection(db_filename):
    print(f"getting heroku postgresql conn for {db_filename}....")
    if HEROKU_DB_URL[db_filename]:
        print('find stored db url!!!')
        db_url = HEROKU_DB_URL[db_filename]
        print('db_url:', repr(db_url))
    else:
        print('no db url stored, getting a new one...')
        #get db congif name takes much time
        db_config_name = os.popen(f'heroku config:get {db_filename} --app {APP_NAME}').read()[:-1] #去掉換行符號\n
        print('db_config_name:',repr(db_config_name))

        db_url = os.popen(f"heroku config:get {db_config_name} --app {APP_NAME}").read()[:-1] #去掉換行符號\n
        print('db_url:',repr(db_url))

        HEROKU_DB_URL[db_filename]=db_url#save db url

    conn = psycopg2.connect(db_url, sslmode='require',cursor_factory=psycopg2.extras.DictCursor)
    cur=conn.cursor()
    cur.execute("SELECT tablename FROM pg_catalog.pg_tables WHERE schemaname != 'pg_catalog' AND schemaname != 'information_schema';")
    # type(conn)==psycopg2.extensions.connection
    # type(cur) ==psycopg2.extras.DictCursor
    # type(Row) ==psycopg2.extras.DictRow
    print(f'tables in {db_filename}:',[i[0] for i in cur.fetchall()])
    cur.close()
    return conn
# conn=get_db_connection(STATIONS_DB_NAME)
# cur=conn.cursor()
# cur.execute('sql query')
# print(cur.fetchall())
# conn.close()
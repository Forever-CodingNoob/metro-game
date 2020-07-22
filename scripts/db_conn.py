import sqlite3,os
STATIONS_DB_NAME= 'Stations.sqlite'#題目db
GAMES_DB_NAME= 'Games.sqlite'#每局資料db
STATIONOWNED_DB_NAME= 'StationsOwned.sqlite'#每局佔領概況db

def get_db_connection(db_filename):
    # print(__file__) #此.py檔絕對路徑
    # print(os.path.sep) #路徑分隔符"\"
    # print(__file__.split(os.path.sep)) #split the path=>list
    # print(__file__.split(os.path.sep)[:-2]) #去掉最後2個子目錄
    # print(os.sep.join(__file__.split(os.sep)[:-2])) #list組回path
    path=os.path.join(os.sep.join(__file__.split(os.sep)[:-2]),'data'+os.sep+db_filename)#加上.splite3的路徑(\data\stations.sqlite)
    print('filepath=',__file__)
    print('db_path=',path)
    conn=sqlite3.connect(path)
    conn.row_factory=sqlite3.Row
    print(f'tables in {db_filename}:',[i[0] for i in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()])
    return conn
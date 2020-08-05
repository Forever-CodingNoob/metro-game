import csv
import sqlite3 #sqlite
import psycopg2 #postgresql
from scripts import get_db_connection,DB_NAMES

#save in local sqlite file
def init_sqlite():
    conn=sqlite3.connect(DB_NAMES.STATIONS_DB_NAME)
    with open('init.sql','r') as f:
        conn.executescript(f.read())
    with open('content.csv', 'r',encoding="utf-8-sig") as f:#去除開頭碼(\uxxxx)!
        reader = csv.reader(f)
        columns = next(reader)
        cur = conn.cursor()
        for data in reader:
            data=[f"'{i}'" for i in data]#加上引號
            cur.execute(f'INSERT INTO content({",".join(columns)}) VALUES({",".join(data)})')
            #可用executemany
    with open('line and station.csv', 'r',encoding="utf-8-sig") as f:#去除開頭碼(\uxxxx)!
        reader = csv.reader(f)
        columns = next(reader)
        cur = conn.cursor()
        for data in reader:
            data=[f"'{i}'" for i in data]#加上引號
            cur.execute(f'INSERT INTO line_and_station({",".join(columns)}) VALUES({",".join(data)})')
    with open('line name.csv','r',encoding="utf-8-sig") as f:#去除開頭碼(\uxxxx)!
        reader = csv.reader(f)
        columns = next(reader)
        cur = conn.cursor()
        for data in reader:
            data = [f"'{i}'" for i in data]  # 加上引號
            cur.execute(f'INSERT INTO line_name({",".join(columns)}) VALUES({",".join(data)})')
    with open('sort_sqlite.sql', 'r') as f:
        conn.executescript(f.read())
    ###
    conn.commit()
    conn.close()
    ###

#save in remote heroku postgresql db
def init_remote_heroku_postgresql():
    conn = get_db_connection(DB_NAMES.STATIONS_DB_NAME)
    with open('init.sql', 'r') as f:
        cur=conn.cursor()
        cur.execute(f.read())
        cur.close()
    with open('content.csv', 'r', encoding="utf-8-sig") as f:  # 去除開頭碼(\uxxxx)!
        reader = csv.reader(f)
        columns = next(reader)
        cur = conn.cursor()
        for data in reader:
            data = [f"'{i}'" for i in data]  # 加上引號
            cur.execute(f'INSERT INTO content({",".join(columns)}) VALUES({",".join(data)})')
            # 可用executemany
        cur.close()
    with open('line and station.csv', 'r', encoding="utf-8-sig") as f:  # 去除開頭碼(\uxxxx)!
        reader = csv.reader(f)
        columns = next(reader)
        cur = conn.cursor()
        for data in reader:
            data = [f"'{i}'" for i in data]  # 加上引號
            cur.execute(f'INSERT INTO line_and_station({",".join(columns)}) VALUES({",".join(data)})')
        cur.close()
    with open('line name.csv', 'r', encoding="utf-8-sig") as f:  # 去除開頭碼(\uxxxx)!
        reader = csv.reader(f)
        columns = next(reader)
        cur = conn.cursor()
        for data in reader:
            data = [f"'{i}'" for i in data]  # 加上引號
            cur.execute(f'INSERT INTO line_name({",".join(columns)}) VALUES({",".join(data)})')
        cur.close()
    conn.commit()

    with open('cards.csv', 'r', encoding="utf-8-sig") as f:  # 去除開頭碼(\uxxxx)!
        reader = csv.reader(f)
        columns = next(reader)
        cur = conn.cursor()
        for data in reader:
            data = [f"'{i}'" for i in data]  # 加上引號
            cur.execute(f'INSERT INTO cards({",".join(columns)}) VALUES({",".join(data)})')
        cur.close()
    conn.commit()

    #sort
    with open('sort_postgresql.sql', 'r') as f:
        cur=conn.cursor()
        cur.execute(f.read())
        cur.close()
    ###
    conn.commit()
    conn.close()
    ###
init_remote_heroku_postgresql()
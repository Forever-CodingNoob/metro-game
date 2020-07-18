import csv
import sqlite3
conn=sqlite3.connect('stations.sqlite')
with open('init.sql','r') as f:
    conn.executescript(f.read())
with open ('content.csv', 'r',encoding="utf-8-sig") as f:#去除開頭碼(\uxxxx)!
    reader = csv.reader(f)
    columns = next(reader)
    cur = conn.cursor()
    for data in reader:
        data=[f"'{i}'" for i in data]#加上引號
        cur.execute(f'INSERT INTO content({",".join(columns)}) VALUES({",".join(data)})')
        #可用executemany
with open ('line and station.csv', 'r',encoding="utf-8-sig") as f:#去除開頭碼(\uxxxx)!
    reader = csv.reader(f)
    columns = next(reader)
    cur = conn.cursor()
    for data in reader:
        data=[f"'{i}'" for i in data]#加上引號
        cur.execute(f'INSERT INTO line_and_station({",".join(columns)}) VALUES({",".join(data)})')
with open('sort.spl','r') as f:
    conn.executescript(f.read())
conn.commit()
conn.close()
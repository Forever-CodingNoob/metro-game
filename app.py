from flask import Flask,url_for,redirect,render_template
import sqlite3
app=Flask(__name__)
def get_db_connection():
    conn=sqlite3.connect('stations.sqlite')
    conn.row_factory=sqlite3.Row
    return conn
def get_station(station):
    conn=get_db_connection()
    contents=conn.execute(f'SELECT * FROM content_sorted WHERE station="{station}"').fetchall()
    conn.close()
    problems=[{'type':content['type'],'exit':content['exit'],'content':content['content'],'answer':content['answer']} for content in contents]
    station_infor = {'name':contents[0]['station'],'lines':contents[0]['lines_for_this_station'].split('/'),'grade':contents[0]['grade'],'number of problems':len(problems),'problems':problems}
    print(station_infor)
    return station_infor

@app.route('/<string:station>/<int:number>')
def show_station(station,number):
    station=get_station(station)
    return render_template('station.html',station=station,number=number)
@app.route('/<string:station>')
def just_show_station(station):
    return redirect(url_for('show_station',station=station,number=1))
@app.route('/')
def home():
    return render_template('index.html')
if __name__=='__main__':
    app.run()
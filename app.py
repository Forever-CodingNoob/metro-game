from flask import Flask,url_for,redirect,render_template
import sqlite3
from scripts import Tag,Line,get_db_connection

app=Flask(__name__)


class Station(dict):
    def __init__(self,station,problem_number):
        conn = get_db_connection()
        contents = conn.execute(f'SELECT * FROM content_sorted WHERE station="{station}"').fetchall()
        conn.close()
        print(contents)
        # problems=[{'type':content['type'],'exit':content['exit'],'content':content['content'],'answer':content['answer']} for content in contents]
        content = contents[problem_number]
        problem = {'number': problem_number, 'type': content['type'], 'exit': content['exit'],
                   'content': content['content'], 'answer': content['answer']}
        self.name= content['station']
        self.lines= Line.getLine(content['lines_for_this_station'].split('/'))
        self.grade= content['grade']
        self.number_of_problems= len(contents)
        super().__init__(problem)
        self.tags = Tag.getTags(self)
        print(self)
'''
def get_station(station,problem_number):
    conn=get_db_connection()
    contents=conn.execute(f'SELECT * FROM content_sorted WHERE station="{station}"').fetchall()
    conn.close()
    #problems=[{'type':content['type'],'exit':content['exit'],'content':content['content'],'answer':content['answer']} for content in contents]
    content=contents[problem_number]
    problem={'number':problem_number,'type': content['type'], 'exit': content['exit'], 'content': content['content'], 'answer': content['answer']}
    station_infor = {'name':contents[0]['station'],'lines':contents[0]['lines_for_this_station'].split('/'),'grade':contents[0]['grade'],'number of problems':len(contents),'problem':problem}
    
    print(station_infor)
    return station_infor
'''
@app.route('/<string:station>/<int:number>')
def show_station(station,number):
    station=station.replace('_','/')#為避免'台北101/世貿'不能作為網址，故連結會導向'台北101_世貿'進入此函數，在此換成'台北101/世貿'!!!!!!!!!
    print(f"station:{station}" , f"number:{number}")
    station=Station(station,number)
    return render_template('station.html',station=station)
@app.route('/station/<string:station>')
def just_show_station(station):
    return redirect(url_for('show_station',station=station,number=0))
@app.route('/favicon.ico')
def img():
    print("brower is getting favortie icon but there's no favicon yet")
    return "nope"
@app.route('/')
def home():
    return render_template('index.html')
if __name__=='__main__':
    app.run()




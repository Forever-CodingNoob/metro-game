import sqlite3
from .db_conn import STATIONS_DB_NAME,get_db_connection,STATIONOWNED_DB_NAME
#import scripts.game as game     don't import it here, otherwise it will cause circular imports
class Tag:
    @classmethod
    def getTags(cls, station):
        return [cls.gradeTag(station.grade),cls.typeTag(station['type']),cls.exitTag(station['exit'])]
    @classmethod
    def typeTag(cls,_type):
        _text=f"類別:{_type}"
        if _type=="活動":
            _class="badge badge-success badge-pill"
        else:
            _class="badge badge-dark badge-pill"
        return cls.makeTag(_class, _text)

    @classmethod
    def gradeTag(cls, grade):
        _text = f"等級:{grade}"
        if grade == "特殊站":
            _class = "badge badge-danger badge-pill"
        else:
            _class = "badge badge-primary badge-pill"
        return cls.makeTag(_class, _text)

    @classmethod
    def exitTag(cls, exit):
        _text=f"出口:{exit}"
        _class= "badge badge-warning"
        return cls.makeTag(_class, _text)

    @staticmethod
    def makeTag(_class,text):
        return {'class':_class,'text':text}
class Line:
    @staticmethod
    def toEN(line_name_zh):
        conn=get_db_connection(STATIONS_DB_NAME)
        cur=conn.cursor()
        cur.execute(f"SELECT lineEN FROM line_name WHERE lineZH='{line_name_zh}'")
        ENname=cur.fetchone()['lineen']
        #show weird keys=>print([i for i in a.keys()])
        #ENname=cur.fetchone()['lineEN']
        return ENname
    @classmethod
    def getLine(cls,lineList):
        return [{'name':line,'imgSRC':f'img/{cls.toEN(line)}.png'} for line in lineList]


class Station(dict):
    def __init__(self,station,problem_number,*,gameid=None):
        conn = get_db_connection(STATIONS_DB_NAME)
        cur=conn.cursor()
        cur.execute(f"SELECT * FROM content_sorted WHERE station='{station}'")
        contents = cur.fetchall()
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
        import scripts.game as game
        self.owner=game.Player(Station.getOwnerID(self.name,gameid)) if gameid else None
        print(self)

    @staticmethod
    def getOwnerID(station_name,gameid):
        conn=get_db_connection(STATIONOWNED_DB_NAME)
        cur=conn.cursor()
        cur.execute(f"SELECT owner FROM {gameid} WHERE station='{station_name}' ORDER BY id DESC LIMIT 1")
        ownerid=cur.fetchone()[0]
        conn.close()
        return ownerid




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
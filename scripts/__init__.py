import sqlite3,os
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
        conn=get_db_connection()
        ENname=conn.execute(f"SELECT lineEN FROM line_name WHERE lineZH='{line_name_zh}'").fetchone()['lineEN']
        return ENname
    @classmethod
    def getLine(cls,lineList):
        return [{'name':line,'imgSRC':f'img/{cls.toEN(line)}.png'} for line in lineList]


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
def get_db_connection():
    # print(__file__) #此.py檔絕對路徑
    # print(os.path.sep) #路徑分隔符"\"
    # print(__file__.split(os.path.sep)) #split the path=>list
    # print(__file__.split(os.path.sep)[:-2]) #去掉最後2個子目錄
    # print(os.sep.join(__file__.split(os.sep)[:-2])) #list組回path
    path=os.path.join(os.sep.join(__file__.split(os.sep)[:-2]),r'data\stations.sqlite')#加上.splite3的路徑
    print('path=',path)
    conn=sqlite3.connect(path)
    conn.row_factory=sqlite3.Row
    return conn
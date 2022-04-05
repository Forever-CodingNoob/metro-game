import sqlite3
from .db_conn import get_db_connection, DB_NAMES


# import scripts.game as game     don't import it here, otherwise it will cause circular imports
class Tag:
    @classmethod
    def getTags(cls, station):
        return [cls.gradeTag(station.grade), cls.typeTag(station['type']), cls.exitTag(station['exit'])]

    @classmethod
    def typeTag(cls, _type):
        _text = f"類別:{_type}"
        if _type == "活動":
            _class = "badge badge-success badge-pill"
        else:
            _class = "badge badge-dark badge-pill"
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
        _text = f"出口:{exit}"
        _class = "badge badge-warning"
        return cls.makeTag(_class, _text)

    @staticmethod
    def makeTag(_class, text):
        return {'class': _class, 'text': text}


class Line:
    @staticmethod
    def toEN(line_name_zh):
        conn = get_db_connection(DB_NAMES.STATIONS_DB_NAME)
        cur = conn.cursor()
        cur.execute(f"SELECT lineEN FROM line_name WHERE lineZH='{line_name_zh}'")
        ENname = cur.fetchone()['lineen']
        # show weird keys=>print([i for i in a.keys()])
        # ENname=cur.fetchone()['lineEN']
        return ENname

    @classmethod
    def getLine(cls, lineList):
        return [{'name': line, 'imgSRC': f'img/{cls.toEN(line)}.png'} for line in lineList]


class Station(dict):
    def __init__(self, station, problem_number, *, gameid=None):
        conn = get_db_connection(DB_NAMES.STATIONS_DB_NAME)
        cur = conn.cursor()
        cur.execute(f"SELECT * FROM content_sorted WHERE station='{station}'")
        contents = cur.fetchall()
        conn.close()
        print(contents)
        # problems=[{'type':content['type'],'exit':content['exit'],'content':content['content'],'answer':content['answer']} for content in contents]
        content = contents[problem_number]
        problem = {'number': problem_number, 'type': content['type'], 'exit': content['exit'],
                   'content': content['content'], 'answer': content['answer']}
        self.name = content['station']
        self.lines = Line.getLine(content['lines_for_this_station'].split('/'))
        self.grade = content['grade']
        self.number_of_problems = len(contents)
        super().__init__(problem)
        self.tags = Tag.getTags(self)
        import scripts.game as game
        ownerid = Station.getOwnerID(self.name, gameid) if gameid else None  # 目前有無加入遊戲(旁觀or玩家)
        self.owner = game.Player(ownerid) if ownerid else None  # 目前該站有無佔領人
        print(self)

    @staticmethod
    def getOwnerID(station_name, gameid):
        conn = get_db_connection(DB_NAMES.STATIONOWNED_DB_NAME)
        cur = conn.cursor()
        cur.execute(f"SELECT owner_id FROM {gameid} WHERE station='{station_name}' ORDER BY id DESC LIMIT 1")
        result = cur.fetchone()
        conn.close()
        if result is None or result[0] == '':  # 此站無佔領歷史or目前又被恢復成公有
            ownerid = None
        else:  # 此站有被佔領
            ownerid = result[0]
        return ownerid


'''
佔領玩家的playerid(owner_id)若是NULL，則表示該站變為公有地
'''

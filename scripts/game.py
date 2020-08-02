from .db_conn import get_db_connection,DB_NAMES
from .score import Score
#import scripts.stations as stations     don't import it here, otherwise it will cause circular imports
from flask import session
import random,pytz
SYMBOLS=[chr(i) for i in range(48,58)]+[chr(i) for i in range(65,91)]+[chr(i) for i in range(97,123)]
def getRandSymbol(length):
    return "".join([random.choice(SYMBOLS) for i in range(length)])
def startGame(players_amount,gamename=''):
    conn = get_db_connection(DB_NAMES.GAMES_DB_NAME)
    print('a new game created.')

    #summon random and distinct gameid
    while True:
        gameid=getRandSymbol(6)#溢位?
        cur=conn.cursor()
        cur.execute(f"SELECT * FROM games WHERE id='{gameid}'")
        if cur.fetchall():
            print("summoned the existing gameid. try making a new one....")
            continue
        break
    print('gameid:',gameid)

    #summon game secret_key
    secret_key=getRandSymbol(10)
    print('game_secret_key:',secret_key)

    #add a new game to sqlite
    cur=conn.cursor()
    cur.execute(f"INSERT INTO games(id,status,players_amount,name,secret_key) VALUES('{gameid}','starting',{players_amount},'{gamename}','{secret_key}')")
    conn.commit()
    conn.close()

    #make browser remember the game
    session['game']=gameid
    #make browser forget previous player logged in
    session.pop('player_id',None)
    #log of owning station
    conn=get_db_connection(DB_NAMES.STATIONOWNED_DB_NAME)
    cur=conn.cursor()
    cur.execute(f"""CREATE TABLE {gameid}(
                    id SERIAL PRIMARY KEY,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    station TEXT,
                    owner_id INTEGER
                    );""")
    conn.commit()
    conn.close()

    conn = get_db_connection(DB_NAMES.PROBLEMSSOLVED_DB_NAME)
    cur = conn.cursor()
    cur.execute(f"""CREATE TABLE {gameid}(
                    id SERIAL PRIMARY KEY,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    station TEXT,
                    problem_number INTEGER,
                    player_id INTEGER
                    );""")
    conn.commit()
    conn.close()
def getCurrentGameId():
    return "" if not session['game'] else session['game']

class Game:
    class GameNotFoundError(Exception):
        pass
    class GameTableNotFoundError(Exception):
        pass
    class OccupyError(Exception):
        pass
    class SolveError(Exception):
        pass
    class LoginError(Exception):
        pass
    class GameEndedError(Exception):
        pass
    def __init__(self,gameid):
        conn=get_db_connection(DB_NAMES.GAMES_DB_NAME)
        cur=conn.cursor()
        cur.execute(f"SELECT * FROM games WHERE id='{gameid}'")
        game_info=cur.fetchone()
        conn.close()
        if game_info is None:#game not found
            raise Game.GameNotFoundError(f"game {gameid} not found")
        #self.info=dict(game_info)
        self.gameid=game_info['id']
        self.created_timestamp=game_info['created_timestamp']
        self.started_timestamp=game_info['started_timestamp']
        self.name=game_info['name'] if game_info['name'] is not None else ''
        self.status=game_info['status']
        self.players_amount=game_info['players_amount']
        self.current_players_amount=len(Player.getAllplayer_ids(self.gameid))
        self.secret_key=game_info['secret_key']
        #too slow=>self.players=Player.getAllplayers(gameid)
        #game_info_dict={'gameid':game_info['id']}
    @staticmethod
    def getAllGames():
        conn=get_db_connection(DB_NAMES.GAMES_DB_NAME)
        cur=conn.cursor()
        cur.execute('SELECT id FROM games ORDER BY created_timestamp DESC')
        gameids=cur.fetchall()
        conn.close()
        return [Game(gameid[0]) for gameid in gameids]

    #建議不要用staticmethod，因為要檢查是否有此遊戲
    @staticmethod
    def register(gameid,name,password):#REGISTER
        '''check if the name is already used'''
        try:
            same_name_player=Player.getOneplayer(gameid,name)
        except Player.PlayerNotFoundError:#the name is unused
            pass
        else:#there's no error=>the name is used
            raise Game.LoginError(f'"{name}" has already been used as name. Plz try another one.')

        '''check if the game is full'''
        if Game(gameid).players_amount<=len(Player.getAllplayer_ids(gameid)):#the game is full
            raise Game.LoginError('the game is full!')

        conn=get_db_connection(DB_NAMES.GAMES_DB_NAME)
        cur=conn.cursor()
        cur.execute(f"INSERT INTO players(name,gameid,password,score) VALUES('{name}','{gameid}','{password}',{Score['init_score']})")
        conn.commit()
        conn.close()
        # make browser remember the player logged in
        session['player_id']=Player.getOneplayer(gameid,name).id
        # make browser remember the game
        session['game'] = gameid

    @staticmethod
    def login(gameid,name,password):#LOGIN
        try:
            player=Player.getOneplayer(gameid,name)
        except Player.PlayerNotFoundError as e:
            raise Game.LoginError(f'player "{name}" not found!')
        if player.password!=password:
            raise Game.LoginError('password does not match!')
        # make browser remember the player logged in
        session['player_id'] = player.id
        # make browser remember the game
        session['game'] = gameid

    @staticmethod
    def logout(player_obj):
        session.pop('player_id')
    @staticmethod
    def quitgame():
        session.pop('player_id',None)
        session.pop('game')

    def end(self):
        self.setStatus('ended')
    def delete(self):
        conn=get_db_connection(DB_NAMES.GAMES_DB_NAME)
        cur=conn.cursor()
        cur.execute(f"""DELETE FROM players WHERE gameid='{self.gameid}';
                        DELETE FROM games WHERE id='{self.gameid}';""")
        conn.commit()
        conn.close()

        conn=get_db_connection(DB_NAMES.STATIONOWNED_DB_NAME)
        conn.cursor().execute(f'DROP TABLE {self.gameid}')
        conn.commit()
        conn.close()

        conn=get_db_connection(DB_NAMES.PROBLEMSSOLVED_DB_NAME)
        conn.cursor().execute(f'DROP TABLE {self.gameid}')
        conn.commit()
        conn.close()

        if session.get('game')==self.gameid:#使用者有gameid=>清掉
            Game.quitgame()

    def setStatus(self,status):
        self.status=status
        conn=get_db_connection(DB_NAMES.GAMES_DB_NAME)
        cur=conn.cursor()
        cur.execute(f"UPDATE games SET status='{status}' WHERE id='{self.gameid}'")
        conn.commit()
        conn.close()

    @staticmethod
    def notAllow_if_gameIsEnded(func):
        def wrapped(player_obj,*arg,**kwargs):
            if Game(player_obj.gameid).status=='ended':
                raise Game.GameEndedError(f'function {func.__name__} is not allowed while the game is ended!')
            return func(*arg,**kwargs)
        return wrapped

class Player:
    class PlayerNotFoundError(Exception):
        pass
    def __init__(self,id):
        conn=get_db_connection(DB_NAMES.GAMES_DB_NAME)
        cur=conn.cursor()
        cur.execute(f"SELECT * FROM players WHERE id='{id}'")
        player=cur.fetchone()
        conn.close()
        if player is None:
            raise  Player.PlayerNotFoundError(f"player with id {id} not found.")
        self.password=player['password']
        self.name=player['name']
        self.gameid=player['gameid']
        self.id=player['id']
        self.score=player['score']
    def getSolvedProblems(self):#解題歷史(不一定有佔領)
        conn=get_db_connection(DB_NAMES.PROBLEMSSOLVED_DB_NAME)
        cur=conn.cursor()
        cur.execute(f"SELECT DISTINCT station,problem_number FROM {self.gameid} WHERE player_id={self.id}")
        result=cur.fetchall()
        conn.close()

        stations=set([i['station'] for i in result])
        problem_solved={station:[i['problem_number'] for i in result if i['station']==station] for station in stations}
        print(f'problems solved by player {self.name}:',problem_solved)
        return problem_solved
    def hasSolvedProblem(self,station,problem_num):
        return problem_num in self.getSolvedProblems().get(station,[])
    def hasSolvedAllProblems(self,station_obj):
        return len(self.getSolvedProblems().get(station_obj.name,[])) >= station_obj.number_of_problems
    def getEverOwnedStations(self):
        conn=get_db_connection(DB_NAMES.STATIONOWNED_DB_NAME)
        cur=conn.cursor()
        cur.execute(f'SELECT DISTINCT station FROM {self.gameid} WHERE owner_id={self.id}')
        stations=cur.fetchall()
        conn.close()
        return [station[0] for station in stations]
    def getCurrentOwnedStations(self):
        import scripts.stations as stations
        owned_stations=[]
        for station in self.getEverOwnedStations():
            if stations.Station.getOwnerID(station,self.gameid)==self.id:#statoin ower's id==player's id
                owned_stations.append(station)
        print(f'player {self.name} owns {owned_stations}.')
        return owned_stations

    @staticmethod
    def getAllplayer_ids(gameid):
        conn = get_db_connection(DB_NAMES.GAMES_DB_NAME)
        cur = conn.cursor()
        cur.execute(f"SELECT id FROM players WHERE gameid='{gameid}'")
        playerids = cur.fetchall()
        conn.close()
        return [playerid[0] for playerid in playerids]
    @staticmethod
    def getAllplayers(gameid):
        return [Player(playerid) for playerid in Player.getAllplayer_ids(gameid)]
    @staticmethod
    def getOneplayer_slow(gameid,name):
        players=Player.getAllplayers(gameid)
        player=[player for player in players if player.name==name]
        if player:
            return player[0]#return the only player in the game that matches the givin name
        raise Player.PlayerNotFoundError(f'player with name {name} not found.')

    @staticmethod
    def getOneplayer(gameid, name):
        conn=get_db_connection(DB_NAMES.GAMES_DB_NAME)
        cur=conn.cursor()
        cur.execute(f"SELECT id FROM players WHERE gameid='{gameid}' AND name='{name}'")
        player=cur.fetchone()
        if player:
            return Player(player[0])  # return the only player in the game that matches the givin name
        raise Player.PlayerNotFoundError(f'player with name {name} not found.')

    def solved(self,station_obj):
        print(f"player {self.name} has solved {station_obj.name}/{station_obj['number']}.")
        #check if this problem is solved
        if self.hasSolvedProblem(station_obj.name,station_obj['number']):
            raise Game.SolveError(f'this problem has already been solved by himself in game {self.gameid}.')



        conn=get_db_connection(DB_NAMES.PROBLEMSSOLVED_DB_NAME)
        cur=conn.cursor()
        try:
            cur.execute(f"""INSERT INTO {self.gameid}(station,problem_number,player_id) 
                            VALUES('{station_obj.name}',{station_obj['number']},{self.id})""")
            conn.commit()
        except Exception as e:
            raise Game.GameTableNotFoundError(f'there is no table for game {self.gameid} in PROBLEMS_SOLVED_DB.')
        finally:
            conn.close()
        print('successfully recorded the solving in db!')


        if station_obj.grade=='普通站':
            self.addPoint(Score['normal_station_pass'])
        else:
            self.addPoint(Score['special_station_pass'])

    def occupy(self,station_obj):
        print(f"player {self.name} is trying to occupy station {station_obj.name}.")
        #check if this station is vacant
        if station_obj.owner is not None:
            raise Game.OccupyError(f'this station has already had its owner in game {self.gameid}.')



        conn=get_db_connection(DB_NAMES.STATIONOWNED_DB_NAME)
        cur=conn.cursor()
        try:
            cur.execute(f"""INSERT INTO {self.gameid}(station,owner_id)
                            VALUES('{station_obj.name}',{self.id})""")
            conn.commit()
        except Exception as e:
            raise Game.GameTableNotFoundError(f'there is no table for game {self.gameid} in STATIONS_OWNED_DB.')
        finally:
            conn.close()
        print('successfully occupied this station!')

    @Game.notAllow_if_gameIsEnded
    def success(self,station_obj):
        try:
            self.solved(station_obj)
        except Game.SolveError as e:
            print('error:',str(e))


        try:
            self.occupy(station_obj)
        except Game.OccupyError as e:#someone has already owned this station
            print('error:',str(e))

    @Game.notAllow_if_gameIsEnded
    def fail(self,station_obj):
        self.addPoint(Score['mission_fail'])




    def setScore(self,score):
        self.score=score
        conn=get_db_connection(DB_NAMES.GAMES_DB_NAME)
        cur=conn.cursor()
        cur.execute(f'UPDATE players SET score={self.score} WHERE id={self.id}')
        conn.commit()
        conn.close()
    def addPoint(self,point):
        print(f'add {point} points to player {self.name}!')
        self.setScore(self.score+point)
    def getRecord(self,tz):
        conn=get_db_connection(DB_NAMES.STATIONOWNED_DB_NAME)
        cur=conn.cursor()
        cur.execute(f'SELECT * FROM {self.gameid} WHERE owner_id={self.id} ORDER BY id DESC')
        station_results=[{'type':'station','timestamp':i['timestamp'],'station':i['station']} for i in cur.fetchall()]
        conn.close()

        conn=get_db_connection(DB_NAMES.PROBLEMSSOLVED_DB_NAME)
        cur=conn.cursor()
        cur.execute(f'SELECT * FROM {self.gameid} WHERE player_id={self.id} ORDER BY id DESC')
        problem_results=[{'type':'problem','timestamp':i['timestamp'],'station':i['station'],'number':i['problem_number']} for i in cur.fetchall()]
        conn.close()


        sorted=station_results+problem_results
        sorted.sort(key=lambda x:x['timestamp'],reverse=True)
        for i in sorted:#調整時區
            utc_time=pytz.utc.localize(i['timestamp'])
            i['timestamp']=utc_time.astimezone(tz).strftime('%Y年 %m月 %d日 %H點 %M:%S')
        print('sorted_history:',sorted)
        return sorted





#datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
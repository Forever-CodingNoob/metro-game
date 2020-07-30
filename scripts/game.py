from .db_conn import get_db_connection,DB_NAMES
#import scripts.stations as stations     don't import it here, otherwise it will cause circular imports
from flask import session
import random
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

    #add a new game to sqlite
    cur=conn.cursor()
    cur.execute(f"INSERT INTO games(id,status,players_amount,name) VALUES('{gameid}','starting',{players_amount},'{gamename}')")
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
    @staticmethod
    def join(gameid,name,password):
        conn=get_db_connection(DB_NAMES.GAMES_DB_NAME)
        cur=conn.cursor()
        cur.execute(f"INSERT INTO players(name,gameid,password) VALUES('{name}','{gameid}','{password}')")
        conn.commit()
        conn.close()
        # make browser remenber the player logged in
        session['player_id']=Player.getOneplayer(gameid,name).id
        # make browser remember the game
        session['game'] = gameid
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
    def getAllplayers(gameid):
        conn=get_db_connection(DB_NAMES.GAMES_DB_NAME)
        cur=conn.cursor()
        cur.execute(f"SELECT id FROM players WHERE gameid='{gameid}'")
        playerids=cur.fetchall()
        conn.close()
        return [Player(playerid[0]) for playerid in playerids]
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

    def success(self,station_obj):
        try:
            self.solved(station_obj)
        except Game.SolveError as e:
            print('error:',str(e))


        try:
            self.occupy(station_obj)
        except Game.OccupyError as e:#someone has already owned this station
            print('error:',str(e))



#datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
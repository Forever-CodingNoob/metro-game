DROP TABLE IF EXISTS games;
DROP TABLE IF EXISTS players;
CREATE TABLE games(
	id TEXT PRIMARY KEY,
	created_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
	started_timestamp DATETIME,
	name TEXT,
	status TEXT,
	players_amount INTEGER
	
);
CREATE TABLE players(
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	name TEXT,
	gameid TEXT,
	password TEXT,
	score INTEGER DEFAULT 0;
); 
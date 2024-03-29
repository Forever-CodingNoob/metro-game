DROP TABLE IF EXISTS games;
DROP TABLE IF EXISTS players;
CREATE TABLE games(
	id TEXT PRIMARY KEY,
	created_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	started_timestamp TIMESTAMP,
	name TEXT,
	status TEXT,
	players_amount INTEGER,
	secret_key TEXT
);
CREATE TABLE players(
	id SERIAL PRIMARY KEY,
	name TEXT,
	gameid TEXT,
	password TEXT,
	score INTEGER DEFAULT 0;
);
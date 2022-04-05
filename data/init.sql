DROP TABLE IF EXISTS content;
DROP TABLE IF EXISTS line_and_station;
DROP TABLE IF EXISTS line_name;
DROP TABLE IF EXISTS cards;
CREATE TABLE content(
    station TEXT NOT NULL,
    exit TEXT NOT NULL,
    grade TEXT NOT NULL,
    type TEXT NOT NULL,
    content TEXT NOT NULL,
    answer TEXT
);
CREATE TABLE line_and_station(
    line TEXT NOT NULL,
    station TEXT NOT NULL
);
CREATE TABLE line_name(
	lineZH TEXT NOT NULL,
	lineEN TEXT NOT NULL
);
CREATE TABLE cards(
	name TEXT NOT NULL,
	description TEXT NOT NULL,
	type TEXT NOT NULL
);
DROP TABLE IF EXISTS content;
DROP TABLE IF EXISTS line_and_station;
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
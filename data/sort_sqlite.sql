DROP TABLE IF EXISTS content_sorted ;
CREATE TABLE content_sorted AS
SELECT content.station, REPLACE(group_concat(DISTINCT line),',','/') AS lines_for_this_station, content.exit, content.grade, content.type, content.content, content.answer
FROM content
JOIN line_and_station ON content.station = line_and_station.station
GROUP BY content.content
ORDER BY content.station;
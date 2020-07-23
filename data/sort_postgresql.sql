DROP TABLE IF EXISTS content_sorted;
CREATE TABLE content_sorted AS
SELECT content.station, string_agg(DISTINCT line,'/') AS lines_for_this_station, content.exit, content.grade, content.type, content.content, content.answer
FROM content
JOIN line_and_station ON content.station = line_and_station.station
GROUP BY content.content,content.station,content.exit, content.grade, content.type, content.content, content.answer
ORDER BY content.station;
from scripts import get_db_connection,DB_NAMES
def reset_remote_heroku_postgresql():
    conn=get_db_connection(DB_NAMES.GAMES_DB_NAME)
    with open('init_games_db_postgresql.sql') as f:
        cur=conn.cursor()
        cur.execute(f.read())
        cur.close()
    conn.commit()
    conn.close()
reset_remote_heroku_postgresql()
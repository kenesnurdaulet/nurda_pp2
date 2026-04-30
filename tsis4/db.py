# db.py
import psycopg2
from config import DB_CONFIG

def connect():
    return psycopg2.connect(**DB_CONFIG)

def init():
    try:
        conn = connect()
        cur  = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS players (
                id       SERIAL PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL
            );
            CREATE TABLE IF NOT EXISTS game_sessions (
                id            SERIAL PRIMARY KEY,
                player_id     INTEGER REFERENCES players(id),
                score         INTEGER NOT NULL,
                level_reached INTEGER NOT NULL,
                played_at     TIMESTAMP DEFAULT NOW()
            );
        """)
        conn.commit(); cur.close(); conn.close()
        return True
    except Exception as e:
        print(f"[DB] init failed: {e}")
        return False

def get_or_create_player(username):
    try:
        conn = connect(); cur = conn.cursor()
        cur.execute("SELECT id FROM players WHERE username=%s", (username,))
        row = cur.fetchone()
        if row:
            pid = row[0]
        else:
            cur.execute("INSERT INTO players (username) VALUES (%s) RETURNING id", (username,))
            pid = cur.fetchone()[0]
        conn.commit(); cur.close(); conn.close()
        return pid
    except Exception as e:
        print(f"[DB] get_or_create_player: {e}")
        return None

def save_session(player_id, score, level):
    try:
        conn = connect(); cur = conn.cursor()
        cur.execute(
            "INSERT INTO game_sessions (player_id, score, level_reached) VALUES (%s,%s,%s)",
            (player_id, score, level)
        )
        conn.commit(); cur.close(); conn.close()
    except Exception as e:
        print(f"[DB] save_session: {e}")

def get_top10():
    try:
        conn = connect(); cur = conn.cursor()
        cur.execute("""
            SELECT p.username, gs.score, gs.level_reached,
                   TO_CHAR(gs.played_at,'YYYY-MM-DD')
            FROM game_sessions gs
            JOIN players p ON p.id = gs.player_id
            ORDER BY gs.score DESC LIMIT 10
        """)
        rows = [(i+1,)+r for i, r in enumerate(cur.fetchall())]
        cur.close(); conn.close()
        return rows
    except Exception as e:
        print(f"[DB] get_top10: {e}")
        return []

def get_best(player_id):
    try:
        conn = connect(); cur = conn.cursor()
        cur.execute("SELECT COALESCE(MAX(score),0) FROM game_sessions WHERE player_id=%s", (player_id,))
        best = cur.fetchone()[0]
        cur.close(); conn.close()
        return best
    except:
        return 0
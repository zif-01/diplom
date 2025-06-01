import os
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor
import logging

load_dotenv()

logging.basicConfig(filename='database.log', level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

def get_db_connection():
    db_params = {
        "dbname": os.getenv("DB_NAME"),
        "user": os.getenv("DB_USER"),
        "password": os.getenv("DB_PASSWORD"),
        "host": os.getenv("DB_HOST"),
        "port": os.getenv("DB_PORT")
    }
    print("Параметры подключения:", {k: v for k, v in db_params.items() if k != "password"})
    try:
        conn = psycopg2.connect(
            dbname=db_params["dbname"],
            user=db_params["user"],
            password=db_params["password"],
            host=db_params["host"],
            port=db_params["port"],
            cursor_factory=RealDictCursor
        )
        print("Подключение к базе данных успешно")
        return conn
    except Exception as e:
        logging.error(f"Ошибка подключения к базе данных: {e}")
        raise

def ensure_user_exists(conn, user_id):
    cur = conn.cursor()
    try:
        cur.execute("SELECT 1 FROM Users WHERE id = %s", (user_id,))
        if not cur.fetchone():
            cur.execute(
                "INSERT INTO Users (id, name, email, role) VALUES (%s, %s, %s, %s)",
                (user_id, f"User {user_id}", f"user{user_id}@example.com", "student")
            )
            cur.execute(
                "SELECT MAX(id) FROM Users"
            )
            max_id = cur.fetchone()['max'] or 0
            cur.execute(
                "SELECT setval('public.users_id_seq', %s)", (max_id,)
            )
            conn.commit()
            print(f"Пользователь с id={user_id} создан")
        else:
            print(f"Пользователь с id={user_id} уже существует")
    except Exception as e:
        conn.rollback()
        logging.error(f"Ошибка при создании пользователя: {e}")
        raise
    finally:
        cur.close()

def insert_query(conn, user_id, query_text):
    try:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO Queries (user_id, query_text, status) VALUES (%s, %s, 'processed') RETURNING id",
            (user_id, query_text)
        )
        query_id = cur.fetchone()['id']
        conn.commit()
        cur.close()
        return query_id
    except Exception as e:
        logging.error(f"Ошибка при вставке запроса: {e}")
        raise

def insert_response(conn, query_id, response_text):
    try:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO Responses (query_id, response_text) VALUES (%s, %s)",
            (query_id, response_text)
        )
        conn.commit()
        cur.close()
    except Exception as e:
        logging.error(f"Ошибка при вставке ответа: {e}")
        raise
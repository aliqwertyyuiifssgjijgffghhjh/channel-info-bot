import sqlite3
from datetime import datetime, timezone


DATABASE_FILE = "channel_bot.db"


def get_connection():
    connection = sqlite3.connect(
        DATABASE_FILE,
        timeout=10,
    )

    connection.execute(
        "PRAGMA journal_mode=WAL"
    )

    return connection


def init_db():
    connection = get_connection()

    try:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS lookups (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_user_id INTEGER NOT NULL,
                telegram_username TEXT,
                channel_id INTEGER NOT NULL,
                channel_username TEXT,
                channel_title TEXT,
                created_at TEXT NOT NULL
            )
            """
        )

        connection.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_user_id
            ON lookups(telegram_user_id)
            """
        )

        connection.commit()

    finally:
        connection.close()


def save_lookup(
    telegram_user_id,
    username,
    channel_id,
    channel_username,
    channel_title,
):
    connection = get_connection()

    try:
        connection.execute(
            """
            INSERT INTO lookups (
                telegram_user_id,
                telegram_username,
                channel_id,
                channel_username,
                channel_title,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                telegram_user_id,
                username,
                channel_id,
                channel_username,
                channel_title,
                datetime.now(timezone.utc).isoformat(),
            ),
        )

        connection.commit()

    finally:
        connection.close()


def get_stats(telegram_user_id):
    connection = get_connection()

    try:
        cursor = connection.execute(
            """
            SELECT COUNT(*)
            FROM lookups
            WHERE telegram_user_id = ?
            """,
            (telegram_user_id,),
        )

        result = cursor.fetchone()

        return result[0] if result else 0

    finally:
        connection.close()

import sqlite3
from threading import Lock

class MessageDB:
    def __init__(self, db_path):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.lock = Lock()
        self._init_tables()

    def _init_tables(self):
        with self.lock:
            cur = self.conn.cursor()
            cur.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                send_id TEXT,
                message TEXT,
                status TEXT,
                timestamp TEXT DEFAULT (datetime('now', 'localtime'))
            )
            """)
            self.conn.commit()

    def insert_message(self, send_id: str, message: str, status: str = "") -> int:
        """
        插入一条消息记录，返回新插入的 id
        """
        with self.lock:
            cur = self.conn.cursor()
            cur.execute(
                "INSERT INTO messages (send_id, message, status) VALUES (?, ?, ?)",
                (send_id, message, status)
            )
            self.conn.commit()
            return cur.lastrowid  # 返回自增 id

    def update_message_fields(self, where_field, where_value, update_dict):
        """
        根据条件字段更新messages表的任意字段（支持多个字段同时更新）
        Args:
            where_field (str): 条件字段名（如 'id' 或 'msg_id'）
            where_value: 条件字段的值
            update_dict (dict): 要更新的字段和值，如 {'status': 'done', 'image_url': 'xxx'}
        """
        # 字段白名单，防止SQL注入
        allowed_fields = {
             "send_id","message", "status", "timestamp"
        }
        for field in update_dict:
            if field not in allowed_fields:
                raise ValueError(f"不允许更新字段: {field}")

        set_clause = ", ".join([f"{field} = ?" for field in update_dict])
        values = list(update_dict.values()) + [where_value]
        sql = f"UPDATE messages SET {set_clause} WHERE {where_field} = ?"

        with self.lock:
            cur = self.conn.cursor()
            cur.execute(sql, values)
            self.conn.commit()

    # ====== 2. 查询 status 为空 或者 发送超时 ======
    def fetch_pending_send(self) -> dict | None:
        """
        在满足以下条件的记录里返回时间最早的一条（单条字典）：
        1. status 为空字符串或 NULL
        2. status = '已发送' 且 timestamp 比现在早 5 秒以上
        如果没有匹配记录返回 None。
        """
        with self.lock:
            cur = self.conn.cursor()
            sql = """
                  SELECT id, send_id, message, status, timestamp
                  FROM messages
                  WHERE status = '' \
                     OR status IS NULL
                     OR (
                      status = '已发送'
                    AND datetime(timestamp \
                      , '+5 seconds') \
                      < datetime('now' \
                      , 'localtime')
                      )
                  ORDER BY timestamp ASC
                      LIMIT 1 \
                  """
            cur.execute(sql)
            row = cur.fetchone()
            if row is None:
                return None
            columns = [desc[0] for desc in cur.description]
            return dict(zip(columns, row))

    # ====== 2. 清空并重置自增计数器（SQLite 语法）======
    def truncate_messages(self) -> None:
        """清空数据并把自增 id 重置为 1"""
        with self.lock:
            cur = self.conn.cursor()
            cur.execute("DELETE FROM messages")
            cur.execute("UPDATE sqlite_sequence SET seq = 0 WHERE name = 'messages'")
            self.conn.commit()

import os
db_path = os.path.join(os.path.dirname(__file__), "qqChat.db")
db = MessageDB(db_path) # SQLite
db.truncate_messages()
# Copyright © 2025, Alexander Suvorov
import sqlite3
from typing import Dict, List, Optional, Any

from clm.core import generate_key, encrypt_decrypt


class CLMDatabase:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._init_db()

    def _init_db(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA foreign_keys=ON")

            conn.execute('''
                CREATE TABLE IF NOT EXISTS config (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                )
            ''')

            conn.execute('''
                CREATE TABLE IF NOT EXISTS chats (
                    name TEXT PRIMARY KEY,
                    secret_hash TEXT,  -- Хеш секретной фразы чата
                    created_at INTEGER DEFAULT (strftime('%s', 'now'))
                )
            ''')

            conn.execute('''
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    type TEXT NOT NULL CHECK (type IN ('sent', 'received')),
                    chat_name TEXT NOT NULL,
                    epoch_index INTEGER NOT NULL,
                    nonce TEXT NOT NULL,
                    message TEXT NOT NULL,
                    payload TEXT NOT NULL,
                    timestamp INTEGER NOT NULL,
                    is_deleted INTEGER DEFAULT 0,
                    created_at INTEGER DEFAULT (strftime('%s', 'now')),
                    FOREIGN KEY (chat_name) REFERENCES chats (name) ON DELETE CASCADE
                )
            ''')

            conn.execute('CREATE INDEX IF NOT EXISTS idx_messages_chat_name ON messages(chat_name)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_messages_timestamp ON messages(timestamp)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_messages_nonce ON messages(nonce)')
            conn.commit()

    def set_chat_secret_hash(self, chat_name: str, secret_hash: str):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("UPDATE chats SET secret_hash = ? WHERE name = ?",
                         (secret_hash, chat_name))
            conn.commit()

    def get_chat_secret_hash(self, chat_name: str) -> Optional[str]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT secret_hash FROM chats WHERE name = ?", (chat_name,))
            result = cursor.fetchone()
            return result[0] if result else None

    def get_config(self) -> Dict[str, str]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT key, value FROM config")
            return {row[0]: row[1] for row in cursor.fetchall()}

    def set_config(self, key: str, value: str) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("INSERT OR REPLACE INTO config VALUES (?, ?)", (key, value))
            conn.commit()

    def get_chats(self) -> Dict[str, Dict[str, Any]]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name, secret_hash, created_at FROM chats ORDER BY name")
            return {row[0]: {"name": row[0], "secret_hash": row[1], "created_at": row[2]}
                    for row in cursor.fetchall()}

    def _ensure_chat_exists(self, chat_name: str, secret_hash: Optional[str] = None) -> None:
        with sqlite3.connect(self.db_path) as conn:
            if secret_hash:
                conn.execute("INSERT OR IGNORE INTO chats (name, secret_hash) VALUES (?, ?)",
                            (chat_name, secret_hash))
            else:
                conn.execute("INSERT OR IGNORE INTO chats (name) VALUES (?)", (chat_name,))
            conn.commit()

    def save_message(self, msg_type: str, chat_name: str, epoch_index: int, nonce: str,
                     message: str, payload: str, chat_secret: str) -> None:
        self._ensure_chat_exists(chat_name)

        message_bytes = message.encode('utf-8')
        encryption_key = generate_key(chat_secret, epoch_index, nonce, len(message_bytes))
        encrypted_message = encrypt_decrypt(message_bytes, encryption_key)

        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT INTO messages (type, chat_name, epoch_index, nonce, message, payload, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (msg_type, chat_name, epoch_index, nonce, encrypted_message.hex(), payload, epoch_index))
            conn.commit()

    def get_messages(self, chat_name: Optional[str] = None, limit: int = 0,
                     include_deleted: bool = False, chat_secret: Optional[str] = None) -> List[Dict[str, Any]]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            query = '''
                SELECT id, type, chat_name, epoch_index, nonce, message, payload, timestamp, is_deleted
                FROM messages
            '''
            params = []
            where_clauses = []
            if not include_deleted:
                where_clauses.append("is_deleted = 0")
            if chat_name:
                where_clauses.append("chat_name = ?")
                params.append(chat_name)

            if where_clauses:
                query += " WHERE " + " AND ".join(where_clauses)

            query += " ORDER BY timestamp ASC"

            if limit > 0:
                query += " LIMIT ?"
                params.append(limit)

            cursor.execute(query, params)
            messages = [dict(row) for row in cursor.fetchall()]

            if chat_secret:
                for msg in messages:
                    try:
                        encrypted_message = bytes.fromhex(msg['message'])
                        encryption_key = generate_key(chat_secret, msg['epoch_index'], msg['nonce'],
                                                      len(encrypted_message))
                        decrypted_message = encrypt_decrypt(encrypted_message, encryption_key)
                        msg['message'] = decrypted_message.decode('utf-8')
                    except:
                        msg['message'] = "[ENCRYPTED - NEED SECRET]"

            return messages

    def get_message_count(self, chat_name: Optional[str] = None, include_deleted: bool = False) -> int:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            query = "SELECT COUNT(*) FROM messages"
            params = []
            where_clauses = []
            if not include_deleted:
                where_clauses.append("is_deleted = 0")
            if chat_name:
                where_clauses.append("chat_name = ?")
                params.append(chat_name)
            if where_clauses:
                query += " WHERE " + " AND ".join(where_clauses)
            cursor.execute(query, params)
            return cursor.fetchone()[0]

    def delete_message(self, message_id: int) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("UPDATE messages SET is_deleted = 1 WHERE id = ?", (message_id,))
            conn.commit()

    def permanent_delete_message(self, message_id: int) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM messages WHERE id = ?", (message_id,))
            conn.commit()

    def restore_message(self, message_id: int) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("UPDATE messages SET is_deleted = 0 WHERE id = ?", (message_id,))
            conn.commit()

    def clear_chat_history(self, chat_name: str) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM messages WHERE chat_name = ?", (chat_name,))
            conn.commit()

    def delete_chat(self, chat_name: str) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM chats WHERE name = ?", (chat_name,))
            conn.commit()

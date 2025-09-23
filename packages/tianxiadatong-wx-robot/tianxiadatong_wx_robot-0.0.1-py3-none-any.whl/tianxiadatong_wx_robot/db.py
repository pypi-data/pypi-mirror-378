import sqlite3
from threading import Lock
from datetime import datetime

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
                group_name TEXT,
                type TEXT,
                content TEXT,
                sender TEXT,
                timestamp TEXT,
                msg_id TEXT,
                quote_id TEXT,
                quote_content TEXT,
                recall_id TEXT,
                image_url TEXT,
                have_checked TEXT,
                status TEXT,
                img_md5 TEXT
            )
            """)
            # cur.execute("""
            # CREATE TABLE IF NOT EXISTS all_messages (
            #     id INTEGER PRIMARY KEY AUTOINCREMENT,
            #     group_name TEXT,
            #     type TEXT,
            #     content TEXT,
            #     sender TEXT,
            #     timestamp TEXT,
            #     msg_id TEXT,
            #     quote_id TEXT,
            #     quote_content TEXT,
            #     recall_id TEXT,
            #     image_url TEXT,
            #     have_checked TEXT,
            #     status TEXT,
            #     img_md5 TEXT
            #
            # )
            # """)
            cur.execute("""
            CREATE TABLE IF NOT EXISTS errors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                type TEXT,
                content TEXT,
                timestamp TEXT
            )
            """)
            cur.execute("""
            CREATE TABLE IF NOT EXISTS group_member (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                group_name TEXT UNIQUE,  -- 关键：设为唯一
                member TEXT
            )
            """)
            cur.execute("""
            CREATE TABLE IF NOT EXISTS send_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                send_id TEXT,
                message TEXT,
                status TEXT,
                timestamp TEXT DEFAULT (datetime('now', 'localtime'))
            )
            """)
            self.conn.commit()

    def query(self, sql, params=()):
        """
        执行自定义查询并返回结果
        """
        cur = self.conn.cursor()
        cur.execute(sql, params)
        return cur.fetchall()
        
    def query_with_fields(self, sql, params=()):
        """
        执行自定义查询并返回结果，字段名自动适配
        """
        cur = self.conn.cursor()
        cur.execute(sql, params)
        keys = [desc[0] for desc in cur.description]
        rows = cur.fetchall()
        return [dict(zip(keys, row)) for row in rows]
    
    def drop_table(self, table_name=""):
        """
        删除指定表（谨慎操作）
        """
        sql = f"DROP TABLE IF EXISTS {table_name}"
        cur = self.conn.cursor()
        cur.execute(sql)
        self.conn.commit()
        print(f"表 '{table_name}' 已删除（如果不存在则忽略）。")

    def get_message_count_by_group(self, group_name):
        """
        查询essage表指定群名的消息记录数量
        
        Args:
            group_name (str): 群名
            
        Returns:
            int: 记录数量
        """
        with self.lock:
            cur = self.conn.cursor()
            cur.execute("SELECT COUNT(*) FROM messages WHERE group_name = ?", (group_name,))
            count = cur.fetchone()[0]
            return count

    def insert_messages(self, msg):
        with self.lock:
            cur = self.conn.cursor()
            cur.execute("""
            INSERT INTO messages (group_name, type, content, sender, timestamp, msg_id, quote_id,quote_content,recall_id,image_url,have_checked,status,img_md5)
            VALUES (?, ?, ?, ?, ?, ?, ?,?,?,?,?,?,?)
            """, (
                msg.get("group_name"), msg.get("type"), msg.get("content"), msg.get("sender"),
                msg.get("timestamp"), msg.get("msg_id"), msg.get("quote_id") ,msg.get("quote_content"),
                msg.get("recall_id"),msg.get("image_url"),msg.get("have_checked"),msg.get("status"),msg.get("img_md5")
            ))
            self.conn.commit()

    # def insert_all_messages(self, msg):
    #     """插入数据到all_messages表"""
    #     with self.lock:
    #         cur = self.conn.cursor()
    #         cur.execute("""
    #         INSERT INTO all_messages (group_name, type, content, sender, timestamp, msg_id, quote_id,quote_content,recall_id,image_url,have_checked,status,img_md5)
    #         VALUES (?, ?, ?, ?, ?, ?, ?,?,?,?,?,?,?)
    #         """, (
    #             msg.get("group_name"), msg.get("type"), msg.get("content"), msg.get("sender"),
    #             msg.get("timestamp"), msg.get("msg_id"), msg.get("quote_id") ,msg.get("quote_content"),
    #             msg.get("recall_id"),msg.get("image_url"),msg.get("have_checked"),msg.get("status"),msg.get("img_md5")
    #         ))
    #         self.conn.commit()

    def get_latest_messages(self, n, group_name=None, **filters):
        with self.lock:
            cur = self.conn.cursor()
            sql = "SELECT id, group_name, type, content, sender, msg_id, quote_id, quote_content,recall_id,image_url,have_checked,status,img_md5, timestamp FROM messages"
            where_clauses = []
            params = []
            if group_name is not None:
                where_clauses.append("group_name = ?")
                params.append(group_name)
            for key, value in filters.items():
                if isinstance(value, (list, tuple)):
                    placeholders = ','.join(['?'] * len(value))
                    where_clauses.append(f"{key} IN ({placeholders})")
                    params.extend(value)
                else:
                    where_clauses.append(f"{key} = ?")
                    params.append(value)
            if where_clauses:
                sql += " WHERE " + " AND ".join(where_clauses)
            sql += " ORDER BY id DESC LIMIT ?"
            params.append(n)
            cur.execute(sql, params)
            keys = [desc[0] for desc in cur.description]
            rows = cur.fetchall()
            return [dict(zip(keys, row)) for row in rows]

    def get_all_messages(self, group_name=None, **filters):
        with self.lock:
            cur = self.conn.cursor()
            sql = "SELECT id, group_name, type, content, sender, msg_id, quote_id, quote_content,recall_id,image_url,have_checked,status,img_md5, timestamp FROM messages"
            where_clauses = []
            params = []
            if group_name is not None:
                where_clauses.append("group_name = ?")
                params.append(group_name)
            for key, value in filters.items():
                if isinstance(value, (list, tuple)):
                    placeholders = ','.join(['?'] * len(value))
                    where_clauses.append(f"{key} IN ({placeholders})")
                    params.extend(value)
                else:
                    where_clauses.append(f"{key} = ?")
                    params.append(value)
            if where_clauses:
                sql += " WHERE " + " AND ".join(where_clauses)
            cur.execute(sql, params)
            keys = [desc[0] for desc in cur.description]
            rows = cur.fetchall()
            return [dict(zip(keys, row)) for row in rows]

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
            "image_url", "status", "recall_id", "have_checked", "content", "type",
            "sender", "timestamp", "quote_id", "quote_content","img_md5"
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

    def insert_after_record(self, group_name, target_id, new_msg):
        """
        在指定记录下方插入一条新数据
        
        Args:
            group_name (str): 群名
            target_id (int): 目标记录的id
            new_msg (dict): 要插入的新消息数据，包含以下字段：
                - type: 消息类型
                - content: 消息内容
                - sender: 发送者
                - timestamp: 时间戳
                - msg_id: 消息ID
                - quote_id: 引用消息ID
                - quote_content: 引用内容
                - recall_id: 撤回消息ID
                - image_url: 图片URL
                - have_checked: 是否已经检查过
                - status: 发送群管请求状态
        """
        with self.lock:
            cur = self.conn.cursor()
            
            # 1. 检查目标记录是否存在
            cur.execute("SELECT id FROM messages WHERE group_name = ? AND id = ?", (group_name, target_id))
            if not cur.fetchone():
                raise ValueError(f"未找到群名为 '{group_name}' 且id为 {target_id} 的记录")
            
            # 2. 获取目标记录之后的所有记录，按id降序排列
            cur.execute("""
                SELECT id FROM messages 
                WHERE group_name = ? AND id > ? 
                ORDER BY id DESC
            """, (group_name, target_id))
            records_to_update = cur.fetchall()
            
            # 3. 将目标记录之后的所有记录的id都加1（从最大的id开始，避免约束冲突）
            for record in records_to_update:
                old_id = record[0]
                new_id = old_id + 1
                cur.execute("UPDATE messages SET id = ? WHERE id = ?", (new_id, old_id))
            
            # 4. 在指定位置插入新记录
            insert_id = target_id + 1
            cur.execute("""
                INSERT INTO messages (id, group_name, type, content, sender, timestamp, msg_id, quote_id, quote_content, recall_id, image_url,have_checked,status,img_md5)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,?,?,?)
            """, (
                insert_id,
                group_name,
                new_msg.get("type", ""),
                new_msg.get("content", ""),
                new_msg.get("sender", ""),
                new_msg.get("timestamp", ""),
                new_msg.get("msg_id", ""),
                new_msg.get("quote_id", ""),
                new_msg.get("quote_content", ""),
                new_msg.get("recall_id", ""),
                new_msg.get("image_url", ""),
                new_msg.get("have_checked", ""),
                new_msg.get("status", ""),
                new_msg.get("img_md5", ""),
            ))
            
            self.conn.commit()
            print(f"成功在群 '{group_name}' 的id {target_id} 记录下方插入新记录，新记录id为 {insert_id}")
            return insert_id


    def log_error(self, err_type, content):
        with self.lock:
            cur = self.conn.cursor()
            cur.execute("INSERT INTO errors (type, content, timestamp) VALUES (?, ?, ?)",
                        (err_type, content, datetime.now().isoformat()))
            self.conn.commit()

    def insert_group_member(self, msg):
        with self.lock:
            cur = self.conn.cursor()
            cur.execute("""
            INSERT OR REPLACE INTO group_member (group_name, member)
            VALUES (?, ?)
            """, (
                msg["group_name"], msg["member"]
            ))
            self.conn.commit()


    # 消息的
    def insert_send_message(self, send_id: str, message: str, status: str = "") -> int:
        """
        插入一条消息记录，返回新插入的 id
        """
        with self.lock:
            cur = self.conn.cursor()
            cur.execute(
                "INSERT INTO send_messages (send_id, message, status) VALUES (?, ?, ?)",
                (send_id, message, status)
            )
            self.conn.commit()
            return cur.lastrowid  # 返回自增 id

    def update_send_message_fields(self, where_field, where_value, update_dict):
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
        sql = f"UPDATE send_messages SET {set_clause} WHERE {where_field} = ?"

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
                  FROM send_messages
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
    def truncate_send_messages(self) -> None:
        """清空数据并把自增 id 重置为 1"""
        with self.lock:
            cur = self.conn.cursor()
            cur.execute("DELETE FROM send_messages")
            cur.execute("UPDATE sqlite_sequence SET seq = 0 WHERE name = 'messages'")
            self.conn.commit()


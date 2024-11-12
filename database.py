import sqlite3
import os

class Database:
    def __init__(self):
        # 获取当前文件所在目录
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.db_path = os.path.join(current_dir, "chat.db")
        
        # 连接数据库
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row  # 设置行工厂，使结果可以通过列名访问
        self.cursor = self.conn.cursor()
        
        # 创建表
        self.create_tables()
    
    def create_tables(self):
        """创建数据库表"""
        try:
            # 创建用户表
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    nickname TEXT NOT NULL,
                    avatar_path TEXT
                )
            ''')
            
            # 创建好友关系表
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS friends (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    friend_id INTEGER NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users (user_id),
                    FOREIGN KEY (friend_id) REFERENCES users (user_id)
                )
            ''')
            
            # 创建聊天记录表
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS chat_messages (
                    message_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sender_id INTEGER NOT NULL,
                    receiver_id INTEGER NOT NULL,
                    content TEXT NOT NULL,
                    message_type TEXT DEFAULT 'text',
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (sender_id) REFERENCES users (user_id),
                    FOREIGN KEY (receiver_id) REFERENCES users (user_id)
                )
            ''')
            self.conn.commit()
        except Exception as e:
            print(f"创建表失败: {e}")
            raise
    
    def add_user(self, username, password, nickname, avatar_path):
        """注册新用户"""
        try:
            self.cursor.execute('''
                INSERT INTO users (username, password, nickname, avatar_path)
                VALUES (?, ?, ?, ?)
            ''', (username, password, nickname, avatar_path))
            self.conn.commit()
            return self.cursor.lastrowid
        except Exception as e:
            print(f"添加用户失败: {e}")
            return None
            
    def verify_user(self, username, password):
        """验证用户登录"""
        try:
            self.cursor.execute('''
                SELECT user_id, username, nickname, avatar_path
                FROM users 
                WHERE username = ? AND password = ?
            ''', (username, password))
            result = self.cursor.fetchone()
            if result:
                return {
                    'user_id': result['user_id'],
                    'username': result['username'],
                    'nickname': result['nickname'],
                    'avatar_path': result['avatar_path']
                }
            return None
        except Exception as e:
            print(f"验证用户失败: {e}")
            return None
            
    def add_friend_request(self, user_id, friend_username):
        """发送好友请求"""
        try:
            friend = self.get_user_by_username(friend_username)
            if not friend:
                return False, "用户不存在"
                
            # 检查是否已经是好友
            self.cursor.execute('''
                SELECT status FROM friendships 
                WHERE (user_id = ? AND friend_id = ?) 
                OR (user_id = ? AND friend_id = ?)
            ''', (user_id, friend['user_id'], friend['user_id'], user_id))
            
            existing = self.cursor.fetchone()
            if existing:
                if existing['status'] == 'accepted':
                    return False, "已经是好友"
                elif existing['status'] == 'pending':
                    return False, "好友请求待处理"
                    
            # 添加好友请求
            self.cursor.execute('''
                INSERT INTO friendships (user_id, friend_id, status)
                VALUES (?, ?, 'pending')
            ''', (user_id, friend['user_id']))
            self.conn.commit()
            return True, "好友请求已发送"
        except Exception as e:
            print(f"发送好友请求失败: {e}")
            return False, str(e)
    
    def get_user(self, username):
        """获取用户信息"""
        try:
            print(f"正在查询用户: {username}")
            self.cursor.execute('''
                SELECT user_id, username, nickname, avatar_path 
                FROM users 
                WHERE username = ?
            ''', (username,))
            result = self.cursor.fetchone()
            print(f"查询结果: {result}")
            return result
        except Exception as e:
            print(f"查询用户失败: {e}")
            return None
    
    def get_user_by_id(self, user_id):
        """通过ID获取用户信息"""
        try:
            self.cursor.execute('''
                SELECT user_id, username, nickname, avatar_path 
                FROM users 
                WHERE user_id = ?
            ''', (user_id,))
            return self.cursor.fetchone()
        except Exception as e:
            print(f"通过ID查询用户失败: {e}")
            return None
    
    def get_friends(self, user_id):
        """获取用户的好友列表"""
        try:
            print(f"正在获取用户 {user_id} 的好友列表")
            self.cursor.execute('''
                SELECT u.user_id, u.username, u.nickname, u.avatar_path
                FROM users u
                INNER JOIN friendships f ON u.user_id = f.friend_id
                WHERE f.user_id = ?
            ''', (user_id,))
            friends = self.cursor.fetchall()
            print(f"查询到的好友列表: {friends}")
            return friends
        except Exception as e:
            print(f"获取好友列表失败: {e}")
            return []
    
    def save_message(self, from_user_id, to_user_id, content, message_type='text'):
        """保存聊天消息到数据库"""
        try:
            self.cursor.execute('''
                INSERT INTO chat_messages 
                (from_user_id, to_user_id, content, message_type) 
                VALUES (?, ?, ?, ?)
            ''', (from_user_id, to_user_id, content, message_type))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"保存消息失败: {e}")
            return False
    
    def get_chat_history(self, user1_id, user2_id):
        """获取两个用户之间的聊天记录"""
        try:
            self.cursor.execute('''
                SELECT m.*, u1.nickname as from_nickname, u2.nickname as to_nickname
                FROM chat_messages m
                JOIN users u1 ON m.from_user_id = u1.user_id
                JOIN users u2 ON m.to_user_id = u2.user_id
                WHERE (m.from_user_id = ? AND m.to_user_id = ?)
                OR (m.from_user_id = ? AND m.to_user_id = ?)
                ORDER BY m.timestamp
            ''', (user1_id, user2_id, user2_id, user1_id))
            return self.cursor.fetchall()
        except Exception as e:
            print(f"获取聊天记录失败: {e}")
            return []
    
    def get_user_by_username(self, username):
        """通过用户名获取用户信息"""
        try:
            print(f"正在查询用户: {username}")
            self.cursor.execute('''
                SELECT user_id, username, nickname, avatar_path 
                FROM users 
                WHERE username = ?
            ''', (username,))
            result = self.cursor.fetchone()
            print(f"查询结果: {result}")
            if result:
                return {
                    'user_id': result['user_id'],
                    'username': result['username'],
                    'nickname': result['nickname'],
                    'avatar_path': result['avatar_path']
                }
            return None
        except Exception as e:
            print(f"通过用户名查询用户失败: {e}")
            return None
            
    def get_user_by_nickname(self, nickname):
        """通过昵称获取用户信息"""
        try:
            self.cursor.execute('''
                SELECT user_id, username, nickname, avatar_path 
                FROM users 
                WHERE nickname = ?
            ''', (nickname,))
            result = self.cursor.fetchone()
            if result:
                return {
                    'user_id': result['user_id'],
                    'username': result['username'],
                    'nickname': result['nickname'],
                    'avatar_path': result['avatar_path']
                }
            return None
        except Exception as e:
            print(f"通过昵称查询用户失败: {e}")
            return None
            
    def get_user_by_id(self, user_id):
        """通过ID获取用户信息"""
        try:
            self.cursor.execute('''
                SELECT user_id, username, nickname, avatar_path 
                FROM users 
                WHERE user_id = ?
            ''', (user_id,))
            result = self.cursor.fetchone()
            if result:
                return {
                    'user_id': result['user_id'],
                    'username': result['username'],
                    'nickname': result['nickname'],
                    'avatar_path': result['avatar_path']
                }
            return None
        except Exception as e:
            print(f"通过ID查询用户失败: {e}")
            return None
            
    def get_friends(self, user_id):
        """获取用户的好友列表"""
        try:
            print(f"正在获取用户 {user_id} 的好友列表")
            self.cursor.execute('''
                SELECT u.user_id, u.username, u.nickname, u.avatar_path
                FROM users u
                INNER JOIN friendships f ON u.user_id = f.friend_id
                WHERE f.user_id = ?
            ''', (user_id,))
            friends = []
            for row in self.cursor.fetchall():
                friends.append({
                    'user_id': row['user_id'],
                    'username': row['username'],
                    'nickname': row['nickname'],
                    'avatar_path': row['avatar_path']
                })
            print(f"查询到的好友列表: {friends}")
            return friends
        except Exception as e:
            print(f"获取好友列表失败: {e}")
            return []
    
    def add_friend(self, user_id, friend_id):
        """添加好友关系"""
        try:
            # 添加正向关系
            self.cursor.execute('''
                INSERT INTO friendships (user_id, friend_id, status)
                VALUES (?, ?, 'accepted')
            ''', (user_id, friend_id))
            
            # 添加反向关系
            self.cursor.execute('''
                INSERT INTO friendships (user_id, friend_id, status)
                VALUES (?, ?, 'accepted')
            ''', (friend_id, user_id))
            
            self.conn.commit()
            return True
        except Exception as e:
            print(f"添加好友关系失败: {e}")
            return False
    
    def save_message(self, sender_id, receiver_id, content, message_type='text'):
        """保存聊天消息"""
        try:
            self.cursor.execute('''
                INSERT INTO chat_messages (from_user_id, to_user_id, content, message_type)
                VALUES (?, ?, ?, ?)
            ''', (sender_id, receiver_id, content, message_type))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"保存消息失败: {e}")
            return False
            
    def get_chat_history(self, user_id, friend_id):
        """获取与指定好友的聊天记录"""
        try:
            self.cursor.execute('''
                SELECT 
                    m.*,
                    sender.nickname as sender_nickname,
                    receiver.nickname as receiver_nickname
                FROM chat_messages m
                JOIN users sender ON m.from_user_id = sender.user_id
                JOIN users receiver ON m.to_user_id = receiver.user_id
                WHERE (m.from_user_id = ? AND m.to_user_id = ?)
                   OR (m.from_user_id = ? AND m.to_user_id = ?)
                ORDER BY m.timestamp ASC
            ''', (user_id, friend_id, friend_id, user_id))
            
            messages = []
            for row in self.cursor.fetchall():
                messages.append({
                    'content': row['content'],
                    'type': row['message_type'],
                    'timestamp': row['timestamp'],
                    'is_send': row['from_user_id'] == user_id,
                    'sender_nickname': row['sender_nickname'],
                    'receiver_nickname': row['receiver_nickname']
                })
            print(f"获取到的聊天记录: {messages}")  # 调试输出
            return messages
        except Exception as e:
            print(f"获取聊天记录失败: {e}")
            return []
import asyncio
import websockets
import json
from PyQt5.QtCore import QObject, pyqtSignal
from database import Database

class ChatClient(QObject):
    message_received = pyqtSignal(int, str, str, str)
    history_received = pyqtSignal(list)
    online_status_changed = pyqtSignal(int, str)
    friends_list_received = pyqtSignal(list)
    connection_error = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.websocket = None
        self._connected = False
        self.server_url = 'ws://yourip:8795'
        self._user_info = None
        self._message_lock = asyncio.Lock()
        
    async def login(self, username, password):
        """登录验证"""
        try:
            print("正在连接服务器...")
            if self.websocket:
                await self.websocket.close()
                
            self.websocket = await websockets.connect(
                self.server_url,
                ping_interval=None,
                max_size=None
            )
            print("已连接到服务器，正在发送登录请求...")
            
            # 发送登录请求
            login_data = {
                'type': 'login',
                'username': username,
                'password': password
            }
            print(f"发送登录数据: {login_data}")
            await self.websocket.send(json.dumps(login_data))
            
            # 接收响应
            response = await self.websocket.recv()
            result = json.loads(response)
            print(f"收到登录响应：{result}")
            
            # 处理 auth 类型的响应
            if result.get('type') == 'auth' and result.get('success'):
                self._connected = True
                self._user_info = result.get('user_info')
                # 启动消息接收循环
                asyncio.create_task(self._receive_messages())
                print("登录成功，WebSocket 连接已建立")
                return self._user_info
                
            print("登录失败：响应格式不正确")
            return None
            
        except Exception as e:
            print(f"登录失败: {e}")
            self._connected = False
            if self.websocket:
                await self.websocket.close()
                self.websocket = None
            return None
            
    async def _receive_messages(self):
        """接收消息循环"""
        try:
            print("开始消息接收循环")
            while self._connected and self.websocket:
                try:
                    async with self._message_lock:
                        message = await self.websocket.recv()
                    data = json.loads(message)
                    print(f"收到服务器消息: {data}")
                    
                    if data['type'] == 'message':
                        self.message_received.emit(
                            data['from_id'],
                            data['from_nickname'],
                            data['content'],
                            data.get('message_type', 'text')
                        )
                    elif data['type'] == 'history':
                        self.history_received.emit(data['messages'])
                    elif data['type'] == 'friends_list':
                        print("收到好友列表数据")
                        self.friends_list_received.emit(data['friends'])
                    elif data['type'] == 'online_status':
                        self.online_status_changed.emit(
                            data['user_id'],
                            data['status']
                        )
                except websockets.exceptions.ConnectionClosed:
                    print("WebSocket 连接已关闭")
                    break
                except Exception as e:
                    print(f"处理消息错误: {e}")
                    continue
                    
        except Exception as e:
            print(f"接收消息循环错误: {e}")
        finally:
            print("消息接收循环结束")
            self._connected = False
            self.websocket = None

    async def register(self, username, password, nickname):
        """注册新用户"""
        try:
            ws = await websockets.connect(self.server_url)
            await ws.send(json.dumps({
                'type': 'register',
                'username': username,
                'password': password,
                'nickname': nickname
            }))
            
            response = await ws.recv()
            result = json.loads(response)
            await ws.close()
            
            return result.get('success'), result.get('message')
            
        except Exception as e:
            print(f"注册失败: {e}")
            return False, str(e)

    async def connect(self, username):
        """连接到服务器并认证"""
        try:
            if self._connected:
                return True
                
            self.websocket = await websockets.connect('ws://yourip:8795')
            self.username = username
            
            # 发送认证信息
            await self.websocket.send(json.dumps({
                'type': 'auth',
                'username': username
            }))
            
            # 等待认证响应
            response = await self.websocket.recv()
            auth_data = json.loads(response)
            
            if auth_data.get('success'):
                self.user_id = auth_data['user_id']
                self._connected = True
                # 启动消息接收循环
                asyncio.create_task(self._message_loop())
                return True
            else:
                error_msg = auth_data.get('error', '认证失败')
                print(f"认证失败: {error_msg}")
                return False
                
        except Exception as e:
            print(f"连接错误: {e}")
            return False
            
    async def _message_loop(self):
        """消息接收循环"""
        try:
            while self._connected:
                message = await self.websocket.recv()
                print(f"客户端收到消息: {message}")
                data = json.loads(message)
                
                if data['type'] == 'history':
                    print(f"收到聊天记录: {data['messages']}")
                    self.history_received.emit(data['messages'])
                elif data['type'] == 'message':
                    self.message_received.emit(
                        data['from_id'],
                        data['from_nickname'],
                        data['content'],
                        data.get('message_type', 'text')
                    )
                elif data['type'] == 'online_status':
                    self.online_status_changed.emit(
                        data['user_id'],
                        data['status']
                    )
        except websockets.exceptions.ConnectionClosed:
            print("连接已关闭")
            self._connected = False
        except Exception as e:
            print(f"消息接收错误: {e}")
            self._connected = False
            
    async def get_chat_history(self, friend_nickname):
        """获取聊天记录"""
        try:
            print(f"请求聊天记录: friend_nickname={friend_nickname}")
            if not self._connected:
                print("未连接到服务器")
                return None
                
            await self.websocket.send(json.dumps({
                'type': 'get_history',
                'friend_nickname': friend_nickname
            }))
            print(f"聊天记录请求已发送")
            
            # 等待服务器响应
            message = await self.websocket.recv()
            print(f"收到服务器响应: {message}")
            result = json.loads(message)
            
            if result['type'] == 'history':
                print(f"解析到聊天记录: {result['messages']}")
                return result.get('messages', [])
            return []
            
        except Exception as e:
            print(f"获取聊天记录失败: {e}")
            return []

    async def send_message(self, to_nickname, content, message_type='text'):
        """发送消息"""
        try:
            if not self._connected:
                print("未连接到服务器")
                return False
                
            await self.websocket.send(json.dumps({
                'type': 'message',
                'to_nickname': to_nickname,
                'content': content,
                'message_type': message_type
            }))
            return True
        except Exception as e:
            print(f"发送消息失败: {e}")
            return False
            
    async def get_friends_list(self, user_id):
        """获取好友列表"""
        try:
            if not self._connected:
                print(f"未连接到服务器 (_connected={self._connected})")
                return
            if not self.websocket:
                print("WebSocket 连接不存在")
                return
                
            print(f"正在请求好友列表，用户ID: {user_id}")
            await self.websocket.send(json.dumps({
                'type': 'get_friends',
                'user_id': user_id
            }))
            print("好友列表请求已发送")
        except Exception as e:
            print(f"请求好友列表失败: {e}")
            self._connected = False
            
    def close(self):
        """关闭连接"""
        if self.websocket:
            asyncio.create_task(self.websocket.close())
            self._connected = False
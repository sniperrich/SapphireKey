import asyncio
import websockets
import json
from PyQt5.QtCore import QObject, pyqtSignal

class ChatClient(QObject):
    message_received = pyqtSignal(int, str, str, str)
    history_received = pyqtSignal(list)
    online_status_changed = pyqtSignal(int, str)
    connection_error = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.websocket = None
        self.user_id = None
        self.username = None
        self._connected = False

    async def connect(self, username):
        """连接到服务器并认证"""
        try:
            if self._connected:
                return True
                
            self.websocket = await websockets.connect('ws://localhost:8795')
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
                data = json.loads(message)
                
                if data['type'] == 'chat_history':
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
        """获取与指定好友的聊天记录"""
        try:
            if not self._connected:
                print("未连接到服务器")
                return
                
            await self.websocket.send(json.dumps({
                'type': 'get_history',
                'friend_nickname': friend_nickname
            }))
        except Exception as e:
            print(f"请求聊天记录失败: {e}")
            
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
            
    def close(self):
        """关闭连接"""
        if self.websocket:
            asyncio.create_task(self.websocket.close())
            self._connected = False
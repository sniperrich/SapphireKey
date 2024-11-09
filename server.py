import asyncio
import websockets
import json
from database import Database
from datetime import datetime

class ChatServer:
    def __init__(self):
        self.clients = {}  # 存储在线客户端连接
        self.db = Database()  # 数据库连接
        
    async def handle_chat_history(self, user_id, data):
        """处理聊天记录请求"""
        try:
            friend_nickname = data['friend_nickname']
            friend = self.db.get_user_by_nickname(friend_nickname)
            if not friend:
                return
                
            # 获取聊天记录
            messages = self.db.get_chat_history(user_id, friend['user_id'])
            formatted_messages = []
            
            for msg in messages:
                formatted_messages.append({
                    'from_id': msg['from_user_id'],
                    'from_nickname': msg['from_nickname'],
                    'to_nickname': msg['to_nickname'],
                    'content': msg['content'],
                    'message_type': msg['message_type'],
                    'timestamp': msg['timestamp']
                })
            
            # 发送聊天记录
            if user_id in self.clients:
                await self.clients[user_id].send(json.dumps({
                    'type': 'chat_history',
                    'messages': formatted_messages
                }))
        except Exception as e:
            print(f"处理聊天记录请求失败: {e}")
            
    async def handle_client(self, websocket, path):
        """处理客户端连接"""
        user_id = None
        try:
            auth_message = await websocket.recv()
            auth_data = json.loads(auth_message)
            
            if auth_data['type'] == 'auth':
                user = self.db.get_user_by_username(auth_data['username'])
                if user:
                    user_id = user['user_id']
                    self.clients[user_id] = websocket
                    await websocket.send(json.dumps({
                        'type': 'auth',
                        'success': True,
                        'user_id': user_id
                    }))
                    
                    # 处理后续消息
                    async for message in websocket:
                        data = json.loads(message)
                        if data['type'] == 'message':
                            await self.handle_chat_message(user_id, data)
                        elif data['type'] == 'get_history':
                            await self.handle_chat_history(user_id, data)
                            
        except websockets.exceptions.ConnectionClosed:
            print("客户端断开连接")
        finally:
            if user_id:
                await self.unregister_client(user_id)

    async def handle_message(self, user_id, message):
        """处理客户端消息"""
        try:
            data = json.loads(message)
            if data['type'] == 'get_history':
                # 获取聊天记录
                friend_nickname = data['friend_nickname']
                friend = self.db.get_user_by_nickname(friend_nickname)
                if friend:
                    history = self.db.get_chat_history(user_id, friend['user_id'])
                    formatted_history = []
                    for msg in history:
                        from_user = self.db.get_user_by_id(msg[1])  # from_user_id
                        formatted_history.append({
                            'content': msg[3],  # content
                            'from_nickname': from_user['nickname'],
                            'message_type': msg[4],  # message_type
                            'timestamp': msg[5]  # timestamp
                        })
                    await self.clients[user_id].send(json.dumps({
                        'type': 'chat_history',
                        'friend_nickname': friend_nickname,
                        'messages': formatted_history
                    }))
            elif data['type'] == 'message':
                # 处理发送消息的逻辑
                await self.handle_chat_message(user_id, data)
                
        except Exception as e:
            print(f"处理消息失败: {e}")

    async def handle_chat_message(self, from_user_id, data):
        """处理聊天消息"""
        try:
            to_nickname = data['to_nickname']
            to_user = self.db.get_user_by_nickname(to_nickname)
            if not to_user:
                return
                
            # 保存消息到数据库
            self.db.save_message(
                from_user_id,
                to_user['user_id'],
                data['content'],
                data.get('message_type', 'text')
            )
            
            # 如果接收者在线，发送消息
            if to_user['user_id'] in self.clients:
                from_user = self.db.get_user_by_id(from_user_id)
                await self.clients[to_user['user_id']].send(json.dumps({
                    'type': 'message',
                    'from_id': from_user_id,
                    'from_nickname': from_user['nickname'],
                    'content': data['content'],
                    'message_type': data.get('message_type', 'text')
                }))
        except Exception as e:
            print(f"处理聊天消息失败: {e}")

    async def unregister_client(self, user_id):
        """注销客户端连接"""
        try:
            if user_id in self.clients:
                print(f"注销客户端连接: user_id={user_id}")
                # 发送离线状态给好友
                friends = self.db.get_friends(user_id)
                offline_message = {
                    'type': 'online_status',
                    'user_id': user_id,
                    'status': 'offline'
                }
                for friend in friends:
                    if friend[0] in self.clients:  # friend[0] 是 user_id
                        await self.clients[friend[0]].send(json.dumps(offline_message))
                
                # 删除连接
                del self.clients[user_id]
                print(f"客户端连接已注销")
        except Exception as e:
            print(f"注销客户端连接失败: {e}")

async def main():
    try:
        server = ChatServer()
        async with websockets.serve(server.handle_client, "localhost", 8795):
            print("聊天服务器已启动，监听端口 8795...")
            await asyncio.Future()
    except Exception as e:
        print(f"服务器启动失败: {e}")
        raise

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n服务器已关闭")
    except Exception as e:
        print(f"服务器运行错误: {e}") 
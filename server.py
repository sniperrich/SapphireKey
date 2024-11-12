import asyncio
import websockets
import json
from database import Database
from chat_history import ChatHistory
from datetime import datetime

class ChatServer:
    def __init__(self):
        self.db = Database()
        self.clients = {}  # 存储客户端连接
        
    async def handle_client(self, websocket):
        try:
            # 处理登录
            auth_message = await websocket.recv()
            auth_data = json.loads(auth_message)
            print(f"收到认证消息: {auth_message}")
            
            if auth_data['type'] == 'login':
                username = auth_data['username']
                password = auth_data['password']
                print(f"用户尝试登录: {username}")
                
                # 验证用户
                user = self.db.verify_user(username, password)
                if user:
                    print(f"用户 {username} 验证成功")
                    user_info = {
                        'user_id': user['user_id'],  # 确保字段名称正确
                        'username': user['username'],
                        'nickname': user['nickname']
                    }
                    
                    # 发送登录成功响应
                    await websocket.send(json.dumps({
                        'type': 'auth',
                        'success': True,
                        'user_info': user_info
                    }))
                    
                    # 存储客户端连接
                    self.clients[user['user_id']] = websocket
                    print(f"用户 {username} 已连接，ID: {user['user_id']}")
                    
                    # 处理后续消息
                    async for message in websocket:
                        try:
                            data = json.loads(message)
                            print(f"收到消息: {message}")
                            
                            if data['type'] == 'get_friends':
                                friends = self.db.get_friends(data['user_id'])
                                print(f"发送好友列表: {friends}")
                                await websocket.send(json.dumps({
                                    'type': 'friends_list',
                                    'friends': friends
                                }))
                                
                            elif data['type'] == 'get_history':
                                try:
                                    friend_nickname = data['friend_nickname']
                                    print(f"收到聊天记录请求: user_id={user['user_id']}, friend_nickname={friend_nickname}")  # 调试信息
                                    
                                    friend = self.db.get_user_by_nickname(friend_nickname)
                                    print(f"查找到好友信息: {friend}")  # 调试信息
                                    
                                    if friend:
                                        history = self.db.get_chat_history(user['user_id'], friend['user_id'])
                                        print(f"获取到聊天记录: {history}")  # 调试信息
                                        
                                        await websocket.send(json.dumps({
                                            'type': 'history',
                                            'messages': history
                                        }))
                                        print("聊天记录已发送")  # 调试信息
                                    else:
                                        print(f"未找到好友: {friend_nickname}")
                                        await websocket.send(json.dumps({
                                            'type': 'history',
                                            'messages': []
                                        }))
                                except Exception as e:
                                    print(f"处理聊天记录请求失败: {e}")
                                    await websocket.send(json.dumps({
                                        'type': 'history',
                                        'messages': []
                                    }))
                                    
                            elif data['type'] == 'message':
                                try:
                                    to_nickname = data['to_nickname']
                                    content = data['content']
                                    message_type = data.get('message_type', 'text')
                                    
                                    to_user = self.db.get_user_by_nickname(to_nickname)
                                    if to_user:
                                        # 保存消息到数据库
                                        self.db.save_message(
                                            user['user_id'],
                                            to_user['user_id'],
                                            content,
                                            message_type
                                        )
                                        
                                        # 如果接收者在线，发送消息
                                        if to_user['user_id'] in self.clients:
                                            await self.clients[to_user['user_id']].send(json.dumps({
                                                'type': 'message',
                                                'from_id': user['user_id'],
                                                'from_nickname': user['nickname'],
                                                'content': content,
                                                'message_type': message_type,
                                                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                            }))
                                except Exception as e:
                                    print(f"处理消息失败: {e}")
                                    
                        except json.JSONDecodeError:
                            print("无效的JSON消息")
                        except Exception as e:
                            print(f"处理消息错误: {e}")
                            
                else:
                    print(f"用户 {username} 验证失败")
                    await websocket.send(json.dumps({
                        'type': 'auth',
                        'success': False,
                        'message': '用户名或密码错误'
                    }))
                    
        except websockets.exceptions.ConnectionClosed:
            print("客户端连接已关闭")
        except Exception as e:
            print(f"处理客户端错误: {e}")
        finally:
            # 清理客户端连接
            for user_id, ws in list(self.clients.items()):
                if ws == websocket:
                    del self.clients[user_id]
                    print(f"用户 {user_id} 已断开连接")
                    break

async def main():
    server = ChatServer()
    try:
        async with websockets.serve(
            server.handle_client,
            "0.0.0.0",
            8795,
            ping_interval=None,
            max_size=None
        ):
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
from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QMessageBox,QPushButton
from PyQt5.QtCore import Qt
from bubble_message import ChatWidget
from friendlist import FriendList
from chat_history import ChatHistory
import asyncio
from PyQt5.QtCore import QTimer
import websockets
import json

class ChatWindow(QMainWindow):
    def __init__(self, user_id, username, nickname, chat_client):
        super().__init__()
        self.user_id = user_id
        self.username = username
        self.nickname = nickname
        self.chat_client = chat_client
        self.current_friend = None
        
        # 初始化UI
        self.init_ui()
        
        # 连接信号
        self.chat_client.message_received.connect(self.on_message_received)
        self.chat_client.history_received.connect(self.on_history_received)
        self.chat_client.friends_list_received.connect(self.on_friends_list_received)
        self.chat_client.online_status_changed.connect(self.on_online_status_changed)
        self.chat_widget.message_sent.connect(self.send_message)
        
        # 延迟请求好友列表
        QTimer.singleShot(1000, lambda: asyncio.create_task(self.load_friends_list()))
        
    def init_ui(self):
        print("初始化聊天窗口UI...")
        self.setWindowTitle(f'聊天窗口 - {self.nickname}')
        self.setMinimumSize(800, 600)
        
        # 创建主窗口部件
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        # 创建水平布局
        layout = QHBoxLayout()
        
        # 创建好友列表
        self.friend_list = FriendList(self)
        self.friend_list.friend_selected.connect(self.on_friend_selected)
        add_button=QPushButton()
        # 创建聊天区域
        self.chat_widget = ChatWidget()
        
        # 添加到布局
        layout.addWidget(self.friend_list)
        layout.addWidget(self.chat_widget)
        
        main_widget.setLayout(layout)
        
    def on_friends_list_received(self, friends):
        """处理收到的好友列表"""
        try:
            for friend in friends:
                self.friend_list.add_friend(
                    friend['avatar_path'],
                    friend['nickname']
                )
        except Exception as e:
            print(f"加载好友列表失败: {e}")
            
    async def on_friend_selected(self, friend_nickname):
        """处理好友选择事件"""
        try:
            print(f"选择好友: {friend_nickname}")
            self.current_friend = friend_nickname
            
            # 清空现有消息
            self.chat_widget.clear_messages()
            
            # 加载聊天记录
            print("正在请求聊天记录...")
            history = await self.chat_client.get_chat_history(friend_nickname)
            print(f"获取到聊天记录: {history}")
            
            if history is not None:
                print("开始加载聊天记录到UI")
                self.chat_widget.load_chat_history(
                    friend_nickname,
                    history,
                    'bubble_message/data/head1.jpg',  # 自己的头像
                    'bubble_message/data/head2.jpg'   # 好友的头像
                )
                print("聊天记录加载完成")
            else:
                print("获取聊天记录失败")
                
        except Exception as e:
            print(f"处理好友选择失败: {e}")
            QMessageBox.warning(self, "错误", f"加载聊天记录失败: {str(e)}")
        
    def on_message_received(self, from_id, from_nickname, content, message_type):
        """处理收到的消息"""
        try:
            if from_nickname == self.current_friend:
                self.chat_widget.add_message(
                    content=content,
                    is_send=False,
                    avatar_path='bubble_message/data/head2.jpg',
                    message_type=message_type
                )
        except Exception as e:
            print(f"处理收到的消息失败: {e}")
            
    def send_message(self, content):
        """发送消息"""
        try:
            if not self.current_friend:
                QMessageBox.warning(self, "错误", "请先选择聊天对象")
                return
                
            # 发送消息到服务器
            asyncio.create_task(self.chat_client.send_message(
                self.current_friend,
                content
            ))
            
            # 在本地显示消息
            # self.chat_widget.add_message(
            #     content,
            #     True,  # 发送的消息
            #     'bubble_message/data/head1.jpg',  # 自己的头像
            #     'text'  # 消息类型
            # )
        except Exception as e:
            print(f"发送消息失败: {e}")
            QMessageBox.warning(self, "错误", f"发送消息失败: {str(e)}")
            
    def on_history_received(self, messages):
        """处理收到的聊天记录"""
        try:
            print(f"收到聊天记录消息: {messages}")
            self.chat_widget.clear_messages()
            for msg in messages:
                print(f"处理消息: {msg}")
                is_send = msg.get('is_send', False)
                self.chat_widget.add_message(
                    msg['content'],
                    is_send,
                    'bubble_message/data/head1.jpg' if is_send else 'bubble_message/data/head2.jpg',
                    msg.get('type', 'text'),
                    msg.get('timestamp')
                )
            print("聊天记录显示完成")
        except Exception as e:
            print(f"显示聊天记录失败: {e}")
            
    def on_online_status_changed(self, user_id, status):
        """处理好友在线状态变化"""
        try:
            self.friend_list.update_friend_status(user_id, status)
        except Exception as e:
            print(f"更新好友状态失败: {e}")
        
    async def load_friends_list(self):
        """加载好友列表"""
        try:
            print(f"正在加载好友列表... (user_id={self.user_id})")
            await self.chat_client.get_friends_list(self.user_id)
        except Exception as e:
            print(f"加载好友列表失败: {e}")
            QMessageBox.warning(self, "错误", f"加载好友列表失败: {str(e)}")
        
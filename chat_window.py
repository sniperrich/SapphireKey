from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QMessageBox,QPushButton
from PyQt5.QtCore import Qt
from bubble_message import ChatWidget
from friendlist import FriendList

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
        self.my_avatar = None  # 存储自己的头像
        self.friend_avatars = {}  # 存储好友头像的字典
        
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
        """处理接收到的好友列表"""
        try:
            print(f"收到好友列表: {friends}")
            # self.friend_list.clear()
            for friend in friends:
                self.friend_avatars[friend['nickname']] = friend['avatar_path']  # 保存好友头像
                self.friend_list.add_friend(friend['avatar_path'], friend['nickname'])
        except Exception as e:
            print(f"处理好友列表失败: {e}")
            
    async def on_friend_selected(self, nickname):
        """处理好友选择事件"""
        try:
            print(f"选中好友: {nickname}")
            self.current_friend = nickname
            
            # 清空聊天记录
            self.chat_widget.clear_messages()
            
            # 设置聊天窗口的头像
            friend_avatar = self.friend_avatars.get(nickname)
            if friend_avatar:
                self.chat_widget.set_avatars(self.my_avatar, friend_avatar)
            
            # 获取聊天记录
            await self.chat_client.get_chat_history(nickname)
            
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
            print(f"处理收到的消��失败: {e}")
            
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
        
    def on_login_success(self, user_info):
        try:
            print("登录成功，正在打开聊天窗口...")
            print(f"用户信息: {user_info}")
            
            self.chat_window = ChatWindow(
                user_info['user_id'],
                user_info['username'],
                user_info['nickname'],
                self.chat_client
            )
            # 设置自己的头像
            self.chat_window.my_avatar = user_info['avatar_path']
            
            self.login_window.hide()
            self.chat_window.show()
            print("聊天窗口已打开")
        except Exception as e:
            print(f"打开聊天窗口失败: {e}")
            QMessageBox.critical(None, "错误", f"打开聊天窗口失败: {str(e)}")
        
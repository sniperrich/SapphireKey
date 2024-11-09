from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QMessageBox
from PyQt5.QtCore import Qt
from bubble_message import ChatWidget
from friendlist import FriendList
from chat_history import ChatHistory
import asyncio

class ChatWindow(QMainWindow):
    def __init__(self, username, nickname, chat_client):
        super().__init__()
        self.username = username
        self.nickname = nickname
        self.chat_client = chat_client
        self.current_friend = None
        self.init_ui()
        
        # 连接信号
        self.chat_client.message_received.connect(self.on_message_received)
        self.chat_client.history_received.connect(self.on_history_received)
        self.chat_client.online_status_changed.connect(self.on_online_status_changed)
        
        # 连接聊天窗口的消息发送信号
        self.chat_widget.message_sent.connect(self.send_message)
        
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
        self.friend_list = FriendList()
        self.friend_list.friend_selected.connect(self.on_friend_selected)
        
        # 创建聊天区域
        self.chat_widget = ChatWidget()
        
        # 添加到布局
        layout.addWidget(self.friend_list)
        layout.addWidget(self.chat_widget)
        
        main_widget.setLayout(layout)
        
        # 加载好友列表
        self.load_friends()
        
    def load_friends(self):
        """加载好友列表"""
        # 这里应该从数据库获取好友列表
        # 暂时添加测试数据
        self.friend_list.add_friend('bubble_message/data/head1.jpg', '张三')
        self.friend_list.add_friend('bubble_message/data/head2.jpg', '李四')
        self.friend_list.add_friend('bubble_message/data/head1.jpg', '王')
        
    def on_friend_selected(self, friend_nickname):
        """处理好友选择事件"""
        try:
            print(f"选择了好友：{friend_nickname}")
            self.current_friend = friend_nickname
            self.chat_widget.clear_messages()
            # 请求聊天记录
            asyncio.create_task(self.chat_client.get_chat_history(friend_nickname))
        except Exception as e:
            print(f"选择好友失败: {e}")
            
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
            self.chat_widget.add_message(
                content,
                True,  # 发送的消息
                'bubble_message/data/head1.jpg',  # 自己的头像
                'text'  # 消息类型
            )
        except Exception as e:
            print(f"发送消息失败: {e}")
            QMessageBox.warning(self, "错误", f"发送消息失败: {str(e)}")
            
    def on_history_received(self, messages):
        """处理收到的聊天记录"""
        try:
            self.chat_widget.clear_messages()
            for msg in messages:
                is_send = msg['from_nickname'] == self.nickname
                self.chat_widget.add_message(
                    msg['content'],
                    is_send,
                    'bubble_message/data/head1.jpg' if is_send else 'bubble_message/data/head2.jpg',
                    msg.get('message_type', 'text'),
                    msg.get('timestamp')
                )
        except Exception as e:
            print(f"显示聊天记录失败: {e}")
            
    def on_online_status_changed(self, user_id, status):
        """处理好友在线状态变化"""
        try:
            self.friend_list.update_friend_status(user_id, status)
        except Exception as e:
            print(f"更新好友状态失败: {e}")
        
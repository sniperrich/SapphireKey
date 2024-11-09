from PyQt5.QtWidgets import QWidget, QLabel, QHBoxLayout, QVBoxLayout, QListWidget, QListWidgetItem
from PyQt5.QtCore import Qt, pyqtSignal, QSize
from PyQt5.QtGui import QPixmap

class FriendItem(QWidget):
    def __init__(self, avatar_path, nickname):
        super().__init__()
        layout = QHBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        
        # 头像
        self.avatar_label = QLabel()
        pixmap = QPixmap(avatar_path).scaled(40, 40, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.avatar_label.setPixmap(pixmap)
        self.avatar_label.setFixedSize(40, 40)
        
        # 昵称
        self.nickname_label = QLabel(nickname)
        self.nickname_label.setObjectName("nickname")  # 设置对象名称
        self.nickname_label.setStyleSheet("""
            QLabel {
                font-family: 微软雅黑;
                font-size: 14px;
                padding-left: 10px;
            }
        """)
        
        layout.addWidget(self.avatar_label)
        layout.addWidget(self.nickname_label)
        layout.addStretch()
        self.setLayout(layout)
        
    def get_nickname(self):
        """获取好友昵称"""
        return self.nickname_label.text()

class FriendList(QWidget):
    friend_selected = pyqtSignal(str)  # 发送被选中好友的昵称
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        self.setMinimumWidth(250)
        
        # 创建好友列表
        self.list_widget = QListWidget()
        self.list_widget.setStyleSheet("""
            QListWidget {
                border: none;
                background-color: #f5f5f5;
            }
            QListWidget::item {
                padding: 5px;
            }
            QListWidget::item:selected {
                background-color: #e3e3e3;
            }
            QListWidget::item:hover {
                background-color: #ebebeb;
            }
        """)
        
        self.list_widget.itemClicked.connect(self.on_friend_selected)
        layout.addWidget(self.list_widget)
        self.setLayout(layout)
        
    def add_friend(self, avatar_path, nickname):
        """添加好友到列表"""
        item = QListWidgetItem()
        friend_widget = FriendItem(avatar_path, nickname)
        item.setSizeHint(friend_widget.sizeHint())
        
        self.list_widget.addItem(item)
        self.list_widget.setItemWidget(item, friend_widget)
        
    def on_friend_selected(self, item):
        """当好友被选中时触发"""
        friend_widget = self.list_widget.itemWidget(item)
        nickname = friend_widget.get_nickname()  # 使用新添加的方法获取昵称
        print(f"选中好友昵称：{nickname}")  # 调试信息
        self.friend_selected.emit(nickname)
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLineEdit, QPushButton, 
                            QLabel, QMessageBox)
from PyQt5.QtCore import pyqtSignal, Qt

class LoginWindow(QWidget):
    login_button_clicked = pyqtSignal(str, str)  # username, nickname
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle('登录')
        self.setFixedSize(300, 200)
        
        layout = QVBoxLayout()
        layout.setSpacing(10)
        
        # 状态标签
        self.status_label = QLabel('')
        self.status_label.setStyleSheet('''
            QLabel {
                color: red;
                font-size: 12px;
                padding: 5px;
            }
        ''')
        layout.addWidget(self.status_label)
        
        # 用户名输入框
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText('用户名')
        layout.addWidget(self.username_input)
        
        # 昵称输入框
        self.nickname_input = QLineEdit()
        self.nickname_input.setPlaceholderText('昵称')
        layout.addWidget(self.nickname_input)
        
        # 登录按钮
        self.login_button = QPushButton('登录')
        self.login_button.clicked.connect(self.on_login)
        layout.addWidget(self.login_button)
        
        self.setLayout(layout)
    
    def on_login(self):
        """处理登录按钮点击"""
        username = self.username_input.text().strip()
        nickname = self.nickname_input.text().strip()
        
        if not username or not nickname:
            self.show_error("用户名和昵称不能为空")
            return
        
        self.login_button.setEnabled(False)
        self.show_connecting()
        self.login_button_clicked.emit(username, nickname)
    
    def show_error(self, message):
        """显示错误信息"""
        self.status_label.setText(message)
        self.status_label.setStyleSheet('''
            QLabel {
                color: red;
                font-size: 12px;
                padding: 5px;
            }
        ''')
        self.login_button.setEnabled(True)
    
    def show_connecting(self):
        """显示连接中状态"""
        self.status_label.setText("正在连接服务器...")
        self.status_label.setStyleSheet('''
            QLabel {
                color: #666;
                font-size: 12px;
                padding: 5px;
            }
        ''')
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLineEdit, QPushButton, 
                            QLabel, QMessageBox)
from PyQt5.QtCore import pyqtSignal, Qt
from register_dialog import RegisterDialog
from chat_client import ChatClient
import asyncio


class LoginWindow(QWidget):
    login_success = pyqtSignal(dict)  # 发送用户信息
    
    def __init__(self, db=None, chat_client=None, parent=None):
        super().__init__(parent)
        self.db = db
        self.chat_client = chat_client
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        # 用户名输入
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("用户名")
        
        # 密码输入
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("密码")
        self.password_input.setEchoMode(QLineEdit.Password)
        
        # 登录按钮
        self.login_btn = QPushButton("登录")
        self.login_btn.clicked.connect(self.on_login_clicked)
        
        # 注册按钮
        self.register_btn = QPushButton("注册")
        self.register_btn.clicked.connect(self.show_register_dialog)
        
        # 添加到布局
        layout.addWidget(self.username_input)
        layout.addWidget(self.password_input)
        layout.addWidget(self.login_btn)
        layout.addWidget(self.register_btn)
        
        self.setLayout(layout)
        
    def on_login_clicked(self):
        """处理登录按钮点击"""
        loop = asyncio.get_event_loop()
        loop.create_task(self.handle_login())
        
    async def handle_login(self):
        """异步处理登录"""
        try:
            username = self.username_input.text().strip()
            password = self.password_input.text()
            
            if not username or not password:
                QMessageBox.warning(self, "错误", "请输入用户名和密码")
                return
                
            user_info = await self.chat_client.login(username, password)
            if user_info:
                # 使用 asyncio.create_task 来处理异步信号
                loop = asyncio.get_event_loop()
                loop.create_task(self._emit_login_success(user_info))
            else:
                QMessageBox.warning(self, "错误", "用户名或密码错误")
        except Exception as e:
            print(f"登录失败: {e}")
            QMessageBox.warning(self, "错误", f"登录失败: {str(e)}")
            
    async def _emit_login_success(self, user_info):
        """发送登录成功信号"""
        if user_info:  # 确保有用户信息
            print(f"发送登录成功信号，用户信息：{user_info}")
            self.login_success.emit(user_info)
        else:
            print("登录失败：未获取到用户信息")
            QMessageBox.warning(self, "错误", "登录失败：未获取到用户信息")
    
    def show_register_dialog(self):
        dialog = RegisterDialog(self)
        dialog.exec_()
    
    def show_error(self, message):
        """显示错误消息"""
        QMessageBox.warning(self, "错误", message)
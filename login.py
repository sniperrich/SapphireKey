from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLineEdit, QPushButton, 
                            QLabel, QMessageBox)
from PyQt5.QtCore import pyqtSignal, Qt

from register_dialog import RegisterDialog


class LoginWindow(QWidget):
    login_success = pyqtSignal(dict)  # 发送用户信息
    
    def __init__(self, db):
        super().__init__()
        self.db = db
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
        self.login_btn.clicked.connect(self.handle_login)
        
        # 注册按钮
        self.register_btn = QPushButton("注册")
        self.register_btn.clicked.connect(self.show_register_dialog)
        
        # 添加到布局
        layout.addWidget(self.username_input)
        layout.addWidget(self.password_input)
        layout.addWidget(self.login_btn)
        layout.addWidget(self.register_btn)
        
        self.setLayout(layout)
        
    def handle_login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text()
        
        if not username or not password:
            QMessageBox.warning(self, "错误", "请输入用户名和密码")
            return
            
        user = self.db.verify_user(username, password)
        if user:
            self.login_success.emit(user)
        else:
            QMessageBox.warning(self, "错误", "用户名或密码错误")
            
    def show_register_dialog(self):
        dialog = RegisterDialog(self.db, self)
        dialog.exec_()
    
    def show_error(self, message):
        """显示错误消息"""
        QMessageBox.warning(self, "错误", message)
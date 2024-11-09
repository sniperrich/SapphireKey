from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QLineEdit, 
                            QPushButton, QLabel, QMessageBox)

class RegisterDialog(QDialog):
    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        # 输入框
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("用户名")
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("密码")
        self.password_input.setEchoMode(QLineEdit.Password)
        
        self.confirm_password = QLineEdit()
        self.confirm_password.setPlaceholderText("确认密码")
        self.confirm_password.setEchoMode(QLineEdit.Password)
        
        self.nickname_input = QLineEdit()
        self.nickname_input.setPlaceholderText("昵称")
        
        # 注册按钮
        self.register_btn = QPushButton("注册")
        self.register_btn.clicked.connect(self.handle_register)
        
        # 添加到布局
        layout.addWidget(self.username_input)
        layout.addWidget(self.password_input)
        layout.addWidget(self.confirm_password)
        layout.addWidget(self.nickname_input)
        layout.addWidget(self.register_btn)
        
        self.setLayout(layout)
        
    def handle_register(self):
        """处理注册请求"""
        try:
            username = self.username_input.text().strip()
            password = self.password_input.text()
            confirm = self.confirm_password.text()
            nickname = self.nickname_input.text().strip()
            
            if not all([username, password, confirm, nickname]):
                QMessageBox.warning(self, "错误", "请填写所有字段")
                return
                
            if password != confirm:
                QMessageBox.warning(self, "错误", "两次输入的密码不一致")
                return
                
            # 默认头像
            avatar_path = 'bubble_message/data/head1.jpg'
            
            try:
                user_id = self.db.add_user(username, password, nickname, avatar_path)
                if user_id:
                    QMessageBox.information(self, "成功", "注册成功")
                    self.accept()
                else:
                    QMessageBox.warning(self, "错误", "注册失败，用户名可能已存在")
            except Exception as e:
                print(f"数据库操作失败: {e}")
                QMessageBox.critical(self, "错误", f"注册失败: {str(e)}")
                
        except Exception as e:
            print(f"注册处理失败: {e}")
            QMessageBox.critical(self, "错误", f"系统错误: {str(e)}")
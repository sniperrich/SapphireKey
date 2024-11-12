from PyQt5.QtWidgets import QApplication, QMessageBox
from login import LoginWindow
from chat_window import ChatWindow
from chat_client import ChatClient
import sys
import asyncio
from qasync import QEventLoop
from functools import partial
from database import Database

class ChatApp(QApplication):
    def __init__(self):
        super().__init__(sys.argv)
        # 初始化事件循环
        self.loop = QEventLoop(self)
        asyncio.set_event_loop(self.loop)
        
        # 初始化其他组件
        self.db = Database()
        self.chat_client = ChatClient()
        self.login_window = LoginWindow(self.db, self.chat_client)
        self.login_window.login_success.connect(self.on_login_success)
        self.login_window.show()
        
    def on_login_success(self, user_info):
        """登录成功处理"""
        try:
            print("登录成功，正在打开聊天窗口...")
            print(f"用户信息: {user_info}")
            
            self.chat_window = ChatWindow(
                user_info['user_id'],
                user_info['username'],
                user_info['nickname'],
                self.chat_client
            )
            self.login_window.hide()
            self.chat_window.show()
            print("聊天窗口已打开")
        except Exception as e:
            print(f"打开聊天窗口失败: {e}")
            QMessageBox.critical(None, "错误", f"打开聊天窗口失败: {str(e)}")
    
    def run(self):
        """运行应用"""
        try:
            with self.loop:
                self.loop.run_forever()
        except Exception as e:
            print(f"应用运行错误: {e}")
            QMessageBox.critical(None, "错误", f"应用运行错误: {str(e)}")

def main():
    try:
        chat_app = ChatApp()
        chat_app.run()
    except Exception as e:
        print(f"程序启动失败: {e}")
        QMessageBox.critical(None, "错误", f"程序启动失败: {str(e)}")

if __name__ == '__main__':
    main()

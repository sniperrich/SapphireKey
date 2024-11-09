from PyQt5.QtWidgets import QApplication, QMessageBox
from login import LoginWindow
from chat_window import ChatWindow
from chat_client import ChatClient
import sys
import asyncio
from qasync import QEventLoop
from functools import partial
from database import Database

class ChatApp:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.loop = QEventLoop(self.app)
        asyncio.set_event_loop(self.loop)
        
        # 创建数据库连接
        self.db = Database()
        
        # 创建登录窗口
        self.login_window = LoginWindow(self.db)
        # 使用 qasync 的方式连接信号
        self.login_window.login_success.connect(lambda user: asyncio.create_task(self.on_login_success(user)))
    
    async def on_login_success(self, user):
        """登录成功的处理"""
        try:
            # 创建聊天客户端
            self.chat_client = ChatClient()
            success = await self.chat_client.connect(user['username'])
            
            if success:
                # 创建主窗口，传入完整的用户信息
                self.chat_window = ChatWindow(
                    user['user_id'],  # 添加用户ID
                    user['username'], 
                    user['nickname'],
                    self.chat_client
                )
                self.chat_window.show()
                self.login_window.hide()
            else:
                QMessageBox.warning(self.login_window, "错误", "连接服务器失败")
        except Exception as e:
            print(f"登录错误: {str(e)}")
            QMessageBox.warning(self.login_window, "错误", f"连接错误: {str(e)}")
    
    def run(self):
        self.login_window.show()
        with self.loop:
            self.loop.run_forever()

def main():
    chat_app = ChatApp()
    chat_app.run()

if __name__ == '__main__':
    main()

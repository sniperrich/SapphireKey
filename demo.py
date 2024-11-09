from PyQt5.QtWidgets import QApplication
from login import LoginWindow
from chat_window import ChatWindow
from chat_client import ChatClient
import sys
import asyncio
from qasync import QEventLoop
from functools import partial

class ChatApp:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.loop = QEventLoop(self.app)
        asyncio.set_event_loop(self.loop)
        
        # 创建聊天客户端
        self.chat_client = ChatClient()
        
        # 创建登录窗口
        self.login_window = LoginWindow()
        self.login_window.login_button_clicked.connect(self.on_login_clicked)
    
    def on_login_clicked(self, username, nickname):
        """处理登录按钮点击事件"""
        # 使用 asyncio.create_task 来运行异步函数
        asyncio.create_task(self.handle_login(username, nickname))
    
    async def handle_login(self, username, nickname):
        """处理登录请求"""
        print(f"正在处理登录请求: username={username}, nickname={nickname}")
        try:
            success = await self.chat_client.connect(username)
            if success:
                print("连接服务器成功，创建聊天窗口...")
                # 创建主聊天窗口，传入chat_client
                self.chat_window = ChatWindow(username, nickname, self.chat_client)
                self.chat_window.show()
                self.login_window.hide()
            else:
                print("连接服务器失败")
                self.login_window.show_error("登录失败")
        except Exception as e:
            print(f"登录错误: {str(e)}")
            self.login_window.show_error(f"连接错误: {str(e)}")
    
    def run(self):
        self.login_window.show()
        with self.loop:
            self.loop.run_forever()

def main():
    chat_app = ChatApp()
    chat_app.run()

if __name__ == '__main__':
    main()

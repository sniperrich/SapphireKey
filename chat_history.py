import json
import os
from datetime import datetime

class ChatHistory:
    def __init__(self, history_dir=None):
        if history_dir is None:
            # 获取当前文件所在目录
            current_dir = os.path.dirname(os.path.abspath(__file__))
            self.history_dir = os.path.join(current_dir, "chat_history")
        else:
            self.history_dir = history_dir
            
        # 确保历史记录目录存在
        if not os.path.exists(self.history_dir):
            os.makedirs(self.history_dir)
        print(f"聊天记录目录：{self.history_dir}")  # 调试信息
    
    def get_history_file(self, friend_name):
        """获取指定好友的聊天记录文件路径"""
        file_path = os.path.join(self.history_dir, f"{friend_name}.json")
        print(f"聊天记录文件路径：{file_path}")  # 调试信息
        return file_path
    
    def load_history(self, friend_name):
        """加载指定好友的聊天记录"""
        file_path = self.get_history_file(friend_name)
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    history = json.load(f)
                    print(f"成功加载聊天记录：{history}")  # 调试信息
                    return history
            except Exception as e:
                print(f"加载聊天记录出错：{e}")
                return []
        else:
            print(f"聊天记录文件不存在：{file_path}")  # 调试信息
        return []
    
    def save_message(self, friend_name, content, is_send, message_type="text"):
        """保存新消息到聊天记录"""
        file_path = self.get_history_file(friend_name)
        history = self.load_history(friend_name)
        
        # 创建新消息
        message = {
            "content": content,
            "is_send": is_send,
            "type": message_type,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        history.append(message)
        
        # 保存到文件
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存聊天记录出错：{e}")
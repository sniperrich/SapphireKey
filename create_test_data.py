import json
import os
from datetime import datetime, timedelta

def create_test_chat_history():
    # 获取当前文件所在目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    history_dir = os.path.join(current_dir, "chat_history")
    
    # 确保目录存在
    if not os.path.exists(history_dir):
        os.makedirs(history_dir)
    
    # 张三的聊天记录
    zhangsan_history = [
        {
            "content": "你好啊",
            "is_send": True,
            "type": "text",
            "timestamp": (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d %H:%M:%S")
        },
        {
            "content": "最近怎么样？",
            "is_send": False,
            "type": "text",
            "timestamp": (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d %H:%M:%S")
        }
    ]
    
    # 李四的聊天记录
    lisi_history = [
        {
            "content": "在吗？",
            "is_send": False,
            "type": "text",
            "timestamp": (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d %H:%M:%S")
        },
        {
            "content": "我这有个问题想请教你",
            "is_send": False,
            "type": "text",
            "timestamp": (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d %H:%M:%S")
        }
    ]
    
    # 保存聊天记录
    with open(os.path.join(history_dir, "张三.json"), "w", encoding="utf-8") as f:
        json.dump(zhangsan_history, f, ensure_ascii=False, indent=2)
    
    with open(os.path.join(history_dir, "李四.json"), "w", encoding="utf-8") as f:
        json.dump(lisi_history, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    create_test_chat_history() 
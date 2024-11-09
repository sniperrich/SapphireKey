from database import Database
import os

def init_database():
    print("开始初始化数据库...")
    
    # 如果数据库文件已存在，先删除它
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "chat.db")
    if os.path.exists(db_path):
        print(f"删除已存在的数据库文件: {db_path}")
        os.remove(db_path)
    
    db = Database()
    
    # 添加测试用户
    print("\n添加测试用户...")
    zhangsan = db.add_user('user1', '张三', 'bubble_message/data/head1.jpg')
    if zhangsan is None:
        print("添加张三失败")
        return
        
    lisi = db.add_user('user2', '李四', 'bubble_message/data/head2.jpg')
    if lisi is None:
        print("添加李四失败")
        return
        
    wangwu = db.add_user('user3', '王五', 'bubble_message/data/head1.jpg')
    if wangwu is None:
        print("添加王五失败")
        return
    
    print(f"\n用户ID: 张三={zhangsan}, 李四={lisi}, 王五={wangwu}")
    
    # 添加好友关系
    print("\n添加好友关系...")
    db.add_friend(zhangsan, lisi)
    db.add_friend(zhangsan, wangwu)
    db.add_friend(lisi, wangwu)
    
    print("\n数据库初始化完成！")

if __name__ == "__main__":
    init_database() 
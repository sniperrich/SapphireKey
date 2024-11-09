from database import Database

def init_test_data():
    db = Database()
    
    # 添加测试用户（添加密码参数）
    zhangsan_id = db.add_user('user1', '123456', '张三', 'bubble_message/data/head1.jpg')
    lisi_id = db.add_user('user2', '123456', '李四', 'bubble_message/data/head2.jpg')
    wangwu_id = db.add_user('user3', '123456', '王五', 'bubble_message/data/head1.jpg')
    
    # 添加好友关系
    db.add_friend(zhangsan_id, lisi_id)
    db.add_friend(zhangsan_id, wangwu_id)
    db.add_friend(lisi_id, wangwu_id)
    
    print("测试数据初始化完成！")
    print(f"张三ID: {zhangsan_id}")
    print(f"李四ID: {lisi_id}")
    print(f"王五ID: {wangwu_id}")

if __name__ == "__main__":
    init_test_data() 
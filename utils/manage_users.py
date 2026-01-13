import os
import sys

# 将项目根目录添加到 python 路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.models import UserDB
from sqlalchemy import text

def list_users():
    db = SessionLocal()
    try:
        users = db.query(UserDB).all()
        print("\n--- 用户列表 ---")
        print(f"{'ID':<5} {'姓名':<10} {'学号':<15} {'角色':<10}")
        print("-" * 40)
        for user in users:
            print(f"{user.id:<5} {user.name:<10} {user.student_number:<15} {user.role:<10}")
        print("-" * 40)
    finally:
        db.close()

def update_role(student_number, new_role):
    if new_role not in ['customer', 'staff']:
        print("错误: 角色必须是 'customer' 或 'staff'")
        return

    db = SessionLocal()
    try:
        user = db.query(UserDB).filter(UserDB.student_number == student_number).first()
        if not user:
            print(f"未找到学号为 {student_number} 的用户")
            return
        
        user.role = new_role
        db.commit()
        print(f"成功将用户 {user.name} ({student_number}) 的角色更新为: {new_role}")
    except Exception as e:
        db.rollback()
        print(f"更新失败: {e}")
    finally:
        db.close()

def main():
    while True:
        print("\n=== 曙光咖啡厅 用户后台管理 ===")
        print("1. 查看所有用户")
        print("2. 修改用户角色")
        print("q. 退出")
        
        choice = input("\n请选择操作: ").strip().lower()
        
        if choice == '1':
            list_users()
        elif choice == '2':
            s_num = input("请输入用户学号: ").strip()
            role = input("请输入新角色 (customer/staff): ").strip().lower()
            update_role(s_num, role)
        elif choice == 'q':
            break
        else:
            print("无效选择，请重试。")

if __name__ == "__main__":
    main()

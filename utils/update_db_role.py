from sqlalchemy import text
from app.database import engine

def update_database():
    try:
        with engine.connect() as connection:
            # 检查是否已存在 role 列
            result = connection.execute(text("SHOW COLUMNS FROM users LIKE 'role'"))
            column_exists = result.fetchone()
            
            if not column_exists:
                print("正在为 users 表添加 role 列...")
                connection.execute(text("ALTER TABLE users ADD COLUMN role VARCHAR(20) DEFAULT 'customer'"))
                connection.commit()
                print("role 列添加成功！")
            else:
                print("role 列已存在，跳过。")
                
    except Exception as e:
        print(f"更新数据库失败: {e}")

if __name__ == "__main__":
    update_database()

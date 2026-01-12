import sys
import os

# 将项目根目录添加到 python 路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import database
from sqlalchemy import text

def reset_order_ids():
    db = next(database.get_db())
    try:
        print("正在清理订单相关数据并重置 ID 计数器...")
        
        # 禁用外键检查以允许截断表
        db.execute(text("SET FOREIGN_KEY_CHECKS = 0;"))
        
        # 截断表（这会删除所有数据并重置 AUTO_INCREMENT）
        db.execute(text("TRUNCATE TABLE order_items;"))
        db.execute(text("TRUNCATE TABLE orders;"))
        
        # 重新启用外键检查
        db.execute(text("SET FOREIGN_KEY_CHECKS = 1;"))
        
        db.commit()
        print("重置成功！现在新的订单 ID 将从 1 开始。")
    except Exception as e:
        db.rollback()
        print(f"重置失败: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    confirm = input("这将删除所有现有的订单数据，确定要重置吗？(y/n): ")
    if confirm.lower() == 'y':
        reset_order_ids()
    else:
        print("操作已取消。")

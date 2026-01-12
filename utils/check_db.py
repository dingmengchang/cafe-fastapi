import sys
import os

# 将项目根目录添加到 python 路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import database, models
from sqlalchemy import text

def check_db_status():
    db = next(database.get_db())
    try:
        # 查询当前最大 ID
        max_id = db.query(models.OrderDB.id).order_by(models.OrderDB.id.desc()).first()
        print(f"当前数据库中最大的 Order ID: {max_id[0] if max_id else '无数据'}")
        
        # 查询 MySQL 的 AUTO_INCREMENT 状态
        result = db.execute(text("SHOW TABLE STATUS LIKE 'orders'"))
        row = result.fetchone()
        if row:
            # 在 MySQL 中，AUTO_INCREMENT 值通常在结果集的第 11 列（索引 10）
            # 或者通过列名获取
            auto_inc = dict(row._mapping).get('Auto_increment')
            print(f"下一条记录将使用的 ID (Auto_increment): {auto_inc}")
    except Exception as e:
        print(f"查询失败: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_db_status()

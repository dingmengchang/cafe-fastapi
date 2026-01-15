from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv
from urllib.parse import quote_plus

# 加载 .env 文件 (在 app 目录的父目录中)
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))

# 优先尝试从常见的环境变量名获取
SQLALCHEMY_DATABASE_URL = (
    os.getenv("DATABASE_URL") or 
    os.getenv("MYSQL_URL") or 
    os.getenv("POSTGRES_URL")
)

if not SQLALCHEMY_DATABASE_URL:
    # 如果没有直接的 URL，则通过各组件构建
    DB_USER = os.getenv("DB_USER", "root")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "3306")
    DB_NAME = os.getenv("DB_NAME", "waimai")
    
    encoded_password = quote_plus(DB_PASSWORD)
    SQLALCHEMY_DATABASE_URL = f"mysql+pymysql://{DB_USER}:{encoded_password}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# 兼容性处理：Zeabur/Render 的 PostgreSQL URL 可能以 postgres:// 开头，但 SQLAlchemy 需要 postgresql://
if SQLALCHEMY_DATABASE_URL and SQLALCHEMY_DATABASE_URL.startswith("postgres://"):
    SQLALCHEMY_DATABASE_URL = SQLALCHEMY_DATABASE_URL.replace("postgres://", "postgresql://", 1)

# 如果是 MySQL URL 且没有指定驱动，添加 pymysql
if SQLALCHEMY_DATABASE_URL and SQLALCHEMY_DATABASE_URL.startswith("mysql://"):
    SQLALCHEMY_DATABASE_URL = SQLALCHEMY_DATABASE_URL.replace("mysql://", "mysql+pymysql://", 1)

# 创建引擎
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建基类供模型继承
Base = declarative_base()

# 获取数据库会话的依赖项
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

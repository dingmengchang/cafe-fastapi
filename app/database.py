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
    # 优先匹配 Zeabur 自动生成的变量名
    DB_USER = os.getenv("MYSQL_USERNAME") or os.getenv("DB_USER") or "root"
    DB_PASSWORD = os.getenv("MYSQL_PASSWORD") or os.getenv("DB_PASSWORD") or ""
    DB_HOST = os.getenv("MYSQL_HOST") or os.getenv("DB_HOST") or "localhost"
    DB_PORT = os.getenv("MYSQL_PORT") or os.getenv("DB_PORT") or "3306"
    DB_NAME = os.getenv("MYSQL_DATABASE") or os.getenv("DB_NAME") or "waimai"
    
    encoded_password = quote_plus(DB_PASSWORD)
    SQLALCHEMY_DATABASE_URL = f"mysql+pymysql://{DB_USER}:{encoded_password}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# 兼容性处理：Zeabur/Render 的 PostgreSQL URL 可能以 postgres:// 开头，但 SQLAlchemy 需要 postgresql://
if SQLALCHEMY_DATABASE_URL and SQLALCHEMY_DATABASE_URL.startswith("postgres://"):
    SQLALCHEMY_DATABASE_URL = SQLALCHEMY_DATABASE_URL.replace("postgres://", "postgresql://", 1)

# 如果是 MySQL URL 且没有指定驱动，添加 pymysql
if SQLALCHEMY_DATABASE_URL and SQLALCHEMY_DATABASE_URL.startswith("mysql://"):
    SQLALCHEMY_DATABASE_URL = SQLALCHEMY_DATABASE_URL.replace("mysql://", "mysql+pymysql://", 1)

# 创建引擎
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    # 增加连接池配置，提高稳定性
    pool_pre_ping=True,
    pool_recycle=3600
)

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

from fastapi import FastAPI, HTTPException, Response, Depends, Request
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from enum import Enum # 枚举类型
from fastapi.middleware.cors import CORSMiddleware # 跨域资源共享
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import os
import bcrypt
from typing import List

# 极其早期的日志，用于排查启动问题
print("--- APP STARTING ---")
print(f"Current Directory: {os.getcwd()}")
print(f"Environment PORT: {os.getenv('PORT')}")

from sqlalchemy.orm import Session
from . import database, models

# 设置基础目录
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")
STATIC_DIR = os.path.join(BASE_DIR, "static")

# 密码哈希逻辑
def get_password_hash(password: str):
    pwd_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(pwd_bytes, salt)
    return hashed.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str):
    try:
        return bcrypt.checkpw(
            plain_password.encode('utf-8'),
            hashed_password.encode('utf-8')
        )
    except Exception:
        return plain_password == hashed_password

# 初始化数据库表
try:
    print(f"Connecting to database: {database.SQLALCHEMY_DATABASE_URL.split('@')[-1] if '@' in database.SQLALCHEMY_DATABASE_URL else 'unknown'}")
    models.Base.metadata.create_all(bind=database.engine)
    print("Database tables initialized successfully.")
except Exception as e:
    print(f"WARNING: Database initialization failed: {e}")
    print("Application will continue to start, but database features may be unavailable.")

app = FastAPI()

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc), "type": type(exc).__name__},
    )

# 挂载静态文件目录
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# 允许跨域
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return FileResponse(os.path.join(STATIC_DIR, "images", "icon.jpg"))

# Pydantic 模型
class User(BaseModel):
    name: str
    student_number: str
    phone_number: str
    password: str
    role: str = "customer"

class LoginRequest(BaseModel):
    student_number: str
    password: str

class OrderItemRequest(BaseModel):
    name: str
    price: float
    quantity: int

class OrderRequest(BaseModel):
    student_number: str
    total_price: float
    items: List[OrderItemRequest]

class OrderStatusUpdate(BaseModel):
    status: str

# 路由定义
@app.get("/", response_class=HTMLResponse)
async def root():
    path = os.path.join(TEMPLATE_DIR, "register.html")
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

@app.get("/register", response_class=HTMLResponse)
async def get_register():
    path = os.path.join(TEMPLATE_DIR, "register.html")
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

@app.get("/login", response_class=HTMLResponse)
async def get_login():
    path = os.path.join(TEMPLATE_DIR, "login.html")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    return "Login page not found."

@app.get("/menu", response_class=HTMLResponse)
async def get_menu():
    path = os.path.join(TEMPLATE_DIR, "menu.html")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    return "Menu page not found."

@app.get("/orders", response_class=HTMLResponse)
async def get_orders_page():
    path = os.path.join(TEMPLATE_DIR, "orders.html")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    return "Orders page not found."

@app.get("/api/admin/orders")
async def get_all_orders(db: Session = Depends(database.get_db)):
    orders = db.query(models.OrderDB).order_by(models.OrderDB.created_at.desc()).all()
    result = []
    for order in orders:
        user = db.query(models.UserDB).filter(models.UserDB.id == order.user_id).first()
        items = db.query(models.OrderItemDB).filter(models.OrderItemDB.order_id == order.id).all()
        result.append({
            "id": order.id,
            "user_name": user.name if user else "未知用户",
            "student_number": user.student_number if user else "N/A",
            "total_price": order.total_price,
            "status": order.status,
            "created_at": order.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "items": [{"name": item.product_name, "quantity": item.quantity, "price": item.price} for item in items]
        })
    return result

@app.patch("/api/admin/orders/{order_id}/status")
async def update_order_status(order_id: int, update: OrderStatusUpdate, db: Session = Depends(database.get_db)):
    order = db.query(models.OrderDB).filter(models.OrderDB.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="订单未找到")
    
    order.status = update.status
    db.commit()
    return {"message": f"订单状态已更新为 {update.status}"}

@app.post("/api/register")
async def create_user(user: User, db: Session = Depends(database.get_db)):
    db_user = db.query(models.UserDB).filter(models.UserDB.student_number == user.student_number).first()
    if db_user:
        raise HTTPException(status_code=400, detail="该学号已注册")
    hashed_password = get_password_hash(user.password)
    new_user = models.UserDB(
        name=user.name,
        student_number=user.student_number,
        phone_number=user.phone_number,
        password=hashed_password,
        role="customer"  # 注册时强制默认为客户
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "注册成功", "user": {"name": new_user.name, "student_number": new_user.student_number, "role": new_user.role}}

@app.post("/api/login")
async def login(login_data: LoginRequest, db: Session = Depends(database.get_db)):
    db_user = db.query(models.UserDB).filter(models.UserDB.student_number == login_data.student_number).first()
    if db_user and verify_password(login_data.password, db_user.password):
        return {
            "message": "登录成功", 
            "user": {
                "name": db_user.name, 
                "student_number": db_user.student_number,
                "role": db_user.role
            }
        }
    raise HTTPException(status_code=401, detail="学号或密码错误")

@app.post("/api/orders")
async def create_order(order_data: OrderRequest, db: Session = Depends(database.get_db)):
    db_user = db.query(models.UserDB).filter(models.UserDB.student_number == order_data.student_number).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="用户不存在")
    new_order = models.OrderDB(
        user_id=db_user.id,
        total_price=order_data.total_price,
        status="pending"
    )
    db.add(new_order)
    db.commit()
    db.refresh(new_order)
    for item in order_data.items:
        new_item = models.OrderItemDB(
            order_id=new_order.id,
            product_name=item.name,
            price=item.price,
            quantity=item.quantity
        )
        db.add(new_item)
    db.commit()
    return {"message": "订单已提交", "order_id": new_order.id}

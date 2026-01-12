from fastapi import FastAPI, HTTPException, Response, Depends, Request
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from enum import Enum # 枚举类型
from fastapi.middleware.cors import CORSMiddleware # 跨域资源共享
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import os
from sqlalchemy.orm import Session
from . import database, models
import bcrypt
from typing import List

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
models.Base.metadata.create_all(bind=database.engine)

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
        password=hashed_password
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "注册成功", "user": {"name": new_user.name, "student_number": new_user.student_number}}

@app.post("/api/login")
async def login(login_data: LoginRequest, db: Session = Depends(database.get_db)):
    db_user = db.query(models.UserDB).filter(models.UserDB.student_number == login_data.student_number).first()
    if db_user and verify_password(login_data.password, db_user.password):
        return {
            "message": "登录成功", 
            "user": {
                "name": db_user.name, 
                "student_number": db_user.student_number
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

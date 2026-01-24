# 曙光咖啡厅管理系统 (Waimai System)

基于 FastAPI 开发的曙光咖啡厅管理系统，支持用户下单、订单状态追踪以及店员端订单管理。

## 🌟 主要功能

- **用户系统**：支持学生注册与登录，密码采用 bcrypt 加密存储。
- **角色分类**：系统分为 **客户 (Customer)** 和 **店员 (Staff)** 两种角色。
  - 注册默认为客户。
  - 店员角色由后台脚本管理，确保安全性。
- **菜单与下单**：用户可在线浏览菜单、选择商品并提交订单。
- **订单管理 (店员端)**：
  - 分类查看“待处理”和“已完成”订单。
  - 一键更新订单状态。
- **数据库集成**：使用 SQLAlchemy ORM 框架，支持 MySQL/SQLite 灵活切换。

## 🛠️ 技术栈

- **后端**: FastAPI (Python)
- **数据库**: MySQL / SQLAlchemy ORM
- **前端**: HTML, CSS, JavaScript (原生), Jinja2 模板
- **安全**: bcrypt 密码哈希
- **运行环境**: Uvicorn

## 🚀 快速开始

### 1. 克隆项目
```bash
git clone <your-repo-url>
cd waimai
```

### 2. 安装依赖
建议使用虚拟环境：
```bash
pip install -r requirements.txt
```

### 3. 数据库配置
在 `app/database.py` 中配置您的数据库连接字符串。默认支持本地 MySQL：
```python
SQLALCHEMY_DATABASE_URL = "mysql+pymysql://user:password@localhost/waimai"
```

### 4. 运行应用
```bash
uvicorn app.main:app --reload
```
访问：`http://127.0.0.1:8000`

## 👥 角色管理

由于店员权限较高，系统不支持在前台直接注册为店员。如需修改用户角色，请使用内置脚本：

```bash
python utils/manage_users.py
```
按照提示输入学号，即可将其设为店员或恢复为普通客户。

## 📂 项目结构

```text
waimai/
├── app/
│   ├── main.py          # 程序入口，路由定义
│   ├── models.py        # 数据库模型 (User, Order, OrderItem)
│   └── database.py      # 数据库连接配置
├── static/              # 静态资源 (CSS, JS, Images)
├── templates/           # HTML 模板 (Jinja2)
├── utils/               # 工具脚本 (如角色管理)
├── requirements.txt     # 项目依赖
└── .gitignore           # Git 忽略文件
```

## 📝 开发计划
- [x] 订单分类显示（待处理/已完成）
- [x] 密码哈希加密
- [x] 后台用户权限管理
- [ ] 接入支付模拟接口
- [ ] 完善移动端适配

---
*本项目不涉及任何商业用途。*

# Community Forum API（社区论坛 - 用户模块后端）

基于 **FastAPI + SQLAlchemy 2.0 + MySQL 8.0** 的社区论坛后端工程，前后端分离，**仅实现用户模块**（注册 / 登录 / 刷新 token / 个人资料 / 查看他人主页），不包含帖子、评论、点赞、关注等业务。

## 技术栈

| 分类       | 选型                                              |
| ---------- | ------------------------------------------------- |
| Web 框架   | FastAPI                                           |
| ORM        | SQLAlchemy 2.0（DeclarativeBase + Mapped）        |
| 数据校验   | Pydantic v2 / pydantic-settings                   |
| 数据库     | MySQL 8.0（驱动默认 PyMySQL，可切换 mysqlclient） |
| 数据库迁移 | Alembic                                           |
| 密码加密   | passlib + bcrypt                                  |
| 鉴权       | JWT（access_token + refresh_token，python-jose）  |
| 日志       | logging（控制台 + 文件滚动）                      |

## 目录结构

```
community/
├── main.py                  # 入口：日志、CORS、全局异常、路由注册
├── config.py                # 全局配置（读取 .env）
├── .env                     # 环境变量（数据库、JWT 密钥等，勿提交仓库）
├── .gitignore
├── requirements.txt
├── README.md
├── alembic.ini
├── alembic/
│   ├── env.py               # 从 .env 读取数据库地址 + 加载模型元数据
│   └── versions/            # 迁移脚本
├── app/
│   ├── database.py          # 引擎 / SessionLocal / Base / get_db
│   ├── dependencies.py      # JWT 依赖，获取当前登录用户
│   ├── exceptions.py        # 自定义异常 + 全局异常捕获
│   ├── models/user.py       # User ORM 模型
│   ├── schemas/             # 请求/响应 schema（user.py、common.py）
│   ├── crud/crud_user.py     # 纯数据库操作
│   ├── api/auth.py          # 用户相关接口
│   ├── api/router.py        # 子路由汇总
│   └── utils/               # jwt_util.py、password_util.py
└── logs/app.log
```

## 一、环境准备

要求：Python 3.10+、MySQL 8.0。

```bash
# 1. 创建并激活虚拟环境（Windows PowerShell）
python -m venv .venv
.venv\Scripts\Activate.ps1

# macOS / Linux
# python -m venv .venv && source .venv/bin/activate

# 2. 安装依赖
pip install -r requirements.txt
```

> 说明：默认使用 **PyMySQL** 驱动（`mysql+pymysql://`），开箱即用。
> 如需 MySQL 官方驱动 `mysqlclient`（`mysql+mysqldb://`），先取消 `requirements.txt` 中该行注释再安装（Windows 需要编译环境，通常建议安装对应的 wheel）。

## 二、新建 MySQL 数据库

```sql
CREATE DATABASE IF NOT EXISTS `community`
  DEFAULT CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;
```

> 表结构不需要手工创建，交给 Alembic 迁移完成。

## 三、修改 .env

打开项目根目录的 `.env`，至少修改数据库账号密码和 JWT 密钥：

```dotenv
DATABASE_URL=mysql+pymysql://root:你的密码@127.0.0.1:3306/community?charset=utf8mb4
SECRET_KEY=换成随机长密钥
```

生成随机密钥：

```bash
python -c "import secrets;print(secrets.token_hex(32))"
```

其他可调项：`ACCESS_TOKEN_EXPIRE_MINUTES`（access_token 有效期，默认 30 分钟）、`REFRESH_TOKEN_EXPIRE_DAYS`（refresh_token 有效期，默认 7 天）、`CORS_ORIGINS`（逗号分隔的前端地址，`*` 表示全部放开）、`LOG_LEVEL`、`LOG_FILE`。

## 四、数据库迁移（Alembic）

```bash
# 执行迁移，创建 users 表（仓库已内置初始迁移脚本）
alembic upgrade head

# 查看当前版本 / 历史
alembic current
alembic history --verbose

# 回滚一个版本
alembic downgrade -1

# 修改模型后生成新的迁移脚本
alembic revision --autogenerate -m "add xxx column"
```

## 五、启动服务

```bash
# 方式一（推荐开发使用，自动重载）
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# 方式二
python main.py
```

- 接口文档（Swagger UI）：<http://127.0.0.1:8000/docs>
- 备用文档（ReDoc）：<http://127.0.0.1:8000/redoc>
- 健康检查：<http://127.0.0.1:8000/health>

## 六、接口清单

统一返回格式：`{"code": int, "msg": str, "data": any}`，成功 `code=200`，参数错误 `400`，未登录 `401`，权限不足 `403`，数据不存在 `404`，服务异常 `500`。

| 方法 | 路径                      | 是否登录 | 说明                                               |
| ---- | ------------------------- | -------- | -------------------------------------------------- |
| POST | `/api/auth/register`      | 否       | 注册（username、email、password），用户名/邮箱唯一 |
| POST | `/api/auth/login`         | 否       | 登录（username 或 email + password），返回双 token |
| POST | `/api/auth/refresh-token` | 否       | 用 refresh_token 换新 access_token                 |
| GET  | `/api/user/me`            | 是       | 获取自己的信息                                     |
| PUT  | `/api/user/me`            | 是       | 修改自己的 avatar / bio（不可改 username、email）  |
| GET  | `/api/user/uid/{uid}`     | 是       | 按用户唯一标识 uid 查询用户公开信息                |
| GET  | `/api/user/{user_id}`     | 是       | 查看他人主页公开信息                               |
| GET  | `/health`                 | 否       | 健康检查                                           |

鉴权方式：请求头 `Authorization: Bearer <access_token>`。

> `uid` 是注册时自动生成的 32 位十六进制用户唯一标识（唯一索引 `uk_uid`），对外用它区分用户，避免暴露自增主键 `id`。

## 七、curl 测试示例

以下示例假设服务运行在 `http://127.0.0.1:8000`。Windows PowerShell 中把行尾的 `\` 换成反引号 `` ` `` 或直接写成一行。

### 1. 注册

```bash
curl -X POST "http://127.0.0.1:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"username":"tom","email":"tom@example.com","password":"123456"}'
```

```json
{
  "code": 200,
  "msg": "注册成功",
  "data": {
    "id": 1,
    "uid": "9f2c7a1b3d4e5f60718293a4b5c6d7e8",
    "username": "tom",
    "email": "tom@example.com",
    "nickname": "tom",
    "avatar": null,
    "signature": null,
    "status": 1,
    "level": 0,
    "points": 0,
    "last_login_at": null,
    "created_at": "2025-01-01T12:00:00",
    "updated_at": "2025-01-01T12:00:00"
  }
}
```

重复注册（用户名已存在）：

```json
{ "code": 400, "msg": "用户名已存在", "data": null }
```

### 2. 登录

```bash
curl -X POST "http://127.0.0.1:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"tom@example.com","password":"123456"}'
```

也可以用用户名登录：`-d '{"username":"tom","password":"123456"}'`

```json
{
  "code": 200,
  "msg": "登录成功",
  "data": {
    "access_token": "eyJhbGciOi...",
    "refresh_token": "eyJhbGciOi...",
    "token_type": "bearer",
    "expires_in": 1800
  }
}
```

### 3. 刷新 access_token

```bash
curl -X POST "http://127.0.0.1:8000/api/auth/refresh-token" \
  -H "Content-Type: application/json" \
  -d '{"refresh_token":"<登录返回的 refresh_token>"}'
```

### 4. 获取自己的信息

```bash
curl -X GET "http://127.0.0.1:8000/api/user/me" \
  -H "Authorization: Bearer <access_token>"
```

未携带 token：

```json
{ "code": 401, "msg": "未携带 token，请先登录", "data": null }
```

### 5. 修改自己的资料

```bash
curl -X PUT "http://127.0.0.1:8000/api/user/me" \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{"avatar":"https://cdn.example.com/avatar/tom.png","bio":"这个人很懒，什么都没留下"}'
```

尝试修改 username（被拒绝，返回参数错误）：

```bash
curl -X PUT "http://127.0.0.1:8000/api/user/me" \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{"username":"new_name"}'
```

```json
{ "code": 400, "msg": "username: Extra inputs are not permitted", "data": null }
```

### 6. 查看他人主页

```bash
curl -X GET "http://127.0.0.1:8000/api/user/2" \
  -H "Authorization: Bearer <access_token>"
```

用户不存在：

```json
{ "code": 404, "msg": "用户不存在", "data": null }
```

### 7. 按 uid 查询用户

```bash
curl -X GET "http://127.0.0.1:8000/api/user/uid/9f2c7a1b3d4e5f60718293a4b5c6d7e8" \
  -H "Authorization: Bearer <access_token>"
```

```json
{
  "code": 200,
  "msg": "success",
  "data": {
    "id": 1,
    "uid": "9f2c7a1b3d4e5f60718293a4b5c6d7e8",
    "username": "tom",
    "nickname": "tom",
    "avatar": null,
    "signature": null,
    "level": 0,
    "points": 0,
    "created_at": "2025-01-01T12:00:00"
  }
}
```

## 八、分层约定

| 层             | 职责                                | 禁止事项                                        |
| -------------- | ----------------------------------- | ----------------------------------------------- |
| `models`       | 只定义表结构                        | 不写业务逻辑                                    |
| `schemas`      | 请求校验 / 响应序列化               | 不依赖 ORM 实例内部状态，不返回 `password_hash` |
| `crud`         | 纯数据库增删改查                    | 不判断权限、不签发 token、不做业务规则          |
| `api`          | 路由、参数校验、权限判断、调用 crud | 不直接写 SQL                                    |
| `dependencies` | JWT 依赖、当前用户获取              | 不写业务分支                                    |
| `utils`        | JWT 编解码、密码哈希等工具          | 不混入业务逻辑                                  |
| `exceptions`   | 自定义异常 + 全局捕获               | 不返回堆栈给前端                                |

## 九、常见问题

- **`ModuleNotFoundError: No module named 'config'`**：请在 `community/` 目录下启动，`alembic.ini` 中的 `prepend_sys_path = .` 已处理迁移场景。
- **`mysqlclient` 安装失败**：Windows 缺编译环境，直接使用默认的 PyMySQL 驱动即可。
- **bcrypt 密码长度**：bcrypt 最多处理 72 字节，密码 schema 已限制 6-72 位，工具层也做了字节截断保护。
- **401 / 403 区分**：未登录或 token 无效返回 401；账号被禁用 / 待激活返回 403。

# 用户鉴权模块

## 1. 模块概述

用户鉴权模块主要负责用户身份认证和接口访问权限控制，
包含了用户注册、用户登录、密码加密、JWT Token生成与校验等功能。

### 主要流程
用户注册：
用户提交账号密码 → 密码bcrypt加密 → 保存用户信息到数据库

用户登录：
用户提交账号密码 → 查询用户 → bcrypt验证密码 → 生成JWT Token → 返回客户端

接口访问：
客户携带JWT Token → 服务端解析Token → 获取用户身份 → 注入当前用户信息 → 执行业务

### 整体流程
注册流程：
```text
    User
     ↓
  Auth Router
     ↓
  Auth Service
     ↓
Password加密/JWT生成
     ↓
  Database
```
登录流程：
```text
    User
     ↓
 Auth Router
     ↓
 Auth Service
     ↓
 Database查询用户
     ↓
  bcrypt验证密码
     ↓
   JWT生成
     ↓
  返回Token
```
鉴权流程：
```text
  用户请求业务接口
       |
       |
   携带JWT Token
       |
       |
  get_current_user
       |
       |
  Token Decode
       |
       |
    get User
       |
       |
    Service
```

## 2. 模块结构
```text
app/
├── api/
│   └── auth.py             # 注册、登录接口
├── auth/
│   ├── jwt.py              # JWT生成与解析
│   ├── password.py         # 密码加密与验证
│   └── dependencies.py     # 用户身份解析依赖
│
│
├── services/
│   └── auth_service.py     # 用户认证业务逻辑
│
└── models/
    └── user.py             # 用户数据库模型
```

## 3. 用户注册流程

### 3.1 请求入口

接口：
```text
Post /auth/register
```
请求：
```text
{
    "username":"admin",
    "password":"123456"
}
```
代码：
```text
user = await create_user_service(
    db=db,
    username=request.username,
    password=request.password
)
```
Router层负责：
- 接受请求
- 参数校验
- 调用Service

### 3.2 密码加密
用户密码不会直接存入数据库，而是使用bcrypt进行哈希处理。
流程：
```text
明文密码
   ↓
bcrypt+salt
   ↓
 密码Hash值
   ↓
 数据库保存
```

## 4. 用户登录流程
接口：
```text
POST /auth/login
```
请求：
```text
{
    "username":"admin",
    "password":"123456"
}
```

流程：
```text
用户输入账号密码
     |
     ↓
 查询数据库用户
     |
     ↓
获取bcrypt密码Hash
     |
     ↓
verify_password()
     |
     ↓
   密码正确
     |
     ↓
create_access_token()
     |
     ↓
 返回JWT Token 
     
```

## 5. 密码验证机制

登录时不会直接比较密码字符串。

数据库：
```text
$2b$12$abcxxxx
```
用户输入：
```text
123456
```
bcrypt内部：
```text
    用户输入密码
        +
    数据库中的salt
        |
        ↓
    重新计算Hash
        |
        ↓
    比较Hash结果
```

## 6. JWT Token机制
### 6.1 Token生成
登录成功以后：
```text
create_access_token(
    {
        "user_id":user.id
    }
)
```
JWT Payload:
```text
{
    "user_id":1,
    "exp":过期时间戳
}
```
服务器使用：
```text
SECRET_KEY
+
HS256算法
```
生成Token

### 6.2 Token作用
JWT Token用于保存用户身份信息。它不保存完整用户数据，只保存用户ID和过期时间。
后续请求通过Token找到对应用户。

## 7. 用户身份校验流程

客户端请求头：
```text
Authorization: Bearer token
```

### 7.1 OAuth2PasswordBearer获取Token

FastAPI通过OAuth2PasswordBearer从请求Header中提取Bearer Token，
随后由decode_token完成JWT合法性校验。

```text
token = Depends(oauth2_scheme)
```
FastAPI自动从Header中获取：
```text
Bearer Token
```
提取Token

### 7.2 decode Token
调用：
```text
payload = decode_token(token)
```
验证：
- Token签名是否正确
- Token是否过期
- Token是否被篡改

### 7.3 获取当前用户
根据user_id查询数据库
```text
    user = (
        db.query(User)
        .filter(
            User.id == user_id
        ).first()
    )
```
得到User对象，返回给FastAPI依赖系统。

## 8. Depends依赖注入机制
业务接口：
```text
@router.post("/create")
def create(
    user=Depends(get_current_user)
):
    ...
```
执行流程：
```text
请求接口
    |
    ↓
发现Depends
    |
    ↓
执行get_current_user()
    |
    ↓
return User对象
    |
    ↓
注入user参数
    |
    ↓
执行业务逻辑
```
因此业务接口无需重复：
- 获取Token
- 验证Token
- 查询用户
仅需直接使用user.id


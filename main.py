import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.chat import chat_router
from app.api.upload import upload_router as upload_router
from app.exceptions.handlers import register_exception_handlers

app = FastAPI(title="AI知识库助手")

# CORS配置
app.add_middleware(
    CORSMiddleware,

    # 允许访问后端的前端地址
    allow_origins=[
        "http://localhost:5173",
    ],

    # 允许前端携带 Cookie、Token、身份凭证 发起请求
    allow_credentials=True,
    allow_methods=[
        "*"
    ],
    allow_headers=[
        "*"
    ],
)

register_exception_handlers(app)
app.include_router(upload_router)
app.include_router(chat_router)
if __name__ == '__main__':
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        # host="0.0.0.0",
        port=8000,
        reload=True,
    )

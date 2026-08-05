from fastapi import Request
from starlette.responses import JSONResponse
from app.exceptions.exceptions import (DocumentNotFound, UnsupportedDocumentType, DocumentEmptyError, LLMTimeoutError,
                                       LLMServiceError, KnowledgeBaseEmptyError, UserConflictError, UserNotFoundError,
                                       PasswordError, TokenInvalidError, InvalidCredentialsError, ConversationNotFound)


def register_exception_handlers(app):

    @app.exception_handler(DocumentNotFound)
    async def not_found_handler(request: Request, exc: DocumentNotFound):
        return JSONResponse(
            status_code=404,
            content={
                "code": 404,
                "message": exc.message
            }
        )

    @app.exception_handler(UnsupportedDocumentType)
    async def unsupported_handler(request: Request, exc: UnsupportedDocumentType):
        return JSONResponse(
            status_code=400,
            content={
                "code": 400,
                "message": exc.message
            }
        )

    @app.exception_handler(DocumentEmptyError)
    async def document_empty_handler(request: Request, exc: DocumentEmptyError):
        return JSONResponse(
            status_code=400,
            content={
                "code": 400,
                "message": exc.message
            }
        )

    @app.exception_handler(LLMTimeoutError)
    async def llm_timeout_handler(request: Request, exc: LLMTimeoutError):
        return JSONResponse(
            status_code=400,
            content={
                "code": 400,
                "message": exc.message
            }
        )

    @app.exception_handler(LLMServiceError)
    async def llm_service_error_handler(request: Request, exc: LLMServiceError):
        return JSONResponse(
            status_code=400,
            content={
                "code": 400,
                "message": exc.message
            }
        )

    @app.exception_handler(KnowledgeBaseEmptyError)
    async def knowledge_base_empty_handler(request: Request, exc: KnowledgeBaseEmptyError):
        return JSONResponse(
            status_code=404,
            content={
                "code": 404,
                "message": exc.message
            }
        )

    @app.exception_handler(UserConflictError)
    async def user_conflict_handler(request: Request, exc: UserConflictError):
        return JSONResponse(
            status_code=409,
            content={
                "code": 409,
                "message": exc.message
            }
        )

    @app.exception_handler(UserNotFoundError)
    async def user_not_found_handler(request: Request, exc: UserNotFoundError):
        return JSONResponse(
            status_code=401,
            content={
                "code": 401,
                "message": exc.message
            }
        )

    @app.exception_handler(PasswordError)
    async def password_handler(request: Request, exc: PasswordError):
        return JSONResponse(
            status_code=401,
            content={
                "code": 401,
                "message": exc.message
            }
        )
    @app.exception_handler(TokenInvalidError)
    async def token_invalid_handler(request: Request, exc: TokenInvalidError):
        return JSONResponse(
            status_code=401,
            content={
                "code": 401,
                "message": exc.message
            }
        )

    @app.exception_handler(InvalidCredentialsError)
    async def invalid_credentials_handler(request: Request, exc: InvalidCredentialsError):
        return JSONResponse(
            status_code=401,
            content={
                "code": 401,
                "message": exc.message
            }
        )

    @app.exception_handler(ConversationNotFound)
    async def conversation_not_found_handler(request: Request, exc: ConversationNotFound):
        return JSONResponse(
            status_code=404,
            content={
                "code": 404,
                "message": exc.message
            }
        )

    @app.exception_handler(Exception)
    async def exception_handler(request: Request, exc: Exception):
        return JSONResponse(
            status_code=500,
            content={
                "code": 500,
                "message": "Internal Server Error"
            }
        )


class DocumentNotFound(Exception):
    def __init__(self, message="上传文件为空"):
        self.message = message


class UnsupportedDocumentType(Exception):
    def __init__(self, message="文件类型不支持"):
        self.message = message


class DocumentEmptyError(Exception):
    def __init__(self, message="上传文件为空"):
        self.message = message


class LLMTimeoutError(Exception):
    def __init__(self, message="LLM请求超时"):
        self.message = message


class LLMServiceError(Exception):
    def __init__(self, message="LLM服务异常"):
        self.message = message


class KnowledgeBaseEmptyError(Exception):
    def __init__(self, message="知识库为空，请先上传文档"):
        self.message = message


class UserConflictError(Exception):
    def __init__(self, message="用户名已存在"):
        self.message = message


class PasswordError(Exception):
    def __init__(self, message="用户名或密码错误"):
        self.message = message


class UserNotFoundError(Exception):
    def __init__(self, message="用户名不存在"):
        self.message = message


class TokenInvalidError(Exception):
    def __init__(self, message="Token无效"):
        self.message = message


class InvalidCredentialsError(Exception):
    def __init__(self, message="密码错误"):
        self.message = message


class ConversationNotFound(Exception):
    def __init__(self, message="对话不存在"):
        self.message = message

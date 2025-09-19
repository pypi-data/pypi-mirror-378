from dataclasses import dataclass
from typing import Dict, Any, List, Optional, Generic, TypeVar

T = TypeVar('T')

@dataclass
class ApiResponse:
    success: bool
    message: str
    data: Any = None

@dataclass
class Pagination:
    page: int
    per_page: int
    total: int
    total_pages: int

@dataclass
class PaginatedResponse(Generic[T]):
    data: List[T]
    success: bool
    message: str
    pagination: Pagination

@dataclass
class ClientConfig:
    # 网关地址。如果提供了此地址，则使用网关模式，否则使用后端直连模式。
    gateway_url: Optional[str] = None
    
    # 各服务地址，仅在未提供 gateway_url 时使用
    auth_service_url: Optional[str] = None
    msg_service_url: Optional[str] = None
    user_service_url: Optional[str] = None
    file_service_url: Optional[str] = None
    survey_service_url: Optional[str] = None
    token_service_url: Optional[str] = None
    
    # 可以添加一个属性来方便判断模式
    @property
    def is_gateway_mode(self):
        return self.gateway_url is not None
@dataclass
class UserContext:
    user_id: str
    role: str  # 'SUPER_ADMIN' | 'ADMIN' | 'STAFF' | 'USER' | 'SYSTEM'
    project_id: str

@dataclass
class RequestOptions:
    method: str = 'GET'  # 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH'
    headers: Optional[Dict[str, str]] = None
    params: Optional[Dict[str, Any]] = None
    body: Optional[Any] = None
    user_context: Optional[UserContext] = None
    
# 微信小程序access_token响应
@dataclass
class WxMiniProgramTokenResponse:
    access_token: str

# 微信公众号access_token响应
@dataclass
class WxOfficialAccountTokenResponse:
    access_token: str

# 微信公众号jsapi_ticket响应
@dataclass
class WxJsapiTicketResponse:
    jsapi_ticket: str

# 微信小程序登录请求
@dataclass
class WxMiniProgramLoginRequest:
    appid: str
    code: str

# 微信小程序登录响应
@dataclass
class WxMiniProgramLoginResponse:
    openid: str
    session_key: str
    unionid: Optional[str] = None

# 微信分享签名请求
@dataclass
class WxSignatureRequest:
    appid: str
    url: str
    imgUrl: Optional[str] = None

# 微信分享签名响应
@dataclass
class WxSignatureResponse:
    appId: str
    timestamp: int
    nonceStr: str
    signature: str
    url: str
    imgUrl: str
    


@dataclass
class LoginResponse:
    access_token: str
    token_type: str
    expires_at: str
    project_id: int

@dataclass
class LoginApiResponse:
    success: bool
    message: str
    access_token: str  # 顶层的access_token字段
    data: LoginResponse  # data字段中的登录信息
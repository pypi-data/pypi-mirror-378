from dataclasses import dataclass
from typing import Optional

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
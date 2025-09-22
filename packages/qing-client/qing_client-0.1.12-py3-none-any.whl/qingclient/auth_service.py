from typing import Any
from .base_client import BaseClient
from .types import RequestOptions, LoginResponse, LoginApiResponse

class AuthService(BaseClient):
    def __init__(self, config):
        super().__init__(config, 'auth')
    
    def login(self, identifier: str, password: str, project_id: int = 0, options: RequestOptions = None) -> LoginResponse:
        # 构建与CURL完全一致的表单数据（包括空字段）
        body = {
            'grant_type': '',  # 空字符串，而不是'password'
            'username': identifier,
            'password': password,
            'scope': '',
            'client_id': '',
            'client_secret': ''
        }
        
        headers = {}
        if options and options.headers:
            headers = options.headers.copy()
        headers['Content-Type'] = 'application/x-www-form-urlencoded'
        
        login_path = '/login'
        
        # 移除project_id查询参数，因为CURL中没有
        # 如果需要project_id，可能需要通过其他方式传递（如token或body）
        api_response = self._raw_request(login_path, RequestOptions(
            method='POST',
            headers=headers,
            body=body  # 不发送查询参数
        ))
        
        # 从API响应中提取实际的登录数据
        login_data = api_response.get('data', {})
        
        # 网关模式下，登录成功后需要保存token
        if hasattr(self.config, 'is_gateway_mode') and self.config.is_gateway_mode:
            # 优先使用顶层的access_token，如果没有则使用data中的
            token_to_save = api_response.get('access_token') or login_data.get('access_token')
            if token_to_save:
                self.set_token(token_to_save)
        
        # 返回登录数据
        return LoginResponse(
            access_token=login_data.get('access_token'),
            token_type=login_data.get('token_type'),
            expires_at=login_data.get('expires_at'),
            project_id=login_data.get('project_id')
        )
    def logout(self, token: str = None, options: RequestOptions = None):
        # 网关模式下，使用保存的token或传入的token
        headers = {}
        if options and options.headers:
            headers = options.headers.copy()
        
        # 明确指定使用哪个token
        logout_token = token if token else self.token
        if logout_token:
            headers['Authorization'] = f'Bearer {logout_token}'
        
        return self.request('/logout', RequestOptions(
            method='POST',
            headers=headers
        ))
        
    def _raw_request(self, path: str, options: RequestOptions = None) -> Any:
        """发送请求并返回完整的API响应（不提取data字段）"""
        # 复制BaseClient.request的逻辑，但不提取data字段
        if options is None:
            options = RequestOptions(method='GET')
        
        try:
            base_url = self._get_base_url()
            full_path = self._get_full_path(path)
            url = f"{base_url}{full_path}"
            
            headers = options.headers.copy() if options.headers else {}
            params = options.params.copy() if options.params else {}
            
            context = options.user_context or self.user_context
            if context and not self._is_gateway_mode():
                headers.update(self._init_user_context_headers(context))
            
            if self._is_gateway_mode() and self.token:
                headers['Authorization'] = f"Bearer {self.token}"
            
            response = self.session.request(
                method=options.method,
                url=url,
                headers=headers,
                params=params,
                json=options.body,
                timeout=30
            )
            
            response.raise_for_status()
            response_data = response.json()
            
            if not response_data.get('success', False):
                raise Exception(response_data.get('message', '业务请求失败'))
            
            # 返回完整的响应，不提取data字段
            return response_data
            
        except Exception as error:
            self._handle_api_error(error, path)
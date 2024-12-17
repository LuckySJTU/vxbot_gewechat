import httpx
import yaml
from pathlib import Path
import logging
import random
from typing import Dict, Tuple, Optional


class KeyManager:
    """API密钥管理器"""

    def __init__(self, config_path: str = 'utils/aiService/config.yml'):
        self.config_path = config_path
        self.logger = logging.getLogger('WeChatBot')
        self._ensure_config_exists()

    def _ensure_config_exists(self):
        """确保配置文件存在，不存在则创建默认配置"""
        if not Path(self.config_path).exists():
            default_config = {
                'ai_service': {
                    'proxy_host': 'http://45.88.42.184:8001',
                    'default_provider': 'claude',
                    'providers': {
                        'claude': {
                            'models': {
                                'Claude-3-Sonnet': {
                                    'model_id': 'claude-3-sonnet-20240229',
                                    'input_cost': 3.0,
                                    'output_cost': 15.0
                                }
                            },
                            'api_keys': {
                                'active': [],
                                'exhausted': []
                            },
                            'api_version': '2023-06-01',
                            'default_model': 'Claude-3-Sonnet'
                        },
                        'openai': {
                            'models': {
                                'GPT-4-Turbo': {
                                    'model_id': 'gpt-4-turbo-preview',
                                    'input_cost': 3.0,
                                    'output_cost': 12.0
                                }
                            },
                            'api_keys': {
                                'active': [],
                                'exhausted': []
                            },
                            'default_model': 'GPT-4-Turbo'
                        }
                    }
                }
            }
            with open(self.config_path, 'w', encoding='utf-8') as f:
                yaml.dump(default_config, f, allow_unicode=True)

    def load_config(self) -> Dict:
        """加载配置"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            self.logger.error(f"加载配置文件失败: {e}")
            return {}

    def get_random_key(self, provider: str) -> Optional[str]:
        """获取指定提供商的随机可用API密钥"""
        config = self.load_config()
        provider_config = config['ai_service']['providers'].get(provider)
        if not provider_config:
            return None
        active_keys = provider_config['api_keys']['active']
        if not active_keys:
            return None
        return random.choice(active_keys)

    def mark_key_as_exhausted(self, provider: str, key: str):
        """将指定提供商的密钥标记为已用尽"""
        config = self.load_config()
        provider_config = config['ai_service']['providers'].get(provider)
        if not provider_config:
            return

        active_keys = provider_config['api_keys']['active']
        exhausted_keys = provider_config['api_keys']['exhausted']

        if key in active_keys:
            active_keys.remove(key)
            exhausted_keys.append(key)

            provider_config['api_keys']['active'] = active_keys
            provider_config['api_keys']['exhausted'] = exhausted_keys

            with open(self.config_path, 'w', encoding='utf-8') as f:
                yaml.dump(config, f, allow_unicode=True)
            self.logger.info(f"{provider} API密钥 {key[:8]}*** 已标记为已用尽")


class AIService:
    """AI服务类"""

    def __init__(self):
        self.key_manager = KeyManager()
        self.logger = logging.getLogger('WeChatBot')
        self.config = self.key_manager.load_config()['ai_service']
        self.proxy_host = self.config['proxy_host']

    def _get_provider_config(self, provider: str, model: Optional[str] = None) -> Tuple[Dict, str]:
        """获取提供商配置和模型ID"""
        if not provider:
            provider = self.config['default_provider']

        provider_config = self.config['providers'].get(provider)
        if not provider_config:
            raise ValueError(f"不支持的AI提供商: {provider}")

        if not model:
            model = provider_config['default_model']

        model_config = provider_config['models'].get(model)
        if not model_config:
            raise ValueError(f"提供商 {provider} 不支持模型 {model}")

        return provider_config, model_config['model_id']

    async def get_ai_response(self, text: str, provider: str = "", model: str = "") -> str:
        """获取AI回复"""
        provider_config, model_id = self._get_provider_config(provider, model)

        while True:
            key = self.key_manager.get_random_key(provider)
            if not key:
                raise Exception(f"{provider} 的所有API密钥已用尽")

            try:
                if provider == 'claude':
                    response = await self._call_claude_api(text, key, provider_config, model_id)
                elif provider == 'openai':
                    response = await self._call_openai_api(text, key, model_id)
                else:
                    raise ValueError(f"未实现的AI提供商: {provider}")
                return response

            except httpx.HTTPStatusError as e:
                if e.response.status_code == 429:  # 配额用尽
                    self.key_manager.mark_key_as_exhausted(provider, key)
                    continue
                raise

    async def _call_claude_api(self, text: str, api_key: str, provider_config: Dict, model_id: str) -> str:
        """调用Claude API"""
        async with httpx.AsyncClient() as client:
            # 可能需要更换url
            response = await client.post(
                f"{self.proxy_host}/claude/messages",
                headers={
                    "accept": "application/json",
                    "content-type": "application/json",
                    "anthropic-version": provider_config['api_version'],
                    "x-api-key": api_key
                },
                json={
                    "model": model_id,
                    "messages": [{"role": "user", "content": text}],
                    "max_tokens": 1024
                },
                timeout=30.0
            )
            response.raise_for_status()
            data = response.json()
            return data["content"][0]["text"].strip()

    async def _call_openai_api(self, text: str, api_key: str, model_id: str) -> str:
        """调用OpenAI API"""
        async with httpx.AsyncClient() as client:
            # 可能需要更换url
            response = await client.post(
                f"{self.proxy_host}/openai/chat/completions",
                headers={
                    "accept": "application/json",
                    "content-type": "application/json",
                    "Authorization": f"Bearer {api_key}"
                },
                json={
                    "model": model_id,
                    "messages": [{"role": "user", "content": text}],
                    "temperature": 0.7
                },
                timeout=30.0
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"].strip()
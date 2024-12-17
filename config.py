import yaml


class Config:
    """配置管理类，负责加载和管理程序配置"""

    def __init__(self, config_file='config.yml'):
        self.config_file = config_file
        self.config = self.load_config()

    def load_config(self):
        """
        加载配置文件，如果文件不存在则创建默认配置
        返回：dict 配置数据
        """
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            # 默认配置
            default_config = {
                'monitoring': {
                    'check_interval': 30,  # 状态检查间隔（秒）
                },
                'alerts': {
                    'email': {
                        'enabled': False,
                        'smtp_server': 'smtp.gmail.com',
                        'smtp_port': 587,
                        'sender_email': '',
                        'sender_password': '',
                        'recipient_email': ''
                    },
                    'telegram': {
                        'enabled': False,
                        'bot_token': '',
                        'chat_id': ''
                    }
                },
                'wechat': {
                    'base_url': 'http://localhost:2531/v2/api',
                    'callback_url': 'http://localhost:8069/callback',
                    'app_id': '',
                    'token': ''
                }
            }
            # 保存默认配置到文件
            with open(self.config_file, 'w', encoding='utf-8') as f:
                yaml.dump(default_config, f, allow_unicode=True)
            return default_config
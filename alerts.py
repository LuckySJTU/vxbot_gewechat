# alerts.py
import smtplib
from email.mime.text import MIMEText
import requests
from abc import ABC, abstractmethod
import logging


class AlertBase(ABC):
    """告警基类，定义告警模块的基本接口"""

    @abstractmethod
    def send_alert(self, message):
        """
        发送告警的抽象方法
        参数：
            message: str 告警消息内容
        返回：
            bool 是否发送成功
        """
        pass


class EmailAlert(AlertBase):
    """邮件告警模块"""

    def __init__(self, config):
        """
        初始化邮件告警模块
        参数：
            config: dict 邮件配置信息
        """
        self.config = config['email']

    def send_alert(self, message):
        """
        发送邮件告警
        参数：
            message: str 告警消息内容
        返回：
            bool 是否发送成功
        """
        if not self.config['enabled']:
            return False

        try:
            msg = MIMEText(message)
            msg['Subject'] = 'WeChat Bot Alert'
            msg['From'] = self.config['sender_email']
            msg['To'] = self.config['recipient_email']

            # 使用SSL连接
            server = smtplib.SMTP_SSL(self.config['smtp_server'], self.config['smtp_port'])
            server.login(self.config['sender_email'], self.config['sender_password'])
            server.send_message(msg)
            server.quit()
            logging.getLogger('WeChatBot').info("邮件告警发送成功")
            return True
        except Exception as e:
            logging.getLogger('WeChatBot').error(f"邮件告警发送失败: {e}")
            return False


class TelegramAlert(AlertBase):
    """Telegram告警模块"""

    def __init__(self, config):
        """
        初始化Telegram告警模块
        参数：
            config: dict Telegram配置信息
        """
        self.config = config['telegram']

    def send_alert(self, message):
        """
        发送Telegram告警
        参数：
            message: str 告警消息内容
        返回：
            bool 是否发送成功
        """
        if not self.config['enabled']:
            return False

        try:
            url = f"https://api.telegram.org/bot{self.config['bot_token']}/sendMessage"
            data = {
                "chat_id": self.config['chat_id'],
                "text": message
            }
            response = requests.post(url, json=data)
            success = response.status_code == 200
            if success:
                logging.getLogger('WeChatBot').info("Telegram告警发送成功")
            else:
                logging.getLogger('WeChatBot').error(f"Telegram告警发送失败: {response.text}")
            return success
        except Exception as e:
            logging.getLogger('WeChatBot').error(f"Telegram告警发送失败: {e}")
            return False


class AlertManager:
    """告警管理器，统一管理所有告警模块"""

    def __init__(self, config):
        """
        初始化告警管理器
        参数：
            config: dict 告警配置信息
        """
        self.alerts = []
        alert_config = config['alerts']
        logger = logging.getLogger('WeChatBot')

        # 初始化启用的告警模块
        if alert_config['email']['enabled']:
            self.alerts.append(EmailAlert(alert_config))
            logger.info("邮件告警模块已启用")
        if alert_config['telegram']['enabled']:
            self.alerts.append(TelegramAlert(alert_config))
            logger.info("Telegram告警模块已启用")

    def send_alerts(self, message):
        """
        发送告警到所有启用的告警模块
        参数：
            message: str 告警消息内容
        """
        for alert in self.alerts:
            alert.send_alert(message)
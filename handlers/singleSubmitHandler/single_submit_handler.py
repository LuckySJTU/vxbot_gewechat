from ..handlers import MessageHandler, MessageContext
import logging

class SingleSubmitHandler(MessageHandler):
    """只允许单次提交处理器"""
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger('WeChatBot')

    async def can_handle(self, context: MessageContext) -> bool:
        """仅处理文本消息"""
        return context.msg_type == 1

    async def handle(self, context: MessageContext) -> bool:
        """处理消息"""
        self.logger.debug(f"SingleSubmitHandler处理用户 {context.from_user} 的消息")
        return True
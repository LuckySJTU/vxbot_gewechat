from ...handlers import MessageHandler, MessageContext
import logging


class EchoHandler(MessageHandler):
    """消息复述处理器"""

    def __init__(self):
        super().__init__()
        from sender import MessageSender
        self.message_sender = MessageSender()
        self.logger = logging.getLogger('WeChatBot')

    async def can_handle(self, context: MessageContext) -> bool:
        return context.msg_type == 1

    async def handle(self, context: MessageContext) -> bool:
        try:
            echo_message = f"{context.content}"
            success = await self.message_sender.send_text(
                context.app_id,
                context.from_user,
                echo_message
            )

            if success:
                self.logger.info(f"已复述消息给用户 {context.from_user}")
                return True
            else:
                self.logger.error("发送消息失败")
                return False

        except Exception as e:
            self.logger.error(f"复述消息时出错: {e}")
            return False
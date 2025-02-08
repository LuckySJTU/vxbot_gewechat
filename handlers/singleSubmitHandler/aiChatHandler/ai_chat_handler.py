# handlers/singleSubmitHandler/aiChatHandler/ai_chat_handler.py
from ...handlers import MessageHandler, MessageContext
from utils.aiService.ai_service import AIService
from sender import MessageSender
import logging


class AIChatHandler(MessageHandler):
    """AI对话处理器"""

    def __init__(self):
        super().__init__()
        self.ai_service = AIService()
        self.message_sender = MessageSender()
        self.logger = logging.getLogger('WeChatBot')

    async def can_handle(self, context: MessageContext) -> bool:
        """判断是否为文本消息"""
        self.logger.info(context.raw_message)
        return False
        # return context.msg_type == 1

    async def handle(self, context: MessageContext) -> bool:
        """处理消息"""
        try:
            # 发送处理中的提示

            # 调用AI服务获取回复
            response = await self.ai_service.get_ai_response(context.content,provider="deepseek",model="deepseek-chat")

            # 发送AI回复
            success = await self.message_sender.send_text(
                context.app_id,
                context.from_user,
                response
            )

            if success:
                self.logger.info(f"已发送AI回复给用户 {context.from_user}")
                return True
            else:
                self.logger.error("发送AI回复失败")
                return False

        except Exception as e:
            self.logger.error(f"AI对话处理出错: {e}")
            # 发送错误提示
            await self.message_sender.send_text(
                context.app_id,
                context.from_user,
                f"抱歉，处理您的消息时出现错误: {str(e)}"
            )
            return False
# handlers/singleSubmitHandler/aiChatHandler/ai_chat_handler.py
from ...handlers import MessageHandler, MessageContext
from utils.aiService.ai_service import AIService
from sender import MessageSender
import logging
from database import Session, ChatMessage
import requests

chat_contexts = {}

# DeepSeek API 配置
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"  
DEEPSEEK_API_KEY = ''
ZHIPU_API_URL = 'https://open.bigmodel.cn/api/paas/v4/chat/completions'
ZHIPU_API_KEY = ''

def save_message(sender_id, sender_name, message, reply):
    """保存聊天记录到数据库"""
    try:
        session = Session()
        chat_message = ChatMessage(
            sender_id=sender_id,
            sender_name=sender_name,
            message=message,
            reply=reply
        )
        session.add(chat_message)
        session.commit()
        session.close()
    except Exception as e:
        logger.error(f"保存消息失败: {str(e)}")


class AIChatHandler(MessageHandler):
    """AI对话处理器"""

    def __init__(self):
        super().__init__()
        self.ai_service = AIService()
        self.message_sender = MessageSender()
        self.logger = logging.getLogger('WeChatBot')

    async def can_handle(self, context: MessageContext) -> bool:
        """判断是否为文本消息"""
        # self.logger.info(context.raw_message)
        # self.logger.info(context.is_group)
        # self.logger.info(context.is_at)
        # self.logger.info(context.is_for_bot)
        # self.logger.info(context.msg)
        return context.msg_type == 1 and context.is_for_bot

    async def handle(self, context: MessageContext) -> bool:
        """处理消息"""
        # 获取用户上下文
        user_wxid = context.from_user
        if user_wxid not in chat_contexts:
            chat_contexts[user_wxid] = []
        # 添加新消息到上下文
        chat_contexts[user_wxid].append({"role": "user", "content": context.msg})
        # 保持上下文长度不超过5条消息
        if len(chat_contexts[user_wxid]) > 5:
            chat_contexts[user_wxid] = chat_contexts[user_wxid][-5:]
        
        try:
            headers = {
                "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
                "Content-Type": "application/json"
            }
            data = {
                "model": "deepseek-chat",
                "messages": [
                    {"role": "system", "content": "你是一个人工智能聊天助手，请尽量简洁明了准确地回答问题。"},
                    *chat_contexts[user_wxid]
                ]
            }
            response = requests.post(DEEPSEEK_API_URL, headers=headers, json=data, timeout=30)
            response.raise_for_status()
            reply = response.json()['choices'][0]['message']['content']
            # 添加回复到上下文
            chat_contexts[user_wxid].append({"role": "assistant", "content": reply})
            
        except Exception as e:
            self.logger.error(f"Deepseek回复出错，尝试使用智谱清言回复。{e}")
        
            try:
                headers = {
                    "Authorization": f"Bearer {ZHIPU_API_KEY}",
                    "Content-Type": "application/json"
                }
                data = {
                    "model": "glm-4-flashx",
                    "messages": [
                        {"role": "system", "content": "你是一个人工智能聊天助手，请尽量简洁明了准确地回答问题。"},
                        *chat_contexts[user_wxid]
                    ]
                }
                response = requests.post(ZHIPU_API_URL, headers=headers, json=data, timeout=30)
                response.raise_for_status()
                reply = response.json()['choices'][0]['message']['content']
                # 添加回复到上下文
                chat_contexts[user_wxid].append({"role": "assistant", "content": reply})
                reply = '【Deepseek无响应，使用智谱清言回复。】' + reply
            
            except Exception as e:
                self.logger.error(f"智谱清言回复失败，返回无法处理。{e}")
                reply = '获取AI回复时出错，请稍后再试。'

        # 尝试发送
        try:
            # 发送回复
            success = await self.message_sender.send_text(
                context.app_id,
                context.from_user,
                reply,
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
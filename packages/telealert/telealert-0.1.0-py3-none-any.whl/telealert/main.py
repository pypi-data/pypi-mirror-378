import logging

from aiogram import Bot


class TeleAlertBot:
    """
    A simple message sender to one or more chats/groups.
    Doesn't listen to incoming messages.
    """

    def __init__(self, token: str, chat_id: int):
        """
        :param token: Your bot's API token
        :param chat_id: Group chat ID
        """
        self.bot = Bot(token=token)
        self.chat_id = chat_id



    async def send_message(self, text: str):
        """
        Sends a message to chat_id.
        """
        try:
            await self.bot.send_message(chat_id=self.chat_id, text=text)
            logging.info(f"Сообщение отправлено в chat_id={self.chat_id}")
        except Exception as e:
            logging.error(f"Failed to send message: {e}")

    async def close(self):
        """
        Closes the bot's HTTP session.
        """
        await self.bot.session.close()
        logging.info("Telegram bot's HTTP session closed")
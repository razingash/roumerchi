import telebot
from avalance.settings.base import TOKEN, CHAT_ID

def log_errors(f):
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            print(f'BOT ERROR: {e}')
            raise e

    return wrapper


bot = telebot.TeleBot(TOKEN)
chat_id = CHAT_ID

@log_errors
def send_message(error_message):
    bot.send_message(chat_id, error_message)


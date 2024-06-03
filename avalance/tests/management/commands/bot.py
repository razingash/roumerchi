import telebot


from avalance.settings import TOKEN


def log_errors(f):
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            print(f'BOT ERROR: {e}')
            raise e

    return wrapper


@log_errors
def send_exception(update, context):
    chat_id = update.message.chat_id
    text = update.message.text

    reply = "asfdsafd"
    context.bot.send_message(chat_id=chat_id, text=reply)

bot = telebot.TeleBot(TOKEN)
chat_id = 537066178
def send_message(error_message):
    bot.send_message(chat_id, error_message)


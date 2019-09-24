import telegram
import key
from ndb_user import NDB_User
import time

'''
python-telegram-bot documentation
https://python-telegram-bot.readthedocs.io/en/stable/
'''

TELEGRAM_BOT = telegram.Bot(token=key.TELEGRAM_API_TOKEN)

def set_webhook():
    s = TELEGRAM_BOT.setWebhook(key.WEBHOOK_TELEGRAM_BASE, allowed_updates=['message'])
    if s:
        print("webhook setup ok: {}".format(key.WEBHOOK_TELEGRAM_BASE))
    else:
        return "webhook setup failed"

def delete_webhook():
    TELEGRAM_BOT.deleteWebhook()

def get_webhook_info():
    print(TELEGRAM_BOT.get_webhook_info())

def get_reply_markup(user, kb, remove_keyboard):
    reply_markup = None
    if kb or remove_keyboard:
        if remove_keyboard:
            user.set_empy_keyboard()            
            reply_markup = telegram.ReplyKeyboardRemove()
        else:
            user.set_keyboard(kb)
            reply_markup = telegram.ReplyKeyboardMarkup(kb, resize_keyboard=True)
    return reply_markup

def send_message(user, text, kb=None, remove_keyboard=False, markdown=True, sleep=False, **kwargs):
    #sendMessage(chat_id, text, parse_mode=None, disable_web_page_preview=None, disable_notification=False,
    # reply_to_message_id=None, reply_markup=None, timeout=None, **kwargs)
    chat_id = user.serial_number if isinstance(user, NDB_User) else user
    reply_markup = get_reply_markup(user, kb, remove_keyboard)
    parse_mode = telegram.ParseMode.MARKDOWN if markdown else None
    TELEGRAM_BOT.sendMessage(
        chat_id = chat_id,
        text = text,            
        reply_markup = reply_markup,
        parse_mode = parse_mode,
        **kwargs
    )
    if sleep:
        time.sleep(0.1)

def send_typing_action(user, sleep_secs=None):    
    chat_id = user.serial_number if isinstance(user, NDB_User) else user
    TELEGRAM_BOT.sendChatAction(
        chat_id = chat_id,
        action = telegram.ChatAction.TYPING
    )
    if sleep_secs:
        time.sleep(sleep_secs)

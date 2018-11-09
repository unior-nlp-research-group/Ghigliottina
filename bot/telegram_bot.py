# -*- coding: utf-8 -*-

import telegram
import key
import ui
import solver
from exception_handler import exception_reporter
import logging
from ndb_user import NDB_User

TELEGRAM_BOT = telegram.Bot(token=key.TELEGRAM_API_TOKEN)

def set_webhook():
    s = TELEGRAM_BOT.setWebhook(key.WEBHOOK_TELEGRAM_BASE)
    if s:
        return "webhook setup ok"
    else:
        return "webhook setup failed"

def delete_webhook():
    TELEGRAM_BOT.deleteWebhook()

def get_webhook_info():
    print(TELEGRAM_BOT.get_webhook_info())

'''
python-telegram-bot documentation
https://python-telegram-bot.readthedocs.io/en/stable/
'''

@exception_reporter
def deal_with_request(request_json):
    # retrieve the message in JSON and then transform it to Telegram object
    update_obj = telegram.Update.de_json(request_json, TELEGRAM_BOT)
    message_obj = update_obj.message    
    user_obj = message_obj.from_user
    name = user_obj.first_name
    if user_obj.last_name:
        name += ' ' + user_obj.last_name
    user = NDB_User('telegram', user_obj.id, name, user_obj.username)
    
    if message_obj.text:
        deal_with_text_request(user, message_obj.text)
    elif message_obj.photo:
        deal_with_photo_request(user, message_obj.photo)
    elif message_obj.document:
        deal_with_document_request(user, message_obj.document)
    else:
        logging.debug('TELEGRAM: no text of photo in request')
        return


DEFAULT_KEYBOARD = [[ui.BUTTON_INFO]]
DEFAULT_REPLY_MARKUP = telegram.ReplyKeyboardMarkup(DEFAULT_KEYBOARD, resize_keyboard=True)

def send_message(user, text, markdown=True):
    if markdown:
        TELEGRAM_BOT.sendMessage(
            chat_id = user.serial_number, 
            text = text,
            parse_mode = telegram.ParseMode.MARKDOWN,
            reply_markup = DEFAULT_REPLY_MARKUP
        )
    else:
        TELEGRAM_BOT.sendMessage(
            chat_id = user.serial_number,          
            text = text,
            reply_markup = DEFAULT_REPLY_MARKUP
        )
    
def deal_with_text_request(user, text):
    if text in ['/start', '/help', ui.BUTTON_INFO]:
        reply_text = ui.intro(from_twitter=False)
        send_message(user, reply_text)    
        return
    if text == '/exception':
        1/0
        return
    if text.startswith('/debug') and ' ' in text:
        on_off = text.lower().split()[1]
        if on_off in ['on','off']:
            user.debug = on_off == 'on'
            user.put()
            msg = "Debug attivato" if user.debug else "Debug disattivato"
            send_message(user, msg)    
            return        
    reply_text, _ = solver.get_solution(user, text)    
    send_message(user, reply_text)    
    logging.debug('TELEGRAM Reply to message from @{} with text {} -> {}'.format(user.serial_number, text, reply_text))            

def get_url_from_file_id(file_id):    
    import requests
    logging.debug("TELEGRAM: Requested file_id: {}".format(file_id))
    r = requests.post(key.DIALECT_API_URL + 'getFile', data={'file_id': file_id})
    r_json = r.json()
    if 'result' not in r_json or 'file_path' not in r_json['result']:
        logging.warning('No result found when requesting file_id: {}'.format(file_id))
        return None
    file_url = r_json['result']['file_path']
    return file_url

def deal_with_photo_request(user, photo_list):
    import vision
    photo_size = photo_list[-1] # last one is the biggest
    file_url_suffix = get_url_from_file_id(photo_size.file_id)
    file_url = key.DIALECT_API_URL_FILE + file_url_suffix
    logging.debug('TELEGRAM File_url: {}'.format(file_url))
    image_content = vision.get_image_content_by_uri(file_url)        
    clues_list = vision.detect_clues(image_content=image_content)
    reply_text, _ = solver.get_solution_from_image(user, clues_list)
    send_message(user, reply_text)    
    logging.debug('TELEGRAM Reply to message from id={} with photo_url {} -> {}'.format(user.serial_number, file_url, reply_text))            

def deal_with_document_request(user, document_obj):
    text = "Mandami l'immagine come *photo* e non come documento."
    send_message(user, text)    

TELEGRAM_BOT_MASTER = None

def report_master(message):
    global TELEGRAM_BOT_MASTER
    if TELEGRAM_BOT_MASTER is None:
        TELEGRAM_BOT_MASTER = NDB_User('telegram', key.TELEGRAM_BOT_MASTER_ID, update=False)
    send_message(TELEGRAM_BOT_MASTER, message, markdown=False)    

# -*- coding: utf-8 -*-

import telegram
import key
import ui
import solver
from exception_handler import exception_reporter
import logging
import ndb_person

TELEGRAM_BOT = telegram.Bot(token=key.TELEGRAM_API_TOKEN)

def set_webhook():
    s = TELEGRAM_BOT.setWebhook(key.WEBKOOK_TELEGRAM_BASE)
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
    user = message_obj.from_user
    chat_id = user.id
    first_name = user.first_name
    last_name = user.last_name
    username = user.username
    ndb_person.register_person('telegram', chat_id, first_name, last_name, username)
    
    if message_obj.text:
        deal_with_text_request(chat_id, message_obj.text)
    elif message_obj.photo:
        deal_with_photo_request(chat_id, message_obj.photo)
    elif message_obj.document:
        deal_with_document_request(chat_id, message_obj.document)
    else:
        logging.debug('TELEGRAM: no text of photo in request')
        return


DEFAULT_KEYBOARD = [[ui.BUTTON_INFO]]
DEFAULT_REPLY_MARKUP = telegram.ReplyKeyboardMarkup(DEFAULT_KEYBOARD, resize_keyboard=True)

def send_message(chat_id, text, markdown=True):
    if markdown:
        TELEGRAM_BOT.sendMessage(
            chat_id=chat_id, 
            text=text,
            parse_mode=telegram.ParseMode.MARKDOWN,
            reply_markup=DEFAULT_REPLY_MARKUP
        )
    else:
        TELEGRAM_BOT.sendMessage(
            chat_id=chat_id,          
            text=text,
            reply_markup=DEFAULT_REPLY_MARKUP
        )
    
def deal_with_text_request(chat_id, text):
    if text in ['/start', '/help', ui.BUTTON_INFO]:
        reply_text = ui.intro(from_twitter=False)
    elif text == '/exception':
        1/0
    else:
        reply_text, _ = solver.get_solution_from_text(text,from_twitter=False)    
    send_message(chat_id, reply_text)    
    logging.debug('TELEGRAM Reply to message from @{} with text {} -> {}'.format(chat_id, text, reply_text))            

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

def deal_with_photo_request(chat_id, photo_list):
    import vision
    photo_size = photo_list[-1] # last one is the biggest
    file_url_suffix = get_url_from_file_id(photo_size.file_id)
    file_url = key.DIALECT_API_URL_FILE + file_url_suffix
    logging.debug('TELEGRAM File_url: {}'.format(file_url))
    image_content = vision.get_image_content_by_uri(file_url)        
    clues_list = vision.detect_clues(image_content=image_content)
    reply_text, _ = solver.get_solution_from_image_clues(clues_list, from_twitter=False)
    send_message(chat_id, reply_text)    
    logging.debug('TELEGRAM Reply to message from @{} with photo_url {} -> {}'.format(chat_id, file_url, reply_text))            

def deal_with_document_request(chat_id, document_obj):
    text = "Mandami l'immagine come *photo* e non come documento."
    send_message(key.TELEGRAM_BOT_MASTER_ID, text)    

def report_master(error_message):
    send_message(key.TELEGRAM_BOT_MASTER_ID, error_message, markdown=False)    

import key
import response_formatter
import solver
from exception_handler import exception_reporter
import logging
import ndb_user
from ndb_user import NDB_User
from telegram_bot import TELEGRAM_BOT, send_message, send_typing_action
import telegram_bot_ux as ux
import utility
import telegram
import generator

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

# ================================
# REPORT MASTER
# ================================
def report_master(message):
    send_message(key.TELEGRAM_BOT_MASTER_ID, message, markdown=False)    


# ================================
# RESTART
# ================================
def restart_user(user):
    redirect_to_state(user, state_INITIAL, message_obj=None)


# ================================
# REDIRECT TO STATE
# ================================
def redirect_to_state(user, new_function, message_obj=None, set_previous_state=True):
    new_state = new_function.__name__
    if user.state != new_state:
        logging.debug("In redirect_to_state. current_state:{0}, new_state: {1}".format(str(user.state), str(new_state)))        
        user.set_state(new_state)
    repeat_state(user, message_obj)

# ================================
# REPEAT STATE
# ================================
def repeat_state(user, message_obj=None):
    state = user.state
    if state is None:
        restart_user(user)
        return
    method = possibles.get(state)
    if not method:
        msg = "⚠️ User {} sent to unknown method state: {}".format(user.chat_id, state)
        report_master(msg)
        send_message(user, ux.MSG_REFRESH_INTERFACE, sleep=1)
        restart_user(user)
    else:
        method(user, message_obj)

# ================================
# Initial State
# ================================
def state_INITIAL(user, message_obj):
    if message_obj is None:
        kb = [
            [ux.BUTTON_SOLVER, ux.BUTTON_GENERATOR],
            [ux.BUTTON_INFO]
        ]
        if user.is_admin():
            kb[1].insert(1, ux.BUTTON_ADMIN)
        send_message(user, ux.MSG_INTRO, kb)
    else:
        text_input = message_obj.text
        kb = user.get_keyboard()
        if text_input:
            if text_input in utility.flatten(kb):
                if text_input == ux.BUTTON_INFO:
                    send_message(user, ux.MSG_INFO)
                elif text_input == ux.BUTTON_SOLVER:
                    redirect_to_state(user, state_SOLVER)
                elif text_input == ux.BUTTON_GENERATOR:
                    redirect_to_state(user, state_GENERATOR)
                elif text_input == ux.BUTTON_ADMIN:
                    msg = "*User Stats*:\n"
                    for a in ['telegram','twitter']:
                        msg += "- {}: {}\n".format(a, ndb_user.get_user_count(a))
                    send_message(user, msg)
                else:
                    assert(False)
            elif ux.text_is_button(text_input):
                send_message(user, ux.MSG_WRONG_BUTTON_INPUT, kb)
            else:
                send_message(user, ux.MSG_WRONG_INPUT_USE_BUTTONS, kb)
        else:
            send_message(user, ux.MSG_WRONG_INPUT_USE_BUTTONS, kb)

# ================================
# SOLVER State
# ================================
def state_SOLVER(user, message_obj):
    if message_obj is None:
        kb = [
            [ux.BUTTON_BACK],
        ]
        send_message(user, ux.MSG_SOLVER_INTRO, kb)
    else: 
        kb = user.get_keyboard()
        if message_obj.text:
            text_input = message_obj.text
            if text_input in utility.flatten(kb):
                if text_input == ux.BUTTON_BACK:
                    restart_user(user)
                else:
                    assert(False)
            elif ux.text_is_button(text_input):
                send_message(user, ux.MSG_WRONG_BUTTON_INPUT, kb)
            else:
                reply_text, _ = solver.get_solution_from_text(user, text_input)    
                send_message(user, reply_text)                    
        elif message_obj.photo:
            import vision
            photo_size = message_obj.photo[-1] # last one is the biggest
            file_url_suffix = get_url_from_file_id(photo_size.file_id)
            file_url = key.DIALECT_API_URL_FILE + file_url_suffix
            logging.debug('TELEGRAM File_url: {}'.format(file_url))
            image_content = vision.get_image_content_by_uri(file_url)        
            clues_list = vision.detect_clues(image_content=image_content)
            reply_text, _ = solver.get_solution_from_image(user, clues_list)
            send_message(user, reply_text)    
            logging.debug('TELEGRAM Reply to message from id={} with photo_url {} -> {}'.format(user.serial_number, file_url, reply_text))            
        elif message_obj.document:
            send_message(user, ux.MSG_SEND_PHOTO_NOT_DOCUMENT)    
        else:
            send_message(user, ux.MSG_WRONG_INPUT_USE_BUTTONS_TEXT_PHOTO, kb)

# ================================
# GENERATOR State
# ================================
def state_GENERATOR(user, message_obj):
    if message_obj is None:
        kb = [
            [ux.BUTTON_SOLUTION],
            [ux.BUTTON_BACK],
        ]
        clues, solution, explanations = generator.get_ghigliottina()        
        user.set_var(
            'GHIGLIOTTINA', 
            {
                'CLUES': clues,
                'SOLUTION': solution,
                'EXPLANATIONS': explanations,
                'TIME': utility.get_now_seconds()
            }            
        )
        msg = ux.MSG_GENERATOR_INTRO.format(', '.join(clues))
        send_message(user, msg, kb)            
    else: 
        kb = user.get_keyboard()
        if message_obj.text:            
            text_input = message_obj.text
            solution = user.get_var('GHIGLIOTTINA')['SOLUTION']
            explanations = '\n'.join('- {}'.format(e) for e in user.get_var('GHIGLIOTTINA')['EXPLANATIONS'])
            if text_input in utility.flatten(kb):
                if text_input == ux.BUTTON_BACK:
                    restart_user(user)
                elif text_input == ux.BUTTON_SOLUTION:    
                    ellapsed_sec = utility.get_now_seconds() - user.get_var('GHIGLIOTTINA')['TIME']
                    if ellapsed_sec<60:
                        send_message(user, ux.MSG_TOO_EARLY)
                    else:
                        send_message(user, ux.MSG_SOLUTION.format(solution))
                        send_typing_action(user, sleep_secs=0.5)
                        send_message(user, ux.MSG_EXPLANATIONS.format(explanations))
                        send_typing_action(user, sleep_secs=1)
                        redirect_to_state(user, state_CONTINUE)
                else:
                    assert(False)
            elif ux.text_is_button(text_input):
                send_message(user, ux.MSG_WRONG_BUTTON_INPUT)
            else:
                correct = text_input.upper() == solution
                msg = ux.MSG_GUESS_OK if correct else ux.MSG_GUESS_KO
                send_message(user, msg)
                if correct:
                    send_typing_action(user, sleep_secs=0.5)
                    send_message(user, ux.MSG_EXPLANATIONS.format(explanations), remove_keyboard=True)
                    send_typing_action(user, sleep_secs=1)
                    redirect_to_state(user, state_CONTINUE)
        else:
            send_message(user, ux.MSG_WRONG_INPUT_USE_BUTTONS, kb)


# ================================
# CONTINUE State
# ================================
def state_CONTINUE(user, message_obj):
    if message_obj is None:
        kb = [
            [ux.BUTTON_YES, ux.BUTTON_NO]
        ]
        send_message(user, ux.MSG_CONTINUE, kb)            
    else: 
        kb = user.get_keyboard()
        if message_obj.text:            
            text_input = message_obj.text
            if text_input in utility.flatten(kb):
                if text_input == ux.BUTTON_YES:
                    redirect_to_state(user, state_GENERATOR)
                elif text_input == ux.BUTTON_NO:                    
                    restart_user(user)
                else:
                    assert(False)
            elif ux.text_is_button(text_input):
                send_message(user, ux.MSG_WRONG_BUTTON_INPUT)
            else:
                send_message(user, ux.MSG_WRONG_INPUT_USE_BUTTONS, kb)
        else:
            send_message(user, ux.MSG_WRONG_INPUT_USE_BUTTONS, kb)

# ================================
# ADMIN State
# ================================
def state_ADMIN(user, message_obj):
    pass    

def deal_with_universal_commands(user, text):
    if text in ['/start', '/help']:
        restart_user(user)
        return True
    if user.is_admin():
        if text == '/exception':
            1/0
            return True
        if text.startswith('/debug') and ' ' in text:
            on_off = text.lower().split()[1]
            if on_off in ['on','off']:
                user.debug = on_off == 'on'
                user.put()
                msg = "Debug attivato" if user.debug else "Debug disattivato"
                send_message(user, msg)    
                return True       
    return False    
    

@exception_reporter
def deal_with_request(request_json):
    # retrieve the message in JSON and then transform it to Telegram object
    update_obj = telegram.Update.de_json(request_json, TELEGRAM_BOT)
    message_obj = update_obj.message    
    if message_obj.chat.type != 'private':
        return
    user_obj = message_obj.from_user
    name = user_obj.first_name
    if user_obj.last_name:
        name += ' ' + user_obj.last_name
    user = NDB_User('telegram', user_obj.id, name, user_obj.username)
    
    if message_obj.text:
        logging.debug('TELEGRAM input message from @{} with text {}'.format(user.serial_number, message_obj.text))            
        if deal_with_universal_commands(user, message_obj.text):
            return
    repeat_state(user, message_obj=message_obj)    

possibles = globals().copy()
possibles.update(locals())

from flask import Flask, Response, request, jsonify
import key

import logging
import google.cloud.logging
client = google.cloud.logging.Client()
# logging.debug #format='%(asctime)s  [%(levelname)s]: %(message)s'
client.setup_logging(log_level=logging.DEBUG)


# If `entrypoint` is not defined in app.yaml, App Engine will look for an app
# called `app` in `main.py`.
app = Flask(__name__)


@app.route('/')
def root():
    logging.debug("in root function")
    """Return a friendly HTTP greeting."""
    return ("Progetto per risolvere in maniera automatica il gioco 'La Ghigliottina' parte del programma l'Eredità di Rai 1.", 200)

@app.route('/test')
def test():
    logging.debug("in test function")
    return ("test", 200)

@app.errorhandler(404)
def page_not_found(error):
    logging.debug("page_not_found: {}".format(error))
    # note that we set the 404 status explicitly
    return ("url not found", 404)

@app.errorhandler(500)
def internal_error(error):
    return ("500 error: {}".format(error), 500)

@app.route(key.WEBHOOK_TELEGRAM_ROUTING, methods=['POST'])
def telegram_webhook_handler():
    import telegram_bot
    import json
    request_json = request.get_json(force=True)

    logging.debug("TELEGRAM POST REQUEST: {}".format(json.dumps(request_json)))

    telegram_bot.deal_with_request(request_json)

    return ('', 200)


@app.route(key.WEBHOOK_TWITTER_ROUTING, methods=['GET'])
def twitter_webhook_challenger():
    from twitter_bot import solve_crc_challenge
    logging.debug("in twitter_webhook_challenger function")
    #import telegram_bot
    #telegram_bot.report_master("call to twitter_webhook_challenger")

    crc_token = request.args.get('crc_token')

    #logging.debug("crc_token: {}".format(crc_token))

    # construct response data with base64 encoded hash
    reponse_json = {
        'response_token': solve_crc_challenge(crc_token),
    }

    return jsonify(reponse_json)


@app.route(key.WEBHOOK_TWITTER_ROUTING, methods=['POST'])
def twitter_webhook_handler():
    import twitter_bot
    event_json = request.get_json()
    twitter_bot.deal_with_event(event_json)
    return ('', 200)


@app.route(key.WEBHOOK_ALEXA_SOLVER_ROUTING, methods=['POST'])
def webhook_alexa_solver():        
    import json    
    request_json = request.get_json(force=True, silent=True)
    logging.debug("ALEXA SOLVER WORDS POST REQUEST: {}".format(json.dumps(request_json)))
    # logging.debug("Content-Type: {}".format(request.content_type))
    import solver    
    clue_keys = ['w1', 'w2', 'w3', 'w4', 'w5']    
    if request_json and all(k in request_json for k in clue_keys):
        from ndb_user import get_webhook_solver_user
        user = get_webhook_solver_user()
        clues = [request_json[w] for w in clue_keys]
        solution, _, _ = solver.get_solution_from_clues(user, clues)
        clues_str = ', '.join(clues)
        result = {
            'success': True,
            'reason': 'success',            
            'answer': 'Credo che la soluzione per le parole: {}, sia: <emphasis level="strong">{}</emphasis>!'.format(clues_str, solution)
        }
    else:
        result = {
            'success': False,
            'reason': 'No keys w1, w2, w3, w4, w5 in input json',
            'answer': "Non ho capito le cinque parole. Prova iniziare la frase con, dammi la soluzione per le parole, seguito dalle cinque parole."
        }    
    return jsonify(result)

@app.route(key.WEBHOOK_ALEXA_LAST_GHIGLIOTTINA, methods=['GET'])
def webhook_alexa_last():        
    import json    
    import ndb_ghigliottina
    clues, solution, score, dt, today = ndb_ghigliottina.get_last_quizgame()
    logging.debug("ALEXA SOLVER LAST GET REQUEST: clues={} solution={} score={} dt={}".format(clues, solution, score, dt))
    clues_str = ', '.join(clues)
    if today:
        result = {
            'success': True,
            'answer': 'Credo che la soluzione della ghigliottina di questa sera con le parole: {}, sia: <emphasis level="strong">{}</emphasis>!'.format(clues_str, solution)
        }    
    else:
        result = {
            'success': True,
            'answer': 'Credo che la soluzione dell\'ultima ghigliottina con le parole: {}, sia: <emphasis level="strong">{}</emphasis>!'.format(clues_str, solution)
        }    
    return jsonify(result)

def send_quiztime_response_callback(clues, callback_url, game_id):
    import requests
    import solver
    from ndb_user import get_quiztime_user
    user = get_quiztime_user()
    solution, _, _ = solver.get_solution_from_clues(user, clues)        
    headers = {'Authorization': key.QUIZTIME_AUTHORIZATION}
    callback_data = {
        'game_id': game_id,
        'solution': solution,
        'uuid': key.QUIZTIME_USER_ID
    }   
    #logging.debug('Sending POST request to: {}'.format(callback_url))
    requests.post(callback_url, headers=headers, data=callback_data)
    #logging.debug("Return status: {}".format(r.status_code))

@app.route(key.WEBHOOK_QUIZTIME_ROUTING, methods=['POST'])
def quiztime_solver_handler():
    import json    
    import threading
    request_json = request.get_json(force=True)
    logging.debug("QUIZTIME POST REQUEST: {}".format(json.dumps(request_json)))
    auth_key = request.headers.get('Authorization')
    clue_keys = ['w1', 'w2', 'w3', 'w4', 'w5']
    game_id_key = 'game_id'
    callback_key = 'callback'
    required_keys = clue_keys + [game_id_key, callback_key]
    if auth_key == key.QUIZTIME_INPUT_AUTH and all(k in request_json for k in required_keys):
        clues = [request_json[w] for w in clue_keys]        
        callback_url = request_json[callback_key]        
        game_id = request_json[game_id_key]        
        threading.Thread(target=send_quiztime_response_callback,
            args=(clues, callback_url, game_id)
        ).start()
        
        result = {'success': True}
    else:
        result = {'success': False, 'reason': 'Invald request'}
    return jsonify(result)

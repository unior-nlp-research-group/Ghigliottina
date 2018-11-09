# -*- coding: utf-8 -*-

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


@app.errorhandler(404)
def page_not_found(e):
    logging.debug("page_not_found")
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

    return ('',200)


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
    return ('',200)


@app.route(key.WEBHOOK_SOLVER_ROUTING, methods=['POST'])
def solver_handler():
    import json
    import solver
    request_json = request.get_json(force=True)
    logging.debug("SOLVER POST REQUEST: {}".format(json.dumps(request_json)))
    clue_keys = ['w1', 'w2', 'w3', 'w4', 'w5']
    if all(k in request_json for k in clue_keys):
        clues = [request_json[w] for w in clue_keys]
        solution = solver.get_best_solution(clues)
        result = {
            'success': True,
            'solution': solution
        }
    else:
        result = {
            'success': False,
            'reason': 'No keys w1, w2, ... w3 in input json'
        }
    return jsonify(result)


@app.route(key.WEBHOOK_QUIZTIME_ROUTING, methods=['POST'])
def quiztime_solver_handler():
    import json
    import solver
    import threading
    request_json = request.get_json(force=True)
    logging.debug("SOLVER POST REQUEST: {}".format(json.dumps(request_json)))
    auth_key = request.headers.get('Authorization')
    clue_keys = ['w1', 'w2', 'w3', 'w4', 'w5']
    game_id_key = 'game_id'
    callback_key = 'callback'
    required_keys = clue_keys + [game_id_key, callback_key]
    if auth_key == key.QUIZTIME_INPUT_AUTH and all(k in request_json for k in required_keys):
        clues = [request_json[w] for w in clue_keys]
        solution = solver.get_best_solution(clues)        
        headers = {'Authorization': key.QUIZTIME_AUTHORIZATION}
        callback_url = request_json[callback_key]        
        callback_data = {
            game_id_key: request_json[game_id_key],
            'solution': solution,
            'uuid': key.QUIZTIME_USER_ID
        }   

        def send_response_callback(callback_url, headers, callback_data):
            import requests
            logging.debug('Sending POST request to: {}'.format(callback_url))
            r = requests.post(callback_url, headers=headers, data=callback_data)
            logging.debug("Return status: {}".format(r.status_code))
        
        threading.Thread(target=send_response_callback,
            args=(callback_url, headers, callback_data)
        ).start()
        
        result = {'success': True}
    else:
        result = {'success': False, 'reason': 'Invald request'}
    return jsonify(result)

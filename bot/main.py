# -*- coding: utf-8 -*-

from flask import Flask, Response, request, jsonify
import key

import logging


# If `entrypoint` is not defined in app.yaml, App Engine will look for an app
# called `app` in `main.py`.
app = Flask(__name__)

@app.route('/')
def root():
    logging.info("in root function")
    """Return a friendly HTTP greeting."""
    return "Progetto per risolvere in maniera automatica il gioco 'La Ghigliottina' parte del programma l'Eredità di Rai 1."

@app.errorhandler(404)
def page_not_found():
    logging.info("page_not_found")
    # note that we set the 404 status explicitly
    return "url not found"

@app.errorhandler(400)
def bad_request():
    logging.info("bad_request")
    # note that we set the 404 status explicitly
    return "bad request"

@app.route(key.WEBKOOK_TELEGRAM_ROUTING, methods=['POST'])
def telegram_webhook_handler():
    import telegram_bot
    import json
    request_json = request.get_json(force=True)

    logging.info("TELEGRAM POST REQUEST: {}".format(json.dumps(request_json)))

    telegram_bot.deal_with_request(request_json)

    return 'ok'

@app.route(key.WEBKOOK_TWITTER_ROUTING, methods=['GET'])
def twitter_webhook_challenger():
    from twitter import solve_crc_challenge
    logging.info("in twitter_webhook_challenger function")
    #import telegram_bot
    #telegram_bot.report_master("call to twitter_webhook_challenger")
    
    crc_token = request.args.get('crc_token')

    #logging.info("crc_token: {}".format(crc_token))

    # construct response data with base64 encoded hash
    reponse_json = {
        'response_token': solve_crc_challenge(crc_token),
    }

    return jsonify(reponse_json)

@app.route(key.WEBKOOK_TWITTER_ROUTING, methods=['POST'])
def twitter_webhook_handler():    
    import twitter
    import json
    event_json = request.get_json()
    logging.info("TWITTER POST REQUEST: {}".format(json.dumps(event_json)))
    twitter.deal_with_event(event_json)
    return 'ok'

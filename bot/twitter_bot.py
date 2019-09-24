#import tweepy
from TwitterAPI import TwitterAPI

import key
import json
import re
from string import punctuation
import solver

from exception_handler import exception_reporter

import logging
import response_formatter

from ndb_user import NDB_User

def test():
    from parameters import TWITTER_API_BASE
    from requests_oauthlib import OAuth1Session
    auth = OAuth1Session(
        key.TWITTER_CUSUMER_API_KEY, key.TWITTER_CUSUMER_API_SECRET,
        key.TWITTER_ACCESS_TOKEN, key.TWITTER_ACCESS_TOKEN_SECRET)
    url = TWITTER_API_BASE + 'account_activity/all/:{}/webhooks'.format(key.TWITTER_ENVNAME)
    r = auth.get(url, auth=auth)
    return r.text

# https://developer.twitter.com/en/docs/accounts-and-users/subscribe-account-activity/guides/managing-webhooks-and-subscriptions

api = TwitterAPI(
        key.TWITTER_CUSUMER_API_KEY, key.TWITTER_CUSUMER_API_SECRET,
        key.TWITTER_ACCESS_TOKEN, key.TWITTER_ACCESS_TOKEN_SECRET
    )

# https://developer.twitter.com/en/docs/accounts-and-users/subscribe-account-activity/api-reference/aaa-premium#post-account-activity-all-env-name-webhooks
# ok
def set_webhook():    
    r = api.request(
        'account_activity/all/:{}/webhooks'.format(key.TWITTER_ENVNAME), 
        {'url': key.WEBHOOK_TWITTER_BASE},
        method_override='POST'
    )
    #id = r.json()['id']
    return r.text

# https://developer.twitter.com/en/docs/accounts-and-users/subscribe-account-activity/api-reference/aaa-premium#get-account-activity-all-env-name-webhooks
# ok
def get_webhook_info():
    r = api.request(
        'account_activity/all/:{}/webhooks'.format(key.TWITTER_ENVNAME), 
        method_override='GET'
    )
    return r.text

# https://developer.twitter.com/en/docs/accounts-and-users/subscribe-account-activity/api-reference/aaa-premium#put-account-activity-all-env-name-webhooks-webhook-id
# ok
def trigger_CRC_request():
    r = api.request(
        'account_activity/all/:{}/webhooks/:{}'.format(key.TWITTER_ENVNAME, 1050757288418512896), 
        method_override='PUT'
    )
    return r.text

# https://developer.twitter.com/en/docs/accounts-and-users/subscribe-account-activity/api-reference/aaa-premium#post-account-activity-all-env-name-subscriptions
# ok (after resetting permission in twitter console)
def add_user_subscription():
    r = api.request(
        'account_activity/all/:{}/subscriptions'.format(key.TWITTER_ENVNAME), 
        method_override='POST'
    )
    return r.text

'''
# https://developer.twitter.com/en/docs/accounts-and-users/subscribe-account-activity/api-reference/aaa-premium#get-account-activity-all-env-name-subscriptions
def get_user_subscription():
    r = api.request(
        'account_activity/all/:{}/subscriptions'.format(key.TWITTER_ENVNAME), 
        method_override='POST'
    )
    return r.text

# https://developer.twitter.com/en/docs/accounts-and-users/subscribe-account-activity/api-reference/aaa-premium#delete-account-activity-all-env-name-webhooks-webhook-id
def delete_webhook():    
    r = api.request(
        'account_activity/all/:{}/webhooks'.format(key.TWITTER_ENVNAME), 
        method_override='DELETE'
    )
    return r.text

# https://developer.twitter.com/en/docs/accounts-and-users/subscribe-account-activity/api-reference/aaa-premium#delete-account-activity-all-env-name-subscriptions
def delete_user_subscription():
    r = api.request(
        'account_activity/all/:{}/subscriptions'.format(key.TWITTER_ENVNAME), 
        method_override='DELETE'
    )
    return r.text

# https://developer.twitter.com/en/docs/accounts-and-users/subscribe-account-activity/api-reference/aaa-premium#get-account-activity-all-env-name-subscriptions-list
def get_all_active_subscription():
    r = api.request(
        'account_activity/all/:{}/subscriptions/list'.format(key.TWITTER_ENVNAME), 
        method_override='GET'
    )
    return r.text
'''

def solve_crc_challenge(crc_token):
    # https://developer.twitter.com/en/docs/accounts-and-users/subscribe-account-activity/guides/securing-webhooks.html
    # https://developer.twitter.com/en/docs/accounts-and-users/subscribe-account-activity/guides/getting-started-with-webhooks
    import base64
    import hashlib
    import hmac   

    # creates HMAC SHA-256 hash from incomming token and your consumer secret
    sha256_hash_digest = hmac.new(
        key.TWITTER_CUSUMER_API_SECRET.encode('utf-8'), 
        msg=crc_token.encode('utf-8'), 
        digestmod=hashlib.sha256
    ).digest()

    return 'sha256=' + base64.b64encode(sha256_hash_digest).decode('utf-8')


def get_user_info(key, value):
    assert key in ['user_id', 'screen_name']
    r = api.request('users/lookup', {key:value})
    if r.status_code == 200:
        user_info = r.json()
        return {
            'user_id': user_info[0]['id'],
            'screen_name': user_info[0]['screen_name'],
            'name': user_info[0]['name'],
        }
    return {}

def send_message(user_id, message_text):

    event = {
        "event": {
            "type": "message_create",
            "message_create": {
                "target": {
                    "recipient_id": user_id
                },
                "message_data": {
                    "text": message_text
                }
            }
        }
    }

    r = api.request('direct_messages/events/new', json.dumps(event))
    print('SUCCESS' if r.status_code == 200 else 'PROBLEM: ' + r.text)

def post_retweet(message_text, original_tweet_id=None):
    if original_tweet_id:
        r = api.request('statuses/update', {'status': message_text, 'in_reply_to_status_id':original_tweet_id})        
    else:
        r = api.request('statuses/update', {'status': message_text})
    print('SUCCESS' if r.status_code == 200 else 'PROBLEM: ' + r.text)
 
@exception_reporter
def deal_with_event(event_json):
    if 'direct_message_events' in event_json:
        process_direct_message(event_json)
    elif 'tweet_create_events' in event_json:
        process_tweet_post(event_json)                
            

def process_direct_message(event_json):
    message_info = event_json['direct_message_events'][0]['message_create']
    sender_id = message_info['sender_id']    
    if sender_id != key.TWITTER_BOT_ID:
        logging.debug("TWITTER DIRECT MESSAGE: {}".format(json.dumps(event_json)))
        sender_screen_name = event_json['users'][sender_id]['screen_name']
        sender_name = get_user_info('user_id', sender_id).get('name', None)
        user = NDB_User('twitter', sender_id, name=sender_name, username=sender_screen_name)
        message_text = message_info['message_data']['text']
        reply_text, _ = solver.get_solution_from_text(user, message_text)
        logging.debug('TWITTER Reply to direct message from @{} with text {} -> {}'.format(sender_screen_name, message_text, reply_text))
        send_message(sender_id, reply_text)

def process_tweet_post(event_json):    
    tweet_info = event_json['tweet_create_events'][0]
    if 'retweeted_status' in tweet_info:
        logging.debug('Retweet detected')
        return
    message_text = tweet_info['text']
    user_info = tweet_info['user']
    sender_screen_name = user_info['screen_name']
    mentions_screen_name = [
        x['screen_name'] 
        for x in tweet_info['entities']['user_mentions'] 
        if x['screen_name']!=key.TWITTER_BOT_SCREEN_NAME
    ]
    if sender_screen_name != key.TWITTER_BOT_SCREEN_NAME:  
        logging.debug("TWITTER POST REQUEST: {}".format(json.dumps(event_json)))
        sender_id = user_info['id']
        sender_name = user_info['name']
        user = NDB_User('twitter', sender_id, name=sender_name, username=sender_screen_name)
        message_text = re.sub(r'(#|@)\w+','',message_text).strip()
        message_text = ''.join(c for c in message_text if c==',' or c not in punctuation)
        reply_text, correct = solver.get_solution_from_text(user, message_text)
        if correct and 'è' in message_text.split():
            correct = False
        tweet_image_url = tweet_info.get('entities',{}).get('media',[{}])[0].get('media_url',None)
        if not correct:            
            if tweet_image_url:
                import vision
                logging.debug('TWITTER deteceted image. File_url: {}'.format(tweet_image_url))
                clues_list = vision.detect_clues(image_uri=tweet_image_url)      
                reply_text, correct = solver.get_solution_from_image(user, clues_list)        
        if correct or tweet_image_url:
            reply_text = '@{} {}'.format(sender_screen_name, reply_text)
            if mentions_screen_name:
                reply_text += ' ' + ' '.join(['@{}'.format(x) for x in mentions_screen_name])            
            tweet_id = tweet_info['id']
            post_retweet(reply_text, tweet_id)       
            logging.debug('TWITTER Reply to tweet from @{} with text {} -> {}'.format(sender_screen_name, message_text, reply_text))
        else:
            sender_id = tweet_info['user']['id']     
            send_message(sender_id, reply_text)
            logging.debug('IGNORED TWITTER Reply to tweet from @{} with text {} -> {}'.format(sender_screen_name, message_text, reply_text))
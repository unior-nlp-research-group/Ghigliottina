import tweepy
from TwitterAPI import TwitterAPI

import key
import json
import re
import solver

from exception_handler import exception_reporter

from requests_oauthlib import OAuth1Session
from parameters import TWITTER_API_BASE
import logging
import ui

def test():
    auth = OAuth1Session(
        key.TWITTER_CUSUMER_API_KEY, key.TWITTER_CUSUMER_API_SECRET,
        key.TWITTER_ACCESS_TOKEN, key.TWITTER_ACCESS_TOKEN_SECRET)
    url = TWITTER_API_BASE + 'account_activity/all/:{}/webhooks'.format(key.TWITTER_ENVNAME)
    r = auth.get(url, auth=auth)
    return r.text



def test_tweepy():
    auth = tweepy.OAuthHandler(key.TWITTER_CUSUMER_API_KEY, key.TWITTER_CUSUMER_API_SECRET)
    auth.set_access_token(key.TWITTER_ACCESS_TOKEN, key.TWITTER_ACCESS_TOKEN_SECRET)

    tweepy_api = tweepy.API(auth)

    public_tweets = tweepy_api.home_timeline()

    for tweet in public_tweets:
        print(tweet.text)

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
        {'url': key.WEBKOOK_TWITTER_BASE},
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


def get_user_id(screen_name):
        r = api.request('users/lookup', {'screen_name':screen_name})
        if r.status_code == 200:
            return r.json()[0]['id']
        return None

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
        if 'retweeted_status' not in event_json:
            process_tweet_post(event_json)        

def process_direct_message(event_json):
    message_info = event_json['direct_message_events'][0]['message_create']
    sender_id = message_info['sender_id']
    sender_screen_name = event_json['users'][sender_id]['screen_name']
    if sender_id != key.TWITTER_BOT_ID:
        message_text = message_info['message_data']['text']
        reply_text, _ = solver.get_solution_from_text(message_text, from_twitter=True)
        logging.info('TWITTER Reply to direct message from @{} with text {} -> {}'.format(sender_screen_name, message_text, reply_text))
        send_message(sender_id, reply_text)

def process_tweet_post(event_json):
    tweet_info = event_json['tweet_create_events'][0]
    message_text = tweet_info['text']
    sender_screen_name = tweet_info['user']['screen_name']            
    mentions_screen_name = [
        x['screen_name'] 
        for x in tweet_info['entities']['user_mentions'] 
        if x['screen_name']!=key.TWITTER_BOT_SCREEN_NAME
    ]
    if sender_screen_name != key.TWITTER_BOT_SCREEN_NAME:          
        message_text = re.sub(r'(#|@)\w+','',message_text).strip()        
        reply_text, correct = solver.get_solution_from_text(message_text, from_twitter=True)
        tweet_image_url = tweet_info.get('entities',{}).get('media',[{}])[0].get('media_url',None)
        if not correct:            
            if tweet_image_url:
                import vision
                logging.info('TWITTER File_url: {}'.format(tweet_image_url))
                clues_list = vision.detect_clues(image_uri=tweet_image_url)      
                reply_text, correct = solver.get_solution_from_image_clues(clues_list, from_twitter=True)        
        if correct or tweet_image_url:
            reply_text = '@{} {}'.format(sender_screen_name, reply_text)
            if mentions_screen_name:
                reply_text += ' ' + ' '.join(['@{}'.format(x) for x in mentions_screen_name])            
            tweet_id = tweet_info['id']
            post_retweet(reply_text, tweet_id)       
            logging.info('TWITTER Reply to tweet from @{} with text {} -> {}'.format(sender_screen_name, message_text, reply_text))
        else:
            sender_id = tweet_info['user']['id']     
            send_message(sender_id, reply_text)
            logging.info('IGNORED TWITTER Reply to tweet from @{} with text {} -> {}'.format(sender_screen_name, message_text, reply_text))
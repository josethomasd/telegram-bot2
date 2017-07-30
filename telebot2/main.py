# -*- coding: utf-8 -*-
import StringIO
import json
import logging
import urllib
import urllib2

# standard app engine imports
from google.appengine.api import urlfetch
from google.appengine.ext import ndb

import webapp2

#for fixing emoji
import sys
reload(sys)  
sys.setdefaultencoding('utf8')

TOKEN = '392793406:AAGGFJW1XOelq1-McaAKlgL-jnygPve-r0Q'

BASE_URL = 'https://api.telegram.org/bot' + TOKEN + '/'


# ================================

class EnableStatus(ndb.Model):
    # key name: str(chat_id)
    enabled = ndb.BooleanProperty(indexed=False, default=False)


class GroupEnableStatus(ndb.Model):
    # key name: str(chat_id)
    enabled = ndb.BooleanProperty(indexed=True, default=False)
    group_id = ndb.StringProperty()
# ================================

def setEnabled(chat_id, yes):
    es = EnableStatus.get_or_insert(str(chat_id))
    es.enabled = yes
    es.put()

def getEnabled(chat_id):
    es = EnableStatus.get_by_id(str(chat_id))
    if es:
        return es.enabled
    return False

def setgroupEnabled(chat_id, yes):
    es = GroupEnableStatus.get_or_insert(str(chat_id))
    es.enabled = yes
    es.group_id = str(chat_id)
    es.put()

def getgroupEnabled(chat_id):
    es = GroupEnableStatus.get_by_id(str(chat_id))
    if es:
        return es.enabled
    return False
# ================================

class HelloWorld(webapp2.RequestHandler):
    def get(self):
        self.response.write('Hello World')


class MeHandler(webapp2.RequestHandler):
    def get(self):
        urlfetch.set_default_fetch_deadline(60)
        self.response.write(json.dumps(json.load(urllib2.urlopen(BASE_URL + 'getMe'))))


class GetUpdatesHandler(webapp2.RequestHandler):
    def get(self):
        urlfetch.set_default_fetch_deadline(60)
        self.response.write(json.dumps(json.load(urllib2.urlopen(BASE_URL + 'getUpdates'))))


class SetWebhookHandler(webapp2.RequestHandler):
    def get(self):
        urlfetch.set_default_fetch_deadline(60)
        url = self.request.get('url')
        if url:
            self.response.write(json.dumps(json.load(urllib2.urlopen(BASE_URL + 'setWebhook', urllib.urlencode({'url': url})))))


class WebhookHandler(webapp2.RequestHandler):
    def post(self):
        urlfetch.set_default_fetch_deadline(60)
        body = json.loads(self.request.body)
        logging.info('request body:')
        logging.info(body)
        self.response.write(json.dumps(body))

        update_id = body['update_id']
        try:
            message = body['message']
        except:
            message = body['edited_message']
        message_id = message.get('message_id')
        date = message.get('date')
        text = message.get('text')
        fr = message.get('from')
        chat = message['chat']
        chat_id = chat['id']
        chat_type = chat['type']

        if not text:
            logging.info('no text')
            return

        def reply(msg=None, img=None):
            if msg:
                resp = urllib2.urlopen(BASE_URL + 'sendMessage', urllib.urlencode({
                    'chat_id': str(chat_id),
                    'text': msg.encode('utf-8'),
                    'disable_web_page_preview': 'true',
                    'reply_to_message_id': str(message_id),
                })).read()
            else:
                logging.error('no msg specified')
                resp = None

            logging.info('send response:')
            logging.info(resp)

        if text.startswith('/'):
            if text == '/start':
                reply('Bot enabled')
                setEnabled(chat_id, True)
                if chat_type=='supergroup' or chat_type=='group':
                    setgroupEnabled(chat_id,True)
            elif text == '/stop':
                reply('Bot disabled')
                setEnabled(chat_id, False)
                if chat_type=='supergroup' or chat_type=='group':
                    setgroupEnabled(chat_id, False)
            else:
                reply('What command?')

        # CUSTOMIZE FROM HERE

        elif 'who are you' in text:
            reply('I am a bot')
        elif 'what time' in text:
            reply('look at the corner of your screen!')
        else:
            if getEnabled(chat_id):
                reply('Please dm @insta_millionaires')
            else:
                logging.info('not enabled for chat_id {}'.format(chat_id))

class MsgHandler(webapp2.RequestHandler):
    def get(self): 
        msg = '🔥POWERLIKES 🔥\n\n📌Get Likes When You Post!\n📌 100s BIG Accs Liking Your Posts!\n📌  Network 🔝110🔝 Million Followers!\n📌 Reach Explore & Go Viral! \n\n📍No Password Required\n⚡Pm @insta_millionaires or @millioniaresquad ⚡'
        q = ndb.gql("SELECT * FROM GroupEnableStatus WHERE enabled=True")
        for grpid in q:
            st = grpid.group_id
            resp = urllib2.urlopen(BASE_URL + 'sendMessage', urllib.urlencode({
                'chat_id': st,
                'text': msg.decode().encode('UTF-8'),
            })).read()
        self.response.write("ok")

app = webapp2.WSGIApplication([
    ('/', HelloWorld),
    ('/me', MeHandler),
    ('/updates', GetUpdatesHandler),
    ('/set_webhook', SetWebhookHandler),
    ('/webhook', WebhookHandler),
    ('/msg1', MsgHandler)
], debug=True)

# -*- coding: utf-8 -*-

from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.api import taskqueue

from base import BaseHandler
from django.utils import simplejson as json
from urllib import urlencode
from twitdao import Twitdao

import md
import twitpic2


class UserTimeline(BaseHandler):
    def get(self, screen_name, slug):

        params = self.params([
            'user_id',
            'since_id',
            'max_id',
            'count',
            'page',
            'trim_user',
            'include_rts',
            'include_entities',
        ],include_rts='true')

        token = md.get_proxy_access_token()
        #if not token:
        #    token = md.get_proxy_access_token()
        if not token:
            self.write(json.dumps({
                'success':False,
                'info':'No access token avaliable.',
            }))
            return

        td = Twitdao(token)
        owner_user = td.users_show_by_screen_name( screen_name=screen_name, **params)
        token_user = td.users_show_by_id(user_id = token.user_id)
        timeline = td.user_timeline(screen_name=screen_name, **params)
        tweets = self.render('ajax/user-user.html', {
            'token':token,
            #'token_user':token_user,
            'owner_user':owner_user,
            'timeline':timeline,
        },out=False)

        if slug == 'refresh':
            next_params={}
            count=0
            if type(timeline) == list and len(timeline):
                next_params['since_id'] = str(timeline[0]['id'])
                count = len(timeline)
            else:
                tweets=''
                next_params['since_id'] = str(params['since_id'])
                count = 0

            self.write(json.dumps({
                'success':True,
                'info':'OK',
                'tweets':tweets,
                'params':next_params,
                'count':count,
            }))
        else:
            next_params={}
            count=0
            if type(timeline) == list and len(timeline):
                next_params['max_id'] = str(timeline[-1]['id']-1)
                count = len(timeline)
            else:
                tweets=''
                next_params['max_id'] = str(params['max_id'])
                count = 0

            self.write(json.dumps({
                'success':True,
                'info':'OK',
                'tweets':tweets,
                'params':next_params,
                'count':count,
                'href':'/user/%s?%s' % (screen_name, urlencode(next_params))
            }))

class ShowStatus(BaseHandler):
    def get(self, status_id):

        params = self.params(['trim_user','include_entities'])
        
        token = md.get_proxy_access_token()
        if not token:
            self.redirect('/settings')
            return
        td = Twitdao(token)
        token_user = td.users_show_by_id(user_id = token.user_id)
        owner_user = token_user
        tweet = td.statuses_show(id=status_id,**params)

        self.render('tweet-show-proxy.html', {
            'token':token,
            #'token_user':token_user,
            'owner_user':owner_user,
            'tweet':tweet,
        })
class AjaxShowStatus(BaseHandler):
    def get(self, id):
        params = self.params(['trim_user','include_entities'])

        token = md.get_default_access_token()
        if not token:
            self.write(json.dumps({
                'success':False,
                'info':'No access token avaliable.',
            }))
            return

        td = Twitdao(token)
        token_user = td.users_show_by_id(user_id = token.user_id)
        tweet = td.statuses_show(id=id, **params)
        tweet_html = self.render('ajax/user-tweet.html', {
            'token':token,
            #'token_user':token_user,
            'tweet':tweet,
        }, out=False)

        self.write(json.dumps({
            'tweet':tweet_html if 'error' not in tweet else None,
            'success':'error' not in tweet,
            'info':tweet['error'] if 'error' in tweet else 'OK',
        }))


def main():
    application = webapp.WSGIApplication([
        ('/x1/user/([0-9a-zA-Z_]+)/(refresh|more)', UserTimeline),
        ('/x1/statuses/([0-9]+)', ShowStatus),
        ('/x1/show/([0-9]+)', AjaxShowStatus),
    ], debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()

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

class UpdateStatus(BaseHandler):

    def post(self):
        status = self.param('status')
        
        params = self.params([
            'in_reply_to_status_id',
            'lat',
            'long',
            'place_id',
            'display_coordinates',
            'trim_user',
            'include_entities',
        ])

        token = md.get_default_access_token()
        if not token:
            self.write(json.dumps({
                'success':False,
                'info':'No access token avaliable.',
            }))
            return

        td = Twitdao(token)
        tweet = td.statuses_update(status=status.encode('utf-8'), **params)
        taskqueue.add(queue_name='cache', url='/q/update_user_cache', params={'tk':token.key(), 'user_id':token.user_id}, method="GET" )
        self.write(json.dumps({
            'success':'error' not in tweet,
            'info':tweet['error'] if 'error' in tweet else 'OK',
            'tweet':tweet if 'error' not in tweet else None,
        }))

class UploadImage(BaseHandler):
    def post(self):
        media = self.param('media')

        token = md.get_default_access_token()
        if not token:
            self.write(json.dumps({
                'success':False,
                'info':'No access token avaliable.',
            }))
            return
        app_config = md.get_app_config()
        
        td = Twitdao(token)

        twitpic = twitpic2.TwitPic2(
            consumer_key = app_config.consumer_key,
            consumer_secret = app_config.consumer_secret,
            access_token = 'oauth_token=%s&oauth_token_secret=%s' % (token.oauth_token, token.oauth_token_secret),
            service_key = app_config.twitpic_api_key,
        )

        try:
            if media:
                filename=self.request.POST[u'media'].filename.encode('utf-8')
                resp=twitpic.api_call('POST', 'upload', {'message':''}, files=[('media', filename, media)])
            self.write(json.dumps({
                'success':'id' in resp,
                'info':'OK',
                'response':resp,
            }))
        except Exception, e:
            self.write(json.dumps({
                'success':False,
                'info':str(e),
                'response':None,
            }))
        except:
            self.write(json.dumps({
                'success':False,
                'info':'Unkown Error.',
                'response':None,
            }))

class ShowStatus(BaseHandler):
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
        tweet_html = self.render('ajax/tweet.html', {
            'token':token,
            'token_user':token_user,
            'tweet':tweet,
        }, out=False)

        self.write(json.dumps({
            'tweet':tweet_html if 'error' not in tweet else None,
            'success':'error' not in tweet,
            'info':tweet['error'] if 'error' in tweet else 'OK',
        }))

class HomeTimeline(BaseHandler):
    def get(self, slug):
        
        params=self.params([
            'since_id',
            'max_id',
            'count',
            'page',
            'trim_user',
            'include_rts',
            'include_entities'
        ])
        params['count'] = 100

        token = md.get_default_access_token()
        if not token:
            self.write(json.dumps({
                'success':False,
                'info':'No access token avaliable.',
            }))
            return

        td = Twitdao(token)
        token_user = td.users_show_by_id(user_id = token.user_id)
        timeline = td.home_timeline(**params)
        tweets = self.render('ajax/home.html', {
            'token':token,
            'token_user':token_user,
            'timeline':timeline,
        }, out=False)

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
                'count':count
            }))
        else:
            next_params={}
            count=0
            if type(timeline) == list and len(timeline):
                next_params['max_id'] = str(timeline[-1]['id']-1)
                count = len(timeline)
            else:
                tweet=''
                next_params['max_id'] = str(params['max_id'])
                count = 0

            self.write(json.dumps({
                'success':True,
                'info':'OK',
                'tweets':tweets,
                'params':next_params,
                'count':count,
                'href':'/t?%s' % urlencode(next_params)
            }))


class Mentions(BaseHandler):
    def get(self, slug):

        params=self.params([
            'since_id',
            'max_id',
            'count',
            'page',
            'trim_user',
            'include_rts',
            'include_entities'
        ])

        token = md.get_default_access_token()
        if not token:
            self.write(json.dumps({
                'success':False,
                'info':'No access token avaliable.',
            }))
            return 

        td = Twitdao(token)
        token_user = td.users_show_by_id(user_id = token.user_id)
        timeline = td.mentions(**params)
        tweets = self.render('ajax/mentions.html', {
            'token':token,
            'token_user':token_user,
            'timeline':timeline,
        }, out=False)

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
                'count':count
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
                'href':'/t/mentions?%s' % urlencode(next_params)
            }))



class Retweets(BaseHandler):
    def get(self, which, slug):

        params=self.params([
            'since_id',
            'max_id',
            'count',
            'page',
            'trim_user',
            'include_entities',
        ])

        token = md.get_default_access_token()
        if not token:
            self.write(json.dumps({
                'success':False,
                'info':'No access token avaliable.',
            }))
            return 

        td = Twitdao(token)
        timeline=[]
        if which == 'retweeted_by_me':
            timeline = td.retweeted_by_me(**params)
        elif which == 'retweeted_to_me':
            timeline = td.retweeted_to_me(**params)
        elif which == 'retweeted_of_me':
            timeline = td.retweets_of_me(**params)
        token_user = td.users_show_by_id(user_id = token.user_id)
        tweets = self.render('ajax/retweets.html', {
            'token':token,
            'token_user':token_user,
            'timeline':timeline,
        }, out=False)

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
                'count':count
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
                'href':'/t/retweets/%s?%s' % (which, urlencode(next_params))
            }))



class RetweetedBy(BaseHandler):
    def get(self, tweet_id):

        params = self.params([
            'count',
            'page',
            'trim_user',
            'include_entities'
        ], include_entities='0')
        #default count number is 20.

        token = md.get_default_access_token()
        if not token:
            self.write(json.dumps({
                'success':False,
                'info':'No access token avaliable.',
            }))
            return

        td = Twitdao(token)
        token_user = td.users_show_by_id(user_id = token.user_id)
        owner_user = token_user
        users = td.statuses_retweeted_by(id=tweet_id, **params)

        retweeted_by = self.render('ajax/retweeted-by.html', {
            'token':token,
            'token_user':token_user,
            'owner_user':owner_user,
            'users':users,
        },out=False)

        self.write(json.dumps({
            'success':True,
            'info':'OK',
            'retweeted_by':retweeted_by,
        }))


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

        token = md.get_default_access_token()
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
        tweets = self.render('ajax/user.html', {
            'token':token,
            'token_user':token_user,
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
                'href':'/t/%s?%s' % (screen_name, urlencode(next_params))
            }))


class Favorite(BaseHandler):
    def post(self, status_id, slug):
        params = self.params(['include_entities'])
        token = md.get_default_access_token()
        if not token:
            self.write(json.dumps({
                'success':False,
                'info':'No access token avaliable.',
            }))
            return
        
        td = Twitdao(token)
        tweet=None
        if slug=='create':
            tweet = td.favorites_create(id=status_id, **params)
        elif slug=='delete':
            tweet = td.favorites_destroy(id=status_id, **params)
        taskqueue.add(queue_name='cache', url='/q/update_user_cache', params={'tk':token.key(), 'user_id':token.user_id}, method="GET" )
        
        self.write(json.dumps({
            'tweet':tweet if 'error' not in tweet else None,
            'success':'error' not in tweet,
            'info':tweet['error'] if 'error' in tweet else 'OK',
        }))

class Retweet(BaseHandler):
    def post(self, id):
        params = self.params(['trim_user','include_entities'])
        token = md.get_default_access_token()
        if not token:
            self.write(json.dumps({
                'success':False,
                'info':'No access token avaliable.',
            }))
            return
        
        td = Twitdao(token)
        tweet = td.statuses_retweet(id=id, **params)
        taskqueue.add(queue_name='cache', url='/q/update_user_cache', params={'tk':token.key(), 'user_id':token.user_id}, method="GET" )
        self.write(json.dumps({
            'tweet':tweet if 'error' not in tweet else None,
            'success':'error' not in tweet,
            'info':tweet['error'] if 'error' in tweet else 'OK',
        }))


class DeleteStatus(BaseHandler):
    def post(self, id):
        params = self.params(['trim_user','include_entities'])

        token = md.get_default_access_token()
        if not token:
            self.write(json.dumps({
                'success':False,
                'info':'No access token avaliable.',
            }))
            return
        
        td = Twitdao(token)
        tweet = td.statuses_destroy(id=id, **params)
        taskqueue.add(queue_name='cache', url='/q/update_user_cache', params={'tk':token.key(), 'user_id':token.user_id}, method="GET" )
        self.write(json.dumps({
            'tweet':tweet if 'error' not in tweet else None,
            'success':'error' not in tweet,
            'info':tweet['error'] if 'error' in tweet else 'OK',
        }))

#TODO
#lists, 

class Follow(BaseHandler):
    def post(self,screen_name, slug):
        token = md.get_default_access_token()
        if not token:
            self.write(json.dumps({
                'success':False,
                'info':'No access token avaliable.',
            }))
            return

        td = Twitdao(token)
        fuser=None
        if 'make' == slug:
            fuser = td.friendships_create(screen_name = screen_name)
        else:
            fuser = td.friendships_destroy(screen_name = screen_name)
        taskqueue.add(queue_name='cache', url='/q/update_user_cache', params={'tk':token.key(), 'user_id':token.user_id}, method="GET" )
        taskqueue.add(queue_name='cache', url='/q/update_user_cache', params={'tk':token.key(), 'screen_name':screen_name}, method="GET" )

        if 'error' in fuser:
            self.write(json.dumps({
                'success':False,
                'info':fuser['error'],
            }))
        else:
            self.write(json.dumps({
                'success':True,
                'info':'OK',
                'user':fuser,
            }))


class Block(BaseHandler):
    def post(self, screen_name, slug):
        token = md.get_default_access_token()
        if not token:
            self.write(json.dumps({
                'success':False,
                'info':'No access token avaliable.',
            }))
            return

        td = Twitdao(token)
        buser=None
        if 'add' == slug:
            buser = td.blocks_create(screen_name = screen_name)
        else:
            buser = td.blocks_destroy(screen_name = screen_name)
        taskqueue.add(queue_name='cache', url='/q/update_user_cache', params={'tk':token.key(), 'user_id':token.user_id}, method="GET" )
        taskqueue.add(queue_name='cache', url='/q/update_user_cache', params={'tk':token.key(), 'screen_name':screen_name}, method="GET" )

        if 'error' in buser:
            self.write(json.dumps({
                'success':False,
                'info':buser['error'],
            }))
        else:
            self.write(json.dumps({
                'success':True,
                'info':'OK',
                'user':buser,
            }))


class ReportSpam(BaseHandler):
    def post(self, screen_name):
        token = md.get_default_access_token()
        if not token:
            self.write(json.dumps({
                'success':False,
                'info':'No access token avaliable.',
            }))
            return

        td = Twitdao(token)
        ruser = td.report_spam(screen_name = screen_name)
        taskqueue.add(queue_name='cache', url='/q/update_user_cache', params={'tk':token.key(), 'user_id':token.user_id}, method="GET" )
        taskqueue.add(queue_name='cache', url='/q/update_user_cache', params={'tk':token.key(), 'screen_name':screen_name}, method="GET" )

        if 'error' in ruser:
            self.write(json.dumps({
                'success':False,
                'info':ruser['error'],
            }))
        else:
            self.write(json.dumps({
                'success':True,
                'info':'OK',
                'user':ruser,
            }))


class Blocking(BaseHandler):
    def get(self):
        pass

class SavedSearch(BaseHandler):
    def get(self):
        pass


class MessageSend(BaseHandler):
    def post(self):
        screen_name = self.param('screen_name')
        user_id = self.param('user_id')
        text = self.param('text')

        params = self.params(['include_entities'])

        token = md.get_default_access_token()
        if not token:
            self.write(json.dumps({
                'success':False,
                'info':'No access token avaliable.',
            }))
            return
        
        td = Twitdao(token)
        message = td.direct_messages_new(user_id=user_id, screen_name=screen_name, text=text.encode('utf-8'), **params)

        if 'error' in message:
            self.write(json.dumps({
                'success':False,
                'info':message['error'],
            }))
        else:
            self.write(json.dumps({
                'success':True,
                'info':'OK',
                'message':message,
            }))

class MessageDestroy(BaseHandler):
    def post(self, id):
        params = self.params(['include_entities'])
        
        token = md.get_default_access_token()
        if not token:
            self.write(json.dumps({
                'success':False,
                'info':'No access token avaliable.',
            }))
            return
        
        td = Twitdao(token)
        message = td.direct_messages_destroy(id=id, **params)

        if 'error' in message:
            self.write(json.dumps({
                'success':False,
                'info':message['error'],
            }))
        else:
            self.write(json.dumps({
                'success':True,
                'info':'OK',
                'message':message,
            }))


class ListTimeline(BaseHandler):
    def get(self, screen_name, slug, xlug):
        
        params = self.params(['since_id','max_id','per_page','page','include_entities'])

        token = md.get_default_access_token()
        if not token:
            self.redirect('/settings')
            return

        td = Twitdao(token)
        token_user = td.users_show_by_id(user_id = token.user_id)
        owner_user = td.users_show_by_screen_name(screen_name = screen_name)
        #ls = td.user_list_id_get(id=slug, screen_name=screen_name)
        timeline = td.user_list_id_statuses(id=slug, screen_name = screen_name, **params)

        tweets=self.render('ajax/list.html', {
            'token':token,
            'token_user':token_user,
            'owner_user':owner_user,
            #'list':ls,
            'timeline':timeline,
        },out=False)

        if xlug == 'refresh':
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
                'href':'/t/%s/%s?%s'% (screen_name, slug, urlencode(next_params))
            }))


class HackedSearch(BaseHandler):
    def get(self, slug):
        q = self.param('q')
        since_id=self.param('since_id')
        page=self.param('page')

        token = md.get_default_access_token()
        if not token:
            self.write(json.dumps({
                'success':False,
                'info':'Token error.'
            }))
            return

        td = Twitdao(token)
        token_user = td.users_show_by_id(user_id = token.user_id)
        owner_user = token_user

        searchd=td.hacked_search(q.encode('utf-8'), since_id, page)
        timeline=searchd['statuses']

        count=0
        next_params={'q':q}
        if slug=='refresh':
            if type(timeline) == list and len(timeline):
                next_params['since_id'] = str(timeline[0]['id'])
            else:
                next_params['since_id'] = str(since_id)
        elif slug=='more':
                next_params['page'] = searchd['next_page']
        count = len(timeline)

        tweets=self.render('ajax/hacked_search.html', {
            'token':token,
            'token_user':token_user,
            'owner_user':owner_user,
            'timeline':timeline,
        },out=False)

        self.write(json.dumps({
            'success':True,
            'info':'OK',
            'tweets':tweets,
            'params':next_params,
            'count':count,
            'href': '/a/search?%s' % urlencode({'page':searchd['next_page'], 'q':q.encode('utf-8')})
        }))


class HackedFollowingFollowersOf(BaseHandler):
    def get(self):
        user_id = self.param('user_id')

        token = md.get_default_access_token()
        if not token:
            self.write(json.dumps({
                'success':False,
                'info':'Token error.'
            }))
            return

        td = Twitdao(token)
        token_user = td.users_show_by_id(user_id = token.user_id)
        owner_user = token_user

        res=td.hacked_following_followers_of(user_id)
        tweets=self.render('ajax/following_followers_of.html', {
            'token':token,
            'token_user':token_user,
            'owner_user':owner_user,
            'res':res,
        },out=False)

        self.write(json.dumps({
            'success':True,
            'info':'OK',
            'html':tweets,
        }))


class HackedFollowsInCommonWith(BaseHandler):
    def get(self):
        user_id = self.param('user_id')

        token = md.get_default_access_token()
        if not token:
            self.write(json.dumps({
                'success':False,
                'info':'Token error.'
            }))
            return

        td = Twitdao(token)
        token_user = td.users_show_by_id(user_id = token.user_id)
        owner_user = token_user

        res=td.hacked_follows_in_common_with(user_id)
        tweets=self.render('ajax/follows_in_common_with.html', {
            'token':token,
            'token_user':token_user,
            'owner_user':owner_user,
            'res':res,
        },out=False)

        self.write(json.dumps({
            'success':True,
            'info':'OK',
            'html':tweets,
        }))


def main():
    application = webapp.WSGIApplication([
        ('/x/update', UpdateStatus),
        ('/x/delete/([0-9]+)', DeleteStatus),
        ('/x/show/([0-9]+)', ShowStatus),

        ('/x/home/(refresh|more)', HomeTimeline),

        ('/x/mentions/(refresh|more)', Mentions),

        ('/x/retweets/(retweeted_by_me|retweeted_to_me|retweeted_of_me)/(refresh|more)', Retweets),
        ('/x/retweet/([0-9]+)', Retweet),
        ('/x/retweeted_by/([0-9]+)', RetweetedBy),
        
        ('/x/user/([0-9a-zA-Z_]+)/(refresh|more)', UserTimeline),

        ('/x/list/([0-9a-zA-Z_]+)/([0-9a-zA-Z\-%]+)/(refresh|more)', ListTimeline),

        ('/x/message_send', MessageSend),
        ('/x/message_destroy/([0-9]+)', MessageDestroy),

        ('/x/favorite/([0-9]+)/(create|delete)', Favorite),
        
        ('/x/friends/([0-9a-zA-Z_]+)/(make|break)', Follow),

        ('/x/block/([0-9a-zA-Z_]+)/(add|remove)', Block),

        ('/x/report/([0-9a-zA-Z_]+)', ReportSpam),
        ('/x/upload_image', UploadImage),

        ('/x/search/(refresh|more)', HackedSearch),
        ('/x/following_followers_of', HackedFollowingFollowersOf),
        ('/x/follows_in_common_with', HackedFollowsInCommonWith),

    ], debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()

# -*- coding: utf-8 -*-
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.api import users
from google.appengine.api import taskqueue

from base import BaseHandler
from twitdao import Twitdao

import md
import utils
import twitpic2

import logging


class Home(BaseHandler):
    def get(self):
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
            self.redirect('/settings')
            return

        td = Twitdao(token)
        token_user = td.users_show_by_id(user_id = token.user_id)
        owner_user = token_user
        timeline = td.home_timeline(**params)
        if 'error' in timeline:
            timeline=[]
        self.render('mobile/home.html', {
            'token':token,
            'token_user':token_user,
            'owner_user':owner_user,
            'timeline':timeline,
            'max_id':str(timeline[-1]['id']-1) if type(timeline)==list and len(timeline)>0 else None,
            'since_id':timeline[0]['id_str'] if type(timeline)==list and len(timeline)>0 else None,
            'where':'home'
        })

class Mentions(BaseHandler):
    def get(self):
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
            self.redirect('/settings')
            return 

        td = Twitdao(token)
        token_user = td.users_show_by_id(user_id = token.user_id)
        owner_user = token_user
        timeline = td.mentions(**params)
        if 'error' in timeline:
            timeline=[]
        self.render('mobile/mentions.html', {
            'token':token,
            'token_user':token_user,
            'owner_user':owner_user,
            'timeline':timeline,
            'max_id':str(timeline[-1]['id']-1) if type(timeline)==list and len(timeline)>0 else None,
            'since_id':timeline[0]['id_str'] if type(timeline)==list and len(timeline)>0 else None,
            'where':'mentions'
        })

class Favorites(BaseHandler):
    def get(self, screen_name):
        params = self.params(['page', 'include_entities'])
        page = self.param('page')

        token = md.get_default_access_token()
        if not token:
            self.redirect('/settings')
            return

        if not screen_name:
            screen_name=token.screen_name

        td = Twitdao(token)
        token_user = td.users_show_by_id(user_id = token.user_id)
        owner_user = td.users_show_by_screen_name(screen_name = screen_name)
        favorites = td.favorites(id=screen_name, **params)
        prev_page, next_page = None, 2
        if page:
            try:
                page = int(page)
                prev_page = page-1 if page-1>0 else None
                next_page = page+1
            except:
                pass

        self.render('mobile/favorites.html', {
            'token':token,
            'token_user':token_user,
            'owner_user':owner_user,
            'favorites':favorites,
            'prev_page':prev_page,
            'next_page':next_page,
            'where':'favorites',
        })

class Followers(BaseHandler):
    def get(self, screen_name):
        params = self.params([
            'user_id',
            'cursor',
            'include_entities',
            'count'
        ], cursor=-1, count=50)

        token = md.get_default_access_token()
        if not token:
            self.redirect('/settings')
            return

        if not screen_name:
            screen_name=token.screen_name

        td = Twitdao(token)
        token_user = td.users_show_by_id(user_id = token.user_id)
        owner_user = td.users_show_by_screen_name(screen_name = screen_name)
        followers = td.statuses_followers(screen_name=screen_name, **params)

        self.render('mobile/followers.html', {
            'token':token,
            'token_user':token_user,
            'owner_user':owner_user,
            'error': followers['error'] if 'error' in followers else False,
            'followers':followers if 'error' in followers else followers['users'],
            'next_cursor':None if 'error' in followers else followers['next_cursor'],
            'next_cursor_str':None if 'error' in followers else followers['next_cursor_str'],
            'previous_cursor':None if 'error' in followers else followers['previous_cursor'],
            'previous_cursor_str':None if 'error' in followers else followers['previous_cursor_str'],
            'where':'followers',
        })

class Following(BaseHandler):
    def get(self, screen_name):
        params = self.params([
            'user_id',
            'cursor',
            'include_entities',
            'count'
        ], cursor=-1, count=50)

        token = md.get_default_access_token()
        if not token:
            self.redirect('/settings')
            return

        if not screen_name:
            screen_name=token.screen_name

        td = Twitdao(token)
        token_user = td.users_show_by_id(user_id = token.user_id)
        owner_user = td.users_show_by_screen_name(screen_name = screen_name)
        following = td.statuses_friends(screen_name=screen_name, **params)

        self.render('mobile/following.html', {
            'token':token,
            'token_user':token_user,
            'owner_user':owner_user,
            'error': following['error'] if 'error' in following else False,
            'following':following if 'error' in following else following['users'],
            'next_cursor':None if 'error' in following else following['next_cursor'],
            'next_cursor_str':None if 'error' in following else following['next_cursor_str'],
            'previous_cursor':None if 'error' in following else following['previous_cursor'],
            'previous_cursor_str':None if 'error' in following else following['previous_cursor_str'],
            'where':'following',
        })

class Messages(BaseHandler):
    def get(self, mbox):
        params = self.params([
            'since_id',
            'max_id',
            'count',
            'page',
            'include_entities',
        ])

        token = md.get_default_access_token()
        if not token:
            self.redirect('/settings')
            return
        
        td = Twitdao(token)
        token_user = td.users_show_by_id(user_id = token.user_id)
        owner_user = token_user

        direct_messages = []
        if mbox=='inbox':
            direct_messages = td.direct_messages(**params)
        elif mbox=='sent':
            direct_messages = td.direct_messages_sent(**params)
        else:
            self.error(404)
            return

        self.render('mobile/messages.html', {
            'token':token,
            'token_user':token_user,
            'owner_user':owner_user,
            'max_id':str(direct_messages[-1]['id']-1) if type(direct_messages)==list and len(direct_messages)>0 else None,
            'since_id':direct_messages[0]['id_str'] if type(direct_messages)==list and len(direct_messages)>0 else None,
            'messages':direct_messages,
            'where': 'messages',
            'at': mbox,
        })

class SendMessage(BaseHandler):
    def get(self):
        screen_name = self.param('screen_name')

        token = md.get_default_access_token()
        if not token:
            self.redirect('/settings')
            return
        
        td = Twitdao(token)
        token_user = td.users_show_by_id(user_id = token.user_id)
        owner_user = token_user

        self.render('mobile/message-send.html',{
            'token':token,
            'token_user':token_user,
            'owner_user':owner_user,
            'screen_name':screen_name,
        })

    def post(self):
        screen_name = self.param('screen_name')
        user_id = self.param('user_id')
        text = self.param('text')

        params = self.params(['include_entities'])

        token = md.get_default_access_token()
        if not token:
            self.redirect('/settings')
            return

        td = Twitdao(token)
        message = td.direct_messages_new(user_id=user_id, screen_name=screen_name, text=text.encode('utf-8'), **params)

        self.redirect('/m/m-sent')

class DeleteMessage(BaseHandler):
    def get(self):
        id=self.param('id')
        token = md.get_default_access_token()
        if not token:
            self.redirect('/settings')
            return
        
        td = Twitdao(token)
        token_user = td.users_show_by_id(user_id = token.user_id)
        owner_user = token_user
        
        #No show single message api.
        message = None 

        self.render('mobile/message-del.html',{
            'token':token,
            'token_user':token_user,
            'owner_user':owner_user,
            'message':message,
            'id':id
        })

    def post(self):
        params = self.params(['include_entities'])
        id = self.param('id')
        
        token = md.get_default_access_token()
        if not token:
            self.redirect('/settings')
            return

        td = Twitdao(token)
        message = td.direct_messages_destroy(id=id, **params)
        self.redirect('/m/m-inbox')

class User(BaseHandler):
    def get(self, screen_name):
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
        if not token:
            self.redirect('/settings')
            return

        td = Twitdao(token)
        owner_user = td.users_show_by_screen_name( screen_name=screen_name )
        token_user = td.users_show_by_id(user_id = token.user_id)
        friendship = td.friendships_show(source_id=token.user_id, target_screen_name=screen_name)
        timeline = td.user_timeline(screen_name=screen_name, **params)
        self.render('mobile/user.html', {
            'token':token,
            'token_user':token_user,
            'owner_user':owner_user,
            'max_id':str(timeline[-1]['id']-1) if type(timeline)==list and len(timeline)>0 else None,
            'since_id':timeline[0]['id_str'] if type(timeline)==list and len(timeline)>0 else None,
            'timeline':timeline,
            'friendship':friendship,
            'where':'user',
        })

class ActionFollow(BaseHandler):
    def get(self, screen_name):
        token = md.get_default_access_token()
        if not token:
            self.redirect('/settings')
            return
        
        td = Twitdao(token)
        token_user = td.users_show_by_id(user_id = token.user_id)
        owner_user = token_user
        follow_user = td.users_show_by_screen_name(screen_name = screen_name)

        self.render('mobile/follow.html', {
            'token':token,
            'token_user':token_user,
            'owner_user':owner_user,
            'user':follow_user,
        })

    def post(self, screen_name):
        token = md.get_default_access_token()
        if not token:
            self.redirect('/settings')
            return

        td = Twitdao(token)
        follow_user = td.friendships_create(screen_name = screen_name)
        taskqueue.add(queue_name='cache', url='/q/update_user_cache', params={'tk':token.key(), 'user_id':token.user_id}, method="GET" )
        taskqueue.add(queue_name='cache', url='/q/update_user_cache', params={'tk':token.key(), 'screen_name':screen_name}, method="GET" )
        self.redirect('/m/u-%s' % screen_name)

class ActionUnfollow(BaseHandler):
    def get(self, screen_name):
        token = md.get_default_access_token()
        if not token:
            self.redirect('/settings')
            return
        
        td = Twitdao(token)
        token_user = td.users_show_by_id(user_id = token.user_id)
        owner_user = token_user
        follow_user = td.users_show_by_screen_name(screen_name = screen_name)

        self.render('mobile/unfollow.html', {
            'token':token,
            'token_user':token_user,
            'owner_user':owner_user,
            'user':follow_user,
        })

    def post(self, screen_name):
        token = md.get_default_access_token()
        if not token:
            self.redirect('/settings')
            return

        td = Twitdao(token)
        follow_user = td.friendships_destroy(screen_name = screen_name)
        taskqueue.add(queue_name='cache', url='/q/update_user_cache', params={'tk':token.key(), 'user_id':token.user_id}, method="GET" )
        taskqueue.add(queue_name='cache', url='/q/update_user_cache', params={'tk':token.key(), 'screen_name':screen_name}, method="GET" )
        self.redirect('/m/u-%s' % screen_name)

class ActionBlock(BaseHandler):
    def get(self, screen_name):
        token = md.get_default_access_token()
        if not token:
            self.redirect('/settings')
            return

        td = Twitdao(token)
        token_user = td.users_show_by_id(user_id = token.user_id)
        owner_user = token_user
        block_user = td.users_show_by_screen_name(screen_name = screen_name)
        self.render('mobile/block.html', {
            'token':token,
            'token_user':token_user,
            'owner_user':owner_user,
            'user':block_user,
        })

    def post(self, screen_name):
        token = md.get_default_access_token()
        if not token:
            self.redirect('/settings')
            return

        td = Twitdao(token)
        block_user = td.blocks_create(screen_name = screen_name)
        taskqueue.add(queue_name='cache', url='/q/update_user_cache', params={'tk':token.key(), 'user_id':token.user_id}, method="GET" )
        taskqueue.add(queue_name='cache', url='/q/update_user_cache', params={'tk':token.key(), 'screen_name':screen_name}, method="GET" )
        self.redirect('/m/u-%s' % screen_name)

class ActionUnblock(BaseHandler):
    def get(self, screen_name):
        token = md.get_default_access_token()
        if not token:
            self.redirect('/settings')
            return
        td = Twitdao(token)
        token_user = td.users_show_by_id(user_id = token.user_id)
        owner_user = token_user
        block_user = td.users_show_by_screen_name(screen_name = screen_name)
        self.render('mobile/unblock.html', {
            'token':token,
            'token_user':token_user,
            'owner_user':owner_user,
            'user':block_user,
        })

    def post(self, screen_name):
        token = md.get_default_access_token()
        if not token:
            self.redirect('/settings')
            return

        td = Twitdao(token)
        follow_user = td.blocks_destroy(screen_name = screen_name)
        taskqueue.add(queue_name='cache', url='/q/update_user_cache', params={'tk':token.key(), 'user_id':token.user_id}, method="GET" )
        taskqueue.add(queue_name='cache', url='/q/update_user_cache', params={'tk':token.key(), 'screen_name':screen_name}, method="GET" )
        self.redirect('/m/u-%s' % screen_name)

class ActionDelete(BaseHandler):
    def get(self, tweet_id):
        params = self.params(['trim_user','include_entities'])

        token = md.get_default_access_token()
        if not token:
            self.redirect('/settings')
            return

        id=utils.tweet_id_decode(tweet_id)

        td = Twitdao(token)
        token_user = td.users_show_by_id(user_id = token.user_id)
        owner_user = token_user
        tweet = td.statuses_show(id=id, **params)

        self.render('mobile/tweet-del.html', {
            'token':token,
            'token_user':token_user,
            'owner_user':owner_user,
            'tweet':tweet,
        })
    
    def post(self, tweet_id):
        params = self.params(['trim_user','include_entities'])

        token = md.get_default_access_token()
        if not token:
            self.redirect('/settings')
            return

        id=utils.tweet_id_decode(tweet_id)

        td = Twitdao(token)
        tweet = td.statuses_destroy(id=id, **params)
        taskqueue.add(queue_name='cache', url='/q/update_user_cache', params={'tk':token.key(), 'user_id':token.user_id}, method="GET" )
        self.redirect('/m/u-/home')

class ActionTweet(BaseHandler):
    def get(self):
        screen_name = self.param('screen_name')
        tweet_id = self.param('tweet_id')

        params = self.params(['trim_user','include_entities'])

        token = md.get_default_access_token()
        if not token:
            self.redirect('/settings')
            return

        tweet_id = utils.tweet_id_decode(tweet_id)

        if screen_name:
            td = Twitdao(token)
            token_user = td.users_show_by_id(user_id = token.user_id)
            owner_user = token_user
            self.render('mobile/reply.html', {
                'token':token,
                'token_user':token_user,
                'owner_user':owner_user,
                'screen_name':screen_name,
            })
        else:
            td = Twitdao(token)
            token_user = td.users_show_by_id(user_id = token.user_id)
            owner_user = token_user
            tweet = td.statuses_show(id=tweet_id,**params)
            self.render('mobile/reply.html', {
                'token':token,
                'token_user':token_user,
                'owner_user':owner_user,
                'tweet':tweet,
            })

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
            self.redirect('/settings')
            return
        td = Twitdao(token)
        td.statuses_update(status=status.encode('utf-8'), **params)
        taskqueue.add(queue_name='cache', url='/q/update_user_cache', params={'tk':token.key(), 'user_id':token.user_id}, method="GET" )
        self.redirect('/m/u-/home')

class ShowTweet(BaseHandler):
    def get(self, tweet_id):
        params = self.params(['trim_user','include_entities'])
        
        token = md.get_default_access_token()
        if not token:
            self.redirect('/settings')
            return
        tweet_id = utils.tweet_id_decode(tweet_id)
        td = Twitdao(token)
        token_user = td.users_show_by_id(user_id = token.user_id)
        owner_user = token_user
        tweet = td.statuses_show(id=tweet_id,**params)

        self.render('mobile/tweet-show.html', {
            'token':token,
            'token_user':token_user,
            'owner_user':owner_user,
            'tweet':tweet,
        })

class ActionQuote(BaseHandler):
    def get(self, tweet_id):
        params = self.params(['trim_user','include_entities'])
        token = md.get_default_access_token()
        if not token:
            self.redirect('/settings')
            return
        id = utils.tweet_id_decode(tweet_id)
        td = Twitdao(token)
        token_user = td.users_show_by_id(user_id = token.user_id)
        owner_user = token_user
        tweet = td.statuses_show(id=id, **params)

        self.render('mobile/quote.html', {
            'token_user':token_user,
            'owner_user':owner_user,
            'tweet':tweet,
        })

class ActionRetweet(BaseHandler):
    def get(self, tweet_id):
        params = self.params(['trim_user','include_entities'])
        token = md.get_default_access_token()
        if not token:
            self.redirect('/settings')
            return
        id = utils.tweet_id_decode(tweet_id)
        td = Twitdao(token)
        token_user = td.users_show_by_id(user_id = token.user_id)
        owner_user = token_user
        tweet = td.statuses_show(id=id, **params)

        self.render('mobile/retweet.html', {
            'token_user':token_user,
            'owner_user':owner_user,
            'tweet':tweet,
        })

    def post(self, tweet_id):
        params = self.params(['trim_user','include_entities'])
        token = md.get_default_access_token()
        if not token:
            self.redirect('/settings')
            return
        id = utils.tweet_id_decode(tweet_id)
        td = Twitdao(token)
        tweet = td.statuses_retweet(id=id, **params)
        taskqueue.add(queue_name='cache', url='/q/update_user_cache', params={'tk':token.key(), 'user_id':token.user_id}, method="GET" )

        self.redirect('/m/u-/home')

class ActionUndoRetweet(BaseHandler):
    def get(self, tweet_id):
        pass

class ActionFavorite(BaseHandler):
    def get(self, tweet_id):
        params = self.params(['trim_user','include_entities'])

        token = md.get_default_access_token()
        if not token:
            self.redirect('/settings')
            return
        id = utils.tweet_id_decode(tweet_id)
        td = Twitdao(token)
        token_user = td.users_show_by_id(user_id = token.user_id)
        owner_user = token_user
        tweet = td.statuses_show(id=id, **params)

        self.render('mobile/favorite.html', {
            'token':token,
            'token_user':token_user,
            'owner_user':owner_user,
            'tweet':tweet,
        })

    def post(self, tweet_id):
        params = self.params(['include_entities'])

        token = md.get_default_access_token()
        if not token:
            self.redirect('/settings')
            return
        id = utils.tweet_id_decode(tweet_id)
        td = Twitdao(token)
        tweet = td.favorites_create(id=id, **params)
        taskqueue.add(queue_name='cache', url='/q/update_user_cache', params={'tk':token.key(), 'user_id':token.user_id}, method="GET" )
        self.redirect('/m/u-%s/favs' % token.screen_name)

class ActionUnfavorite(BaseHandler):
    def get(self, tweet_id):
        params = self.params(['trim_user','include_entities'])

        token = md.get_default_access_token()
        if not token:
            self.redirect('/settings')
            return
        id = utils.tweet_id_decode(tweet_id)
        td = Twitdao(token)
        token_user = td.users_show_by_id(user_id = token.user_id)
        owner_user = token_user
        tweet = td.statuses_show(id=id, **params)

        self.render('mobile/unfavorite.html', {
            'token':token,
            'token_user':token_user,
            'owner_user':owner_user,
            'tweet':tweet,
        })

    def post(self, tweet_id):
        params = self.params(['include_entities'])

        token = md.get_default_access_token()
        if not token:
            self.redirect('/settings')
            return
        id = utils.tweet_id_decode(tweet_id)
        td = Twitdao(token)
        tweet = td.favorites_destroy(id=id, **params)
        taskqueue.add(queue_name='cache', url='/q/update_user_cache', params={'tk':token.key(), 'user_id':token.user_id}, method="GET" )
        self.redirect('/m/u-%s/favs' % token.screen_name)


class Settings(BaseHandler):
    def get(self, section):
        token = md.get_default_access_token()
        if not token:
            self.redirect('/settings')
            return

        cursor=self.param('cursor', default_value=None)
        tokens, cursor = md.get_user_access_tokens(users.get_current_user(), 10, cursor)
        td=Twitdao(token)
        token_user=td.users_show_by_id(user_id=token.user_id)

        self.render('mobile/settings.html', {
            'token':token,
            'tokens':tokens,
            'token_user':token_user,
            'owner_user':token_user,
            'where':'settings'
        })

    def post(self, section):
        token = md.get_default_access_token()
        if not token:
            self.redirect('/settings')
            return

        if section=='token':
            token_key = self.param('tk')
            token = md.get_access_token(token_key, users.get_current_user())
            md.set_default_access_token(token)
        elif section=='media':
            show_avatar=self.param('show_avatar')
            show_media=self.param('show_media')
            settings={}
            settings['m_show_avatar']=True if show_avatar=='t' else False
            settings['m_show_media']=True if show_media=='t' else False
            md.set_token_settings(token.key(), users.get_current_user(), **settings)
        elif section=='opti':
            opti=self.param('opti')
            settings={}
            settings['m_optimizer']=opti if opti!='none' or opti=='' else None
            md.set_token_settings(token.key(), users.get_current_user(), **settings)

        self.redirect('/m/s-')


class UploadPhoto(BaseHandler):
    def get(self):
        token = md.get_default_access_token()
        if not token:
            self.redirect('/settings')
            return
        td = Twitdao(token)
        token_user = td.users_show_by_id(user_id = token.user_id)
        owner_user = token_user
        self.render('mobile/upload.html', {
            'token':token,
            'token_user':token_user,
            'owner_user':owner_user,
        })

    def post(self):
        media = self.param('media')
        status = self.param('status')

        token = md.get_default_access_token()
        if not token:
            self.redirect('/settings')
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
                resp=twitpic.api_call('POST', 'upload', {'message':status.encode('utf-8')}, files=[('media', filename, media)])
            full_status=status+" "+resp['url']
            tweet_status = full_status
            if len(full_status)-140>0:
                tweet_status = status[:140-len(resp['url'])-4]+"... "+resp['url']
            td.statuses_update(status=tweet_status.encode('utf-8'))
            taskqueue.add(queue_name='cache', url='/q/update_user_cache', params={'tk':token.key(), 'user_id':token.user_id}, method="GET" )
        except Exception, e:
            logging.debug(e)
        except:
            raise
        self.redirect('/m/u-/home')


class UserAgentTest(BaseHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        self.write(self.request.headers['user-agent'])


def main():
    application = webapp.WSGIApplication([
        ('/m(?:|/|/u-/home)', Home),
        ('/m/u-/at', Mentions),
        ('/m/u-([0-9a-zA-Z_]*)/favs', Favorites),
        ('/m/u-([0-9a-zA-Z_]*)/foers', Followers),
        ('/m/u-([0-9a-zA-Z_]*)/foing', Following),

        ('/m/m-(inbox|sent)', Messages),
        ('/m/m-send', SendMessage),
        ('/m/m-del', DeleteMessage),

        ('/m/u-([0-9a-zA-Z_]+)', User),
        ('/m/u-([0-9a-zA-Z_]+)/fo', ActionFollow),
        ('/m/u-([0-9a-zA-Z_]+)/ufo', ActionUnfollow),
        ('/m/u-([0-9a-zA-Z_]+)/b', ActionBlock),
        ('/m/u-([0-9a-zA-Z_]+)/ub', ActionUnblock),

        ('/m/t-', ActionTweet),
        ('/m/t-([0-9a-zA-Z_\-\.]+)', ShowTweet),
        ('/m/t-([0-9a-zA-Z_\-\.]+)/qt', ActionQuote),
        ('/m/t-([0-9a-zA-Z_\-\.]+)/del', ActionDelete),
        ('/m/t-([0-9a-zA-Z_\-\.]+)/rt', ActionRetweet),
        ('/m/t-([0-9a-zA-Z_\-\.]+)/urt', ActionUndoRetweet),
        ('/m/t-([0-9a-zA-Z_\-\.]+)/fav', ActionFavorite),
        ('/m/t-([0-9a-zA-Z_\-\.]+)/ufav', ActionUnfavorite),

        ('/m/s-(token|media|opti|)', Settings),
        ('/m/p-', UploadPhoto),
        ('/m/uat-', UserAgentTest),

    ], debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()

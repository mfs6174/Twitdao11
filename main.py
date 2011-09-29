# -*- coding: utf-8 -*-
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.api import taskqueue

from base import BaseHandler
from twitdao import Twitdao

import md

import urllib


#Home
class HomeTimeline(BaseHandler):
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
        limit_rate = td.API_limit_rate()

        self.render('home-timeline.html', {
            'token':token,
            'token_user':token_user,
            'owner_user':owner_user,
            'timeline':timeline,
            'max_id':str(timeline[-1]['id']-1) if type(timeline)==list and len(timeline)>0 else None,
            'since_id':timeline[0]['id_str'] if type(timeline)==list and len(timeline)>0 else None,
            'limit_rate':limit_rate,
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

        self.render('mentions-timeline.html', {
            'token':token,
            'token_user':token_user,
            'owner_user':owner_user,
            'timeline':timeline,
            'max_id':str(timeline[-1]['id']-1) if type(timeline)==list and len(timeline)>0 else None,
            'since_id':timeline[0]['id_str'] if type(timeline)==list and len(timeline)>0 else None,
            'where':'mentions'
        })


class Retweets(BaseHandler):
    def get(self, which):
        params=self.params([
            'since_id',
            'max_id',
            'count',
            'page',
            'trim_user',
            'include_entities'
        ])
        token = md.get_default_access_token()
        if not token:
            self.redirect('/settings')
            return 

        td = Twitdao(token)
        timeline=[]
        if which == 'retweeted_by_me':
            timeline = td.retweeted_by_me(**params)
            title = "retweeted by me"
        elif which == 'retweeted_to_me':
            timeline = td.retweeted_to_me(**params)
            title = "retweeted to me"
        elif which == 'retweeted_of_me':
            timeline = td.retweets_of_me(**params)
            title = "retweeted of me"
        token_user = td.users_show_by_id(user_id = token.user_id)
        owner_user = token_user

        self.render('retweets-timeline.html', {
            'token':token,
            'token_user':token_user,
            'owner_user':owner_user,
            'timeline':timeline,
            'max_id':str(timeline[-1]['id']-1) if type(timeline)==list and len(timeline)>0 else None,
            'since_id':timeline[0]['id_str'] if type(timeline)==list and len(timeline)>0 else None,
            'where':which,
            'which':which,
            'title':title,
        })


class Retweet(BaseHandler):
    def get(self, id):
        params = self.params(['trim_user','include_entities'])
        token = md.get_default_access_token()
        if not token:
            self.redirect('/settings')
            return

        td = Twitdao(token)
        token_user = td.users_show_by_id(user_id = token.user_id)
        owner_user = token_user
        tweet = td.statuses_show(id=id, **params)

        self.render('retweet.html', {
            'token_user':token_user,
            'owner_user':owner_user,
            'tweet':tweet,
        })

    def post(self, id):
        params = self.params(['trim_user','include_entities'])
        token = md.get_default_access_token()
        if not token:
            self.redirect('/settings')
            return

        td = Twitdao(token)
        tweet = td.statuses_retweet(id=id, **params)
        taskqueue.add(queue_name='cache', url='/q/update_user_cache', params={'tk':token.key(), 'user_id':token.user_id}, method="GET" )

        self.redirect('/t')


class UserTimeline(BaseHandler):
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

        self.render('user-timeline.html', {
            'token':token,
            'token_user':token_user,
            'owner_user':owner_user,
            'max_id':str(timeline[-1]['id']-1) if type(timeline)==list and len(timeline)>0 else None,
            'since_id':timeline[0]['id_str'] if type(timeline)==list and len(timeline)>0 else None,
            'timeline':timeline,
            'friendship':friendship,
            'where':'user',
        })


class UpdateStatus(BaseHandler):

    def get(self):

        screen_name = self.param('screen_name')
        status_id = self.param('status_id')

        params = self.params(['trim_user','include_entities'])
        
        token = md.get_default_access_token()
        if not token:
            self.redirect('/settings')
            return

        if screen_name:
            td = Twitdao(token)
            token_user = td.users_show_by_id(user_id = token.user_id)
            owner_user = token_user

            self.render('reply.html', {
                'token':token,
                'token_user':token_user,
                'owner_user':owner_user,
                'screen_name':screen_name,
            })
        else:
            td = Twitdao(token)
            token_user = td.users_show_by_id(user_id = token.user_id)
            owner_user = token_user
            tweet = td.statuses_show(id=status_id,**params)
                        
            self.render('reply.html', {
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
        self.redirect('/t')


class ShowStatus(BaseHandler):
    def get(self, status_id):

        params = self.params(['trim_user','include_entities'])
        
        token = md.get_default_access_token()
        if not token:
            self.redirect('/settings')
            return
        td = Twitdao(token)
        token_user = td.users_show_by_id(user_id = token.user_id)
        owner_user = token_user
        tweet = td.statuses_show(id=status_id,**params)

        self.render('tweet-show.html', {
            'token':token,
            'token_user':token_user,
            'owner_user':owner_user,
            'tweet':tweet,
        })


class DeleteStatus(BaseHandler):
    def get(self, id):

        params = self.params(['trim_user','include_entities'])

        token = md.get_default_access_token()
        if not token:
            self.redirect('/settings')
            return

        td = Twitdao(token)
        token_user = td.users_show_by_id(user_id = token.user_id)
        owner_user = token_user
        tweet = td.statuses_show(id=id, **params)

        self.render('tweet-delete.html', {
            'token':token,
            'token_user':token_user,
            'owner_user':owner_user,
            'tweet':tweet,
        })
    
    def post(self, id):
        
        params = self.params(['trim_user','include_entities'])

        token = md.get_default_access_token()
        if not token:
            self.redirect('/settings')
            return
        
        td = Twitdao(token)
        tweet = td.statuses_destroy(id=id, **params)
        taskqueue.add(queue_name='cache', url='/q/update_user_cache', params={'tk':token.key(), 'user_id':token.user_id}, method="GET" )

        self.redirect('/t')


class Followers(BaseHandler):
    def get(self, screen_name):
        
        params = self.params([
            'user_id',
            'cursor',
            'include_entities',
        ], cursor=-1)

        token = md.get_default_access_token()
        if not token:
            self.redirect('/settings')
            return
        
        td = Twitdao(token)
        token_user = td.users_show_by_id(user_id = token.user_id)
        owner_user = td.users_show_by_screen_name(screen_name = screen_name)
        followers = td.statuses_followers(screen_name=screen_name, **params)

        self.render('followers.html', {
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
        ], cursor=-1)

        token = md.get_default_access_token()
        if not token:
            self.redirect('/settings')
            return
        
        td = Twitdao(token)
        token_user = td.users_show_by_id(user_id = token.user_id)
        owner_user = td.users_show_by_screen_name(screen_name = screen_name)
        following = td.statuses_friends(screen_name=screen_name, **params)
        
        self.render('following.html', {
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


class Follow(BaseHandler):
    def get(self, screen_name):
        
        token = md.get_default_access_token()
        if not token:
            self.redirect('/settings')
            return
        
        td = Twitdao(token)
        token_user = td.users_show_by_id(user_id = token.user_id)
        owner_user = token_user
        follow_user = td.users_show_by_screen_name(screen_name = screen_name)

        self.render('follow.html', {
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
        self.redirect('/t/%s?force_refresh=true' % screen_name)



class UnFollow(BaseHandler):
    def get(self, screen_name):
        
        token = md.get_default_access_token()
        if not token:
            self.redirect('/settings')
            return
        
        td = Twitdao(token)
        token_user = td.users_show_by_id(user_id = token.user_id)
        owner_user = token_user
        follow_user = td.users_show_by_screen_name(screen_name = screen_name)

        self.render('unfollow.html', {
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
        self.redirect('/t/%s?force_refresh=true' % screen_name)



class Block(BaseHandler):
    def get(self, screen_name):
        
        token = md.get_default_access_token()
        if not token:
            self.redirect('/settings')
            return

        td = Twitdao(token)
        token_user = td.users_show_by_id(user_id = token.user_id)
        owner_user = token_user
        block_user = td.users_show_by_screen_name(screen_name = screen_name)

        self.render('block.html', {
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
        self.redirect('/t/%s?force_refresh=true' % screen_name)


class UnBlock(BaseHandler):
    def get(self, screen_name):
        
        token = md.get_default_access_token()
        if not token:
            self.redirect('/settings')
            return
        
        td = Twitdao(token)
        token_user = td.users_show_by_id(user_id = token.user_id)
        owner_user = token_user
        block_user = td.users_show_by_screen_name(screen_name = screen_name)

        self.render('unblock.html', {
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
        self.redirect('/t/%s?force_refresh=true' % screen_name)


#Favorite
class Favorites(BaseHandler):
    def get(self, screen_name):

        params = self.params(['page', 'include_entities'])
        page = self.param('page')
        
        token = md.get_default_access_token()
        if not token:
            self.redirect('/settings')
            return
        
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

        self.render('favorites.html', {
            'token':token,
            'token_user':token_user,
            'owner_user':owner_user,
            'favorites':favorites,
            'prev_page':prev_page,
            'next_page':next_page,
            'where':'favorites',
        })


class FavoritesDestroy(BaseHandler):
    def get(self, id):

        params = self.params(['trim_user','include_entities'])

        token = md.get_default_access_token()
        if not token:
            self.redirect('/settings')
            return
        
        td = Twitdao(token)
        token_user = td.users_show_by_id(user_id = token.user_id)
        owner_user = token_user
        tweet = td.statuses_show(id=id, **params)

        self.render('unfavorite.html', {
            'token':token,
            'token_user':token_user,
            'owner_user':owner_user,
            'tweet':tweet,
        })

    def post(self, id):

        params = self.params(['include_entities'])

        token = md.get_default_access_token()
        if not token:
            self.redirect('/settings')
            return
        
        td = Twitdao(token)
        tweet = td.favorites_destroy(id=id, **params)
        taskqueue.add(queue_name='cache', url='/q/update_user_cache', params={'tk':token.key(), 'user_id':token.user_id}, method="GET" )
        self.redirect('/t/%s/favorites' % token.screen_name)


class FavoritesCreate(BaseHandler):

    def get(self, id):

        params = self.params(['trim_user','include_entities'])

        token = md.get_default_access_token()
        if not token:
            self.redirect('/settings')
            return
        
        td = Twitdao(token)
        token_user = td.users_show_by_id(user_id = token.user_id)
        owner_user = token_user
        tweet = td.statuses_show(id=id, **params)

        self.render('favorite.html', {
            'token':token,
            'token_user':token_user,
            'owner_user':owner_user,
            'tweet':tweet,
        })

    def post(self, id):

        params = self.params(['include_entities'])

        token = md.get_default_access_token()
        if not token:
            self.redirect('/settings')
            return
        
        td = Twitdao(token)
        tweet = td.favorites_create(id=id, **params)
        taskqueue.add(queue_name='cache', url='/q/update_user_cache', params={'tk':token.key(), 'user_id':token.user_id}, method="GET" )
        self.redirect('/t/%s/favorites' % token.screen_name)


#direct message
class DirectMessages(BaseHandler):
    def get(self):

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
        direct_messages = td.direct_messages(**params)

        self.render('messages.html', {
            'token':token,
            'token_user':token_user,
            'owner_user':owner_user,
            'max_id':str(direct_messages[-1]['id']-1) if type(direct_messages)==list and len(direct_messages)>0 else None,
            'since_id':direct_messages[0]['id_str'] if type(direct_messages)==list and len(direct_messages)>0 else None,
            'messages':direct_messages,
            'where':'inbox',
        })


class DirectMessagesSent(BaseHandler):
    def get(self):
        
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
        direct_messages = td.direct_messages_sent(**params)
        self.render('messages-sent.html', {
            'token':token,
            'token_user':token_user,
            'owner_user':owner_user,
            'max_id':str(direct_messages[-1]['id']-1) if type(direct_messages)==list and len(direct_messages)>0 else None,
            'since_id':direct_messages[0]['id_str'] if type(direct_messages)==list and len(direct_messages)>0 else None,
            'messages':direct_messages,
            'where':'sent',
        })


class DirectMessagesNew(BaseHandler):
    def get(self):

        screen_name = self.param('screen_name')

        token = md.get_default_access_token()
        if not token:
            self.redirect('/settings')
            return
        
        td = Twitdao(token)
        token_user = td.users_show_by_id(user_id = token.user_id)
        owner_user = token_user

        self.render('message-new.html',{
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

        self.redirect('/a/messages_sent')


class DirectMessagesDestroy(BaseHandler):
    def get(self, id):

        token = md.get_default_access_token()
        if not token:
            self.redirect('/settings')
            return
        
        td = Twitdao(token)
        token_user = td.users_show_by_id(user_id = token.user_id)
        owner_user = token_user
        
        #No show single message api.
        message = None 

        self.render('message-destroy.html',{
            'token':token,
            'token_user':token_user,
            'owner_user':owner_user,
            'message':message,
        })

    def post(self, id):
        params = self.params(['include_entities'])
        
        token = md.get_default_access_token()
        if not token:
            self.redirect('/settings')
            return
        
        td = Twitdao(token)
        message = td.direct_messages_destroy(id=id, **params)
        self.redirect('/a/messages_sent')


class Lists(BaseHandler):
    def get(self, screen_name):

        params = self.params(['cursor'],cursor=-1)

        token = md.get_default_access_token()
        if not token:
            self.redirect('/settings')
            return

        td = Twitdao(token)
        token_user = td.users_show_by_id(user_id = token.user_id)
        owner_user = td.users_show_by_screen_name(screen_name = screen_name)
        lists = td.user_lists_get(screen_name = screen_name, **params)

        self.render('lists.html', {
            'token':token,
            'token_user':token_user,
            'owner_user':owner_user,
            'lists':lists['lists'], 
            'next_cursor':lists['next_cursor'],
            'next_cursor_str':lists['next_cursor_str'],
            'previous_cursor':lists['previous_cursor'],
            'previous_cursor_str':lists['previous_cursor_str'],
            'where':'lists',
        })


class ListsMemberships(BaseHandler):
    def get(self, screen_name):

        params = self.params(['cursor'],cursor=-1)

        token = md.get_default_access_token()
        if not token:
            self.redirect('/settings')
            return
        
        td = Twitdao(token)
        token_user = td.users_show_by_id(user_id = token.user_id)
        owner_user = td.users_show_by_screen_name(screen_name = screen_name)
        lists = td.user_list_memberships(screen_name = screen_name, **params)

        self.render('lists-memberships.html', {
            'token':token,
            'token_user':token_user,
            'owner_user':owner_user,
            'lists':lists['lists'], 
            'next_cursor':lists['next_cursor'],
            'next_cursor_str':lists['next_cursor_str'],
            'previous_cursor':lists['previous_cursor'],
            'previous_cursor_str':lists['previous_cursor_str'],
            'where':'list-memberships',
        })


class ListsSubscriptions(BaseHandler):
    def get(self, screen_name):

        params = self.params(['cursor'],cursor=-1)

        token = md.get_default_access_token()
        if not token:
            self.redirect('/settings')
            return

        td = Twitdao(token)
        token_user = td.users_show_by_id(user_id = token.user_id)
        owner_user = td.users_show_by_screen_name(screen_name = screen_name)
        lists = td.user_list_subscriptions(screen_name = screen_name, **params)

        self.render('lists-subscriptions.html', {
            'token':token,
            'token_user':token_user,
            'owner_user':owner_user,
            'lists':lists['lists'], 
            'next_cursor':lists['next_cursor'],
            'next_cursor_str':lists['next_cursor_str'],
            'previous_cursor':lists['previous_cursor'],
            'previous_cursor_str':lists['previous_cursor_str'],
            'where':'list-subscriptions',
        })


class ListTimeline(BaseHandler):
    def get(self, screen_name, slug ):
        params = self.params(['since_id','max_id','per_page','page','include_entities'])

        token = md.get_default_access_token()
        if not token:
            self.redirect('/settings')
            return

        td = Twitdao(token)
        token_user = td.users_show_by_id(user_id = token.user_id)
        owner_user = td.users_show_by_screen_name(screen_name = screen_name)
        ls = td.user_list_id_get(id=slug, screen_name=screen_name)
        timeline = td.user_list_id_statuses(id=slug, screen_name = screen_name, **params)

        self.render('list-timeline.html', {
            'token':token,
            'token_user':token_user,
            'owner_user':owner_user,
            'list':ls,
            'timeline':timeline,
            'max_id':str(timeline[-1]['id']-1) if type(timeline)==list and len(timeline)>0 else None,
            'since_id':timeline[0]['id_str'] if type(timeline)==list and len(timeline)>0 else None,
            'where':'list-timeline'
        })


class ListCreate(BaseHandler):
    def get(self):

        token = md.get_default_access_token()
        if not token:
            self.redirect('/settings')
            return
        
        td = Twitdao(token)
        token_user = td.users_show_by_id(user_id = token.user_id)
        owner_user = token_user

        self.render('list-create.html',{
            'token_user':token_user,
            'owner_user':owner_user,
        })

    def post(self):
        name = self.param('name')
        params = self.params(['mode','description'], mode='public')

        name=name.encode('utf-8')
        if 'description' in params:
            params['description']=params['description'].encode('utf-8')

        token = md.get_default_access_token()
        if not token:
            self.redirect('/settings')
            return

        td = Twitdao(token)
        token_user = td.users_show_by_id(user_id = token.user_id)
        lst = td.user_lists_post(name=name, **params)
        self.redirect('/t/%s/%s' % (token_user['screen_name'], urllib.quote(lst['slug'].encode('utf-8'))))


class ListEdit(BaseHandler):
    def get(self, lid):

        token = md.get_default_access_token()
        if not token:
            self.redirect('/settings')
            return

        td = Twitdao(token)
        token_user = td.users_show_by_id(user_id = token.user_id)
        owner_user = token_user
        lst = td.user_list_id_get(id=lid)

        self.render('list-edit.html',{
            'token_user':token_user,
            'owner_user':owner_user,
            'list':lst,
        })
    
    def post(self, lid):

        params = self.params(['name','mode','description'])

        if 'name' in params:
            params['name']=params['name'].encode('utf-8')
        if 'description' in params:
            params['description']=params['description'].encode('utf-8')

        token = md.get_default_access_token()
        if not token:
            self.redirect('/settings')
            return
        
        td = Twitdao(token)
        token_user = td.users_show_by_id(user_id = token.user_id)
        lst = td.user_lists_id_post(id=lid, **params)
        self.jedirect('/t/%s/%s' % (token_user['screen_name'], urllib.quote(lst['slug'].encode('utf-8'))), time=2000)


class ListDelete(BaseHandler):
    def get(self, lid):

        token = md.get_default_access_token()
        if not token:
            self.redirect('/settings')
            return
        
        td = Twitdao(token)
        token_user = td.users_show_by_id(user_id = token.user_id)
        owner_user = token_user
        lst = td.user_list_id_get(id=lid)

        self.render('list-delete.html',{
            'token_user':token_user,
            'owner_user':owner_user,
            'list':lst,
        })
    
    def post(self, lid):

        token = md.get_default_access_token()
        if not token:
            self.redirect('/settings')
            return
        
        td = Twitdao(token)
        lst = td.user_list_id_delete(id=lid)
        self.redirect('/t/%s/lists' % token.screen_name)


class ListFollow(BaseHandler):
    def get(self, screen_name, slug ):

        token = md.get_default_access_token()
        if not token:
            self.redirect('/settings')
            return

        td = Twitdao(token)
        token_user = td.users_show_by_id(user_id = token.user_id)
        owner_user = token_user
        lst = td.user_list_id_get(id=slug, screen_name=screen_name )

        self.render('list-follow.html',{
            'token_user':token_user,
            'owner_user':owner_user,
            'list':lst,
        })

    def post(self, screen_name, slug ):

        token = md.get_default_access_token()
        if not token:
            self.redirect('/settings')
            return

        td = Twitdao(token)
        td.user_list_id_subscribers_post(screen_name=screen_name, list_id=slug)
        self.redirect('/t/%s/%s' % (screen_name, slug) )


class ListUnFollow(BaseHandler):
    def get(self, screen_name, slug ):

        token = md.get_default_access_token()
        if not token:
            self.redirect('/settings')
            return

        td = Twitdao(token)
        token_user = td.users_show_by_id(user_id = token.user_id)
        owner_user = token_user
        lst = td.user_list_id_get(id=slug, screen_name=screen_name )

        self.render('list-unfollow.html',{
            'token_user':token_user,
            'owner_user':owner_user,
            'list':lst,
        })

    def post(self, screen_name, slug ):

        token = md.get_default_access_token()
        if not token:
            self.redirect('/settings')
            return

        td = Twitdao(token)
        td.user_list_id_subscribers_delete(screen_name=screen_name, list_id=slug)
        self.redirect('/t/%s/%s' % (screen_name, slug) )


class ListAdd(BaseHandler):
    def get(self, screen_name):

        params = self.params(['cursor'],cursor=-1)

        token = md.get_default_access_token()
        if not token:
            self.redirect('/settings')
            return

        td = Twitdao(token)
        token_user = td.users_show_by_id(user_id = token.user_id)
        owner_user = td.users_show_by_screen_name(screen_name = screen_name)
        add_user = owner_user
        lists = td.user_lists_get(**params)

        self.render('lists-add-to.html', {
            'token':token,
            'token_user':token_user,
            'owner_user':owner_user,
            'add_user':add_user,
            'lists':lists['lists'],
            'where':'lists',
        })

    def post(self, screen_name):

        list_ids=self.request.get_all('list_ids')

        token = md.get_default_access_token()
        if not token:
            self.redirect('/settings')
            return

        td = Twitdao(token)
        for list_id in list_ids:
            taskqueue.add(url="/q/list_add_user", params={'tk':token.key(), 'list_id':list_id, 'screen_name':screen_name}, method='GET')
            #td.user_list_id_members_post(token.screen_name, list_id, id=screen_name)

        self.redirect('/t/%s/lists' % token.screen_name)


class ListRemove(BaseHandler):
    def get(self, slug, screen_name):

        token = md.get_default_access_token()
        if not token:
            self.redirect('/settings')
            return

        td = Twitdao(token)
        token_user = td.users_show_by_id(user_id = token.user_id)
        owner_user = token_user
        remove_user = td.users_show_by_screen_name(screen_name = screen_name)
        lst = td.user_list_id_get(id=slug, screen_name=token.screen_name )

        self.render('list-remove-from.html', {
            'token':token,
            'token_user':token_user,
            'owner_user':owner_user,
            'remove_user':remove_user,
            'list':lst,
            'where':'lists',
        })

    def post(self, slug, screen_name):

        token = md.get_default_access_token()
        if not token:
            self.redirect('/settings')
            return

        td = Twitdao(token)
        td.user_list_id_members_delete(screen_name=token.screen_name, list_id=slug, id=screen_name)
        self.redirect('/t/%s/%s/following' % (token.screen_name, slug) )


class ListFollowing(BaseHandler):
    def get(self, screen_name, slug):

        params = self.params(['cursor', 'include_entities'], cursor=-1)

        token = md.get_default_access_token()
        if not token:
            self.redirect('/settings')
            return

        td = Twitdao(token)
        token_user = td.users_show_by_id(user_id = token.user_id)
        owner_user = td.users_show_by_screen_name(screen_name = screen_name)
        lst = td.user_list_id_get(id=slug, screen_name=screen_name )
        following = td.user_list_id_members_get(screen_name, slug, **params)
        self.render('list-following.html', {
            'token':token,
            'token_user':token_user,
            'owner_user':owner_user,
            'error': following['error'] if 'error' in following else False,
            'following':following if 'error' in following else following['users'],
            'next_cursor':None if 'error' in following else following['next_cursor'],
            'next_cursor_str':None if 'error' in following else following['next_cursor_str'],
            'previous_cursor':None if 'error' in following else following['previous_cursor'],
            'previous_cursor_str':None if 'error' in following else following['previous_cursor_str'],
            'list':lst,
            'where':'list-following',
        })


class ListFollowers(BaseHandler):
    def get(self, screen_name, slug):

        params = self.params(['cursor', 'include_entities'], cursor=-1)

        token = md.get_default_access_token()
        if not token:
            self.redirect('/settings')
            return

        td = Twitdao(token)
        token_user = td.users_show_by_id(user_id = token.user_id)
        owner_user = td.users_show_by_screen_name(screen_name = screen_name)
        lst = td.user_list_id_get(id=slug, screen_name=screen_name )
        followers = td.user_list_id_subscribers_get(screen_name, slug, **params)
        self.render('list-followers.html', {
            'token':token,
            'token_user':token_user,
            'owner_user':owner_user,
            'error': followers['error'] if 'error' in followers else False,
            'followers':followers if 'error' in followers else followers['users'],
            'next_cursor':None if 'error' in followers else followers['next_cursor'],
            'next_cursor_str':None if 'error' in followers else followers['next_cursor_str'],
            'previous_cursor':None if 'error' in followers else followers['previous_cursor'],
            'previous_cursor_str':None if 'error' in followers else followers['previous_cursor_str'],
            'list':lst,
            'where':'list-followers',
        })


class Blocking(BaseHandler):

    def get(self):
        token = md.get_default_access_token()
        if not token:
            self.redirect('/settings')
            return

        params = self.params(['page', 'include_entities'])
        page = self.param('page')

        td = Twitdao(token)
        token_user = td.users_show_by_id(user_id = token.user_id)
        owner_user = token_user
        blocking = td.blocks_blocking(**params)

        prev_page, next_page = None, 2
        if page:
            try:
                page = int(page)
                prev_page = page-1 if page-1>0 else None
                next_page = page+1
            except:
                pass

        self.render('blocking.html',{
            'token_user':token_user,
            'owner_user':owner_user,
            'blocking':blocking,
            'prev_page':prev_page,
            'next_page':next_page,
        })


class ReportSpam(BaseHandler):
    def get(self, screen_name):
        
        token = md.get_default_access_token()
        if not token:
            self.redirect('/settings')
            return

        td = Twitdao(token)
        token_user = td.users_show_by_id(user_id = token.user_id)
        owner_user = td.users_show_by_screen_name(screen_name = screen_name)

        self.render('report-spam.html', {
            'token':token,
            'token_user':token_user,
            'owner_user':owner_user,
            'title':'Report %s for spam?' % screen_name,
            'confirm':'Report',
            'where':'reportspam',
        })

    def post(self, screen_name):
        #user_id, screen_name, include_entities
        token = md.get_default_access_token()
        if not token:
            self.redirect('/settings')
            return

        td = Twitdao(token)
        td.report_spam(screen_name = screen_name)
        taskqueue.add(queue_name='cache', url='/q/update_user_cache', params={'tk':token.key(), 'user_id':token.user_id}, method="GET" )
        taskqueue.add(queue_name='cache', url='/q/update_user_cache', params={'tk':token.key(), 'screen_name':screen_name}, method="GET" )
        self.redirect('/t/%s?force_refresh=true' % screen_name)


class SavedSearches(BaseHandler):
    def get(self):
        token = md.get_default_access_token()
        if not token:
            self.redirect('/settings')
            return

        td = Twitdao(token)
        token_user = td.users_show_by_id(user_id = token.user_id)
        owner_user = token_user
        searches = td.saved_searches()

        self.render('saved_searches.html',{
            'token':token,
            'token_user':token_user,
            'owner_user':owner_user,
            'searches':searches,
        })


class Search(BaseHandler):
    def get(self):

        q = self.param('q')

        params = self.params([
            'lang',
            'locate',
            'rpp',
            'page',
            'since_id',
            'until',
            'geocode',
            'show_user',
            'result_type',
        ])

        token = md.get_default_access_token()
        if not token:
            self.redirect('/settings')
            return

        td = Twitdao(token)
        token_user = td.users_show_by_id(user_id = token.user_id)
        owner_user = token_user
        limit_rate = td.API_limit_rate()

        searchd = None
        if q:
            q = q.encode('utf-8')
            searchd = td.search(q, **params)
        self.render('search.html', {
            'token':token,
            'token_user':token_user,
            'owner_user':owner_user,
            'q':q,
			'limit_rate':limit_rate,
            'search_data':searchd
        })


class HackedSearch(BaseHandler):
    def get(self):
        q = self.param('q')
        page = self.param('page')

        token = md.get_default_access_token()
        if not token:
            self.redirect('/settings')
            return

        td = Twitdao(token)
        token_user = td.users_show_by_id(user_id = token.user_id)
        owner_user = token_user

        searchd = None
        timeline=[]
        if q:
            searchd=td.hacked_search(q.encode('utf-8'), page=page)
            timeline=searchd['statuses']
        self.render('hacked_search.html', {
            'token':token,
            'token_user':token_user,
            'owner_user':owner_user,
            'q':q,
            'since_id':timeline[0]['id_str'] if type(timeline)==list and len(timeline)>0 else None,
            'search_data':searchd
        })


def main():
    application = webapp.WSGIApplication([
        ('/t/?', HomeTimeline),
        ('/t/mentions', Mentions),
        ('/t/retweets/(retweeted_by_me)', Retweets),
        ('/t/retweets/(retweeted_to_me)', Retweets),
        ('/t/retweets/(retweeted_of_me)', Retweets),
        ('/a/retweet/([0-9]+)', Retweet),
        ('/t/statuses/update', UpdateStatus),
        ('/a/statuses/reply', UpdateStatus),
        ('/a/statuses/mention', UpdateStatus),
        ('/a/statuses/delete/([0-9]+)', DeleteStatus),
        ('/a/statuses/([0-9]+)', ShowStatus),
        ('/t/([0-9a-zA-Z_]+)/followers', Followers),
        ('/t/([0-9a-zA-Z_]+)/following', Following),
        ('/t/([0-9a-zA-Z_]+)/favorites', Favorites),
        ('/t/[0-9a-zA-Z_]+/favorites/create/([0-9]+)', FavoritesCreate),
        ('/t/[0-9a-zA-Z_]+/favorites/destroy/([0-9]+)', FavoritesDestroy),

        ('/t/([0-9a-zA-Z_]+)/lists', Lists),
        ('/t/([0-9a-zA-Z_]+)/lists/memberships', ListsMemberships),
        ('/t/([0-9a-zA-Z_]+)/lists/subscriptions', ListsSubscriptions),
        ('/t/([0-9a-zA-Z_]+)/([0-9a-zA-Z\-%]+)/?', ListTimeline),

        ('/t/([0-9a-zA-Z_]+)/([0-9a-zA-Z\-%]+)/following', ListFollowing),
        ('/t/([0-9a-zA-Z_]+)/([0-9a-zA-Z\-%]+)/followers', ListFollowers),

        ('/a/list_create', ListCreate),
        ('/a/list_edit/([0-9a-zA-Z\-%]+)', ListEdit),
        ('/a/list_delete/([0-9a-zA-Z\-%]+)', ListDelete),
        ('/a/list_follow/([0-9a-zA-Z_]+)/([0-9a-zA-Z\-%]+)', ListFollow),
        ('/a/list_unfollow/([0-9a-zA-Z_]+)/([0-9a-zA-Z\-%]+)', ListUnFollow),

        ('/a/list_add/([0-9a-zA-Z_]+)', ListAdd),
        ('/a/list_remove/([0-9a-zA-Z\-%]+)/([0-9a-zA-Z_]+)', ListRemove),

        ('/t/([0-9a-zA-Z_]+)', UserTimeline),

        ('/a/messages', DirectMessages),
        ('/a/messages_sent', DirectMessagesSent),
        ('/a/messages_new', DirectMessagesNew),
        ('/a/messages_destroy/([0-9]+)', DirectMessagesDestroy),

        ('/a/follow/([0-9a-zA-Z_]+)', Follow),
        ('/a/unfollow/([0-9a-zA-Z_]+)', UnFollow),

        ('/a/block/([0-9a-zA-Z_]+)', Block),
        ('/a/unblock/([0-9a-zA-Z_]+)', UnBlock),
        ('/a/blocking', Blocking),

        ('/a/report_spam/([0-9a-zA-Z_]+)', ReportSpam),

        #('/a/search', Search),
        ('/a/saved_searches', SavedSearches),

        ('/a/search', HackedSearch),

    ], debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()

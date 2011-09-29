# -*- coding: utf-8 -*-
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.api import taskqueue

from base import BaseHandler
from twitdao import Twitdao

import md

import urllib

class ShowUserTimeline(BaseHandler):
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
        #if screen_name== '':
        #    self.redirect('/')
        #    return
        token = md.get_proxy_access_token()
        #if not token:
        #    self.redirect('/')
        #    return

        td = Twitdao(token)
        owner_user = td.users_show_by_screen_name( screen_name=screen_name )
        token_user = td.users_show_by_id(user_id = token.user_id)
        friendship = td.friendships_show(source_id=token.user_id, target_screen_name=screen_name)
        timeline = td.user_timeline(screen_name=screen_name, **params)


        self.render('user-timeline-proxy.html', {
            'token':token,
            #'token_user':'twittertwitter',#  token_user
            'owner_user':owner_user,
            'max_id':str(timeline[-1]['id']-1) if type(timeline)==list and len(timeline)>0 else None,
            'since_id':timeline[0]['id_str'] if type(timeline)==list and len(timeline)>0 else None,
            'timeline':timeline,
            #'friendship':friendship,
            'where':'user',
        })


def main():
    application = webapp.WSGIApplication([
        ('/user/([0-9a-zA-Z_]+)', ShowUserTimeline),
    ], debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()

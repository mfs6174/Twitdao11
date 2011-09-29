# -*- coding: utf-8 -*-
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.api import memcache
from google.appengine.api import users

from base import BaseHandler
from twitdao import Twitdao

import md

import random
import os


def _generate_id(length=64):
    '''Generate a cookie id. '''
    s = '1234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_'
    a = []
    for i in range(length):
        a.append(random.choice(s))
    return ''.join(a)


class Auth(BaseHandler):
    def get(self):
        url = self.param('url')
        if not url:
            url='%s://%s/settings' % (self.request.scheme, os.environ['HTTP_HOST'])
        callback='%s://%s/settings/callback?url=%s' % (self.request.scheme, os.environ['HTTP_HOST'], url)

        td=Twitdao()
        request_token = td.fetch_request_token(callback=callback)
        if not request_token and users.is_current_user_admin():
            self.redirect('/config')
            return
        elif not request_token:
            self.redirect('/settings')
            return

        cookie_id = _generate_id()
        memcache.set(cookie_id, request_token)
        self.set_cookie('cid', cookie_id)
        self.redirect(td.get_authorize_url(request_token, force_login=True))


class AuthCallback(BaseHandler):
    def get(self):
        denied = self.param('denied', default_value=None)

        if denied:
            self.render('denied.html')
            return

        oauth_verifier = self.param('oauth_verifier')
        cookie_id = self.get_cookie('cid','')
        request_token = memcache.get(cookie_id)

        if not request_token or 'oauth_token' not in request_token:
            self.delete_cookie('cid')
            self.error(404)
            return

        td = Twitdao(md.AccessToken(
            oauth_token=request_token['oauth_token'],
            oauth_token_secret=request_token['oauth_token_secret']
        ))

        access_token = td.fetch_access_token(oauth_verifier)

        md.save_access_token(
            user_id=access_token['user_id'],
            screen_name=access_token['screen_name'],
            oauth_token=access_token['oauth_token'],
            oauth_token_secret=access_token['oauth_token_secret'],
            app_user = users.get_current_user()
        )

        self.delete_cookie('cid')
        self.redirect(self.param('url'))


class Settings(BaseHandler):
    def get(self):
        cursor=self.param('cursor', default_value=None)
        default_token = md.get_default_access_token()
        tokens, cursor = md.get_user_access_tokens(users.get_current_user(), 10, cursor)

        self.render('settings.html', {
            'default_token':default_token,
            'tokens':tokens,
            'cursor':cursor,
            'where':'settings'
        })


class SetDefaultToken(BaseHandler):
    def post(self):
        token_key = self.param('token_key')
        token = md.get_access_token(token_key, users.get_current_user())
        md.set_default_access_token(token)
        self.redirect('/settings')


class DeleteToken(BaseHandler):
    def post(self):
        token_key = self.param('token_key')
        t = md.delete_access_token(token_key, users.get_current_user())
        self.redirect('/settings')


class SettingsProfile(BaseHandler):
    def get(self):
        tk=self.param('tk')
        if not tk:
            self.error(404)
            return

        token = md.get_access_token(tk, users.get_current_user())
        if not token:
            self.redirect('/settings')
            return

        td=Twitdao(token)
        token_user=td.users_show_by_id(user_id=token.user_id, _twitdao_force_refresh=True)

        self.render('settings-profile.html', {
            'token_key':tk,
            'token':token,
            'token_user':token_user,
            'owner_user':token_user,
            'where':'settings-profile'
        })

    def post(self):
        tk=self.param('tk')
        if not tk:
            self.error(404)
            return


        token = md.get_access_token(tk, users.get_current_user())
        if not token:
            self.redirect('/settings')
            return

        td=Twitdao(token)
        
        image=self.param('picture')
        if image:
            filename=self.request.POST[u'picture'].filename.encode('utf-8')
            td.account_update_profile_image(('image', filename, image))

        params=self.params(['name', 'url', 'location', 'description', 'include_entities'])
        for k in params:
            params[k]=params[k].encode('utf-8')
        td.account_update_profile(**params)

        self.redirect('/settings/profile?tk=%s' % tk)


class SettingsDesign(BaseHandler):
    def get(self):
        tk=self.param('tk')
        if not tk:
            self.error(404)
            return

        token = md.get_access_token(tk, users.get_current_user())
        if not token:
            self.redirect('/settings')
            return

        td=Twitdao(token)
        token_user=td.users_show_by_id(user_id=token.user_id, _twitdao_force_refresh=True)

        self.render('settings-design.html', {
            'token_key':tk,
            'token':token,
            'token_user':token_user,
            'owner_user':token_user,
            'where':'settings-design'
        })

    def post(self):
        tk=self.param('tk')
        if not tk:
            self.error(404)
            return

        ds_type=self.param('ds_type')

        token = md.get_access_token(tk, users.get_current_user())
        if not token:
            self.redirect('/settings')
            return

        td=Twitdao(token)
        if ds_type == 'colors':
            params=self.params([
                'profile_background_color',
                'profile_text_color',
                'profile_link_color',
                'profile_sidebar_fill_color',
                'profile_sidebar_border_color',
                'include_entities',
            ])
            td.account_update_profile_colors(**params)
        elif ds_type == 'background':
            image=self.param('image')
            if image:
                params=self.params(['tile','include_entities'])
                for k in params:
                    params[k]=params[k].encode('utf-8')
                filename=self.request.POST[u'image'].filename.encode('utf-8')
                td.account_update_profile_background_image(('image', filename, image), **params)

        self.redirect('/settings/design?tk=%s' % tk)


class SettingsTwitdao(BaseHandler):
    def get(self):
        tk=self.param('tk')
        if not tk:
            self.error(404)
            return

        token = md.get_access_token(tk, users.get_current_user())
        if not token:
            self.redirect('/settings')
            return

        td=Twitdao(token)
        token_user=td.users_show_by_id(user_id=token.user_id)

        self.render('settings-twitdao.html', {
            'token_key':tk,
            'token':token,
            'token_user':token_user,
            'owner_user':token_user,
            'where':'settings-twitdao'
        })

    def post(self):
        tk=self.param('tk')
        if not tk:
            self.error(404)
            return

        ds_type=self.param('ds_type')

        token = md.get_access_token(tk, users.get_current_user())
        if not token:
            self.redirect('/settings')
            return

        show_media=self.param('show_media')

        settings={}
        settings['show_media']=True if show_media=='True' else False

        md.set_token_settings(tk, users.get_current_user(), **settings)

        self.redirect('/settings/twitdao?tk=%s' % tk)



def main():
    application = webapp.WSGIApplication([
        ('/settings', Settings),
        ('/settings/auth', Auth),
        ('/settings/callback', AuthCallback),
        ('/settings/delete_token', DeleteToken),
        ('/settings/set_default_token', SetDefaultToken),

        ('/settings/profile', SettingsProfile),
        ('/settings/design', SettingsDesign),
        ('/settings/twitdao', SettingsTwitdao),
        #('/settings/sync', SettingsSync), #TODO

    ], debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()

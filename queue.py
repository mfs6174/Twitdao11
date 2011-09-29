# -*- coding: utf-8 -*-
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util

from base import BaseHandler
from twitdao import Twitdao

import md
import urllib
import logging

class UpdateUserCache(BaseHandler):

    def get(self):
        tk = self.param('tk')
        screen_name = self.param('screen_name')
        user_id = self.param('user_id')

        params={'_twitdao_force_refresh':True}
        include_entities = self.param('include_entities')
        if include_entities:
            params.update({'include_entities':include_entities})

        token = md.get_access_token(tk)
        td = Twitdao(token)
        user = None
        if user_id:
            user=td.users_show_by_id(user_id=user_id, **params)
        elif screen_name:
            user=td.users_show_by_screen_name(screen_name=screen_name, **params)
        logging.debug(user)
        if 'X-AppEngine-QueueName' not in self.request.headers:
            self.write(repr(user))


class VerifyAccess(BaseHandler):
    def get(self):
        tk = self.param('tk')
        token = md.get_access_token(tk)

        if not token:
            logging.debug('Token not found.')
            return

        td = Twitdao(token)
        token_user = td.account_verify_credentials()
        if 'error' in token_user:
            logging.debug('Delete invalid token: %s' % token)
            md.delete_access_token(token.key())
        else:
            logging.debug('Verified token: %s' % token)
        if 'X-AppEngine-QueueName' not in self.request.headers:
            self.write(repr(token_user))


class ListAddUser(BaseHandler):
    def get(self):
        tk = self.param('tk')
        list_id = self.param('list_id')
        screen_name = self.param('screen_name')

        token = md.get_access_token(tk)
        td = Twitdao(token)
        lst=td.user_list_id_members_post(token.screen_name, urllib.quote(list_id.encode('utf-8')), id=screen_name)
        logging.debug(lst)
        if 'X-AppEngine-QueueName' not in self.request.headers:
            self.write(repr(lst))


def main():
    application = webapp.WSGIApplication([
        ('/q/update_user_cache', UpdateUserCache),
        ('/q/verify_access', VerifyAccess),
        ('/q/list_add_user', ListAddUser),

    ], debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()

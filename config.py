# -*- coding: utf-8 -*-
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.api import users
from google.appengine.api import memcache
from google.appengine.api import taskqueue

from base import BaseHandler
import md

import os
import logging


class AppConfig(BaseHandler):
    def get(self):
        app_config = None
        if users.is_current_user_admin():
            app_config = md.get_app_config()
        self.render('app-config.html', {
            'app_config':app_config,
            'where':'twitdao-config'
        })

    def post(self):
        params=self.params([
            'consumer_key',
            'consumer_secret',
            'request_token_url',
            'access_token_url',
            'authorize_url',
            'authenticate_url',
            'api_url',
            'search_api_url',
            'twitpic_api_key',
        ])
        md.set_app_config(**params)
        self.redirect('/config')


class ImageProxyConfig(BaseHandler):
    def get(self):
        image_proxy_config = None
        if users.is_current_user_admin():
            image_proxy_config = md.get_image_proxy_config()
        self.render('image-proxy-config.html', {
            'image_proxy_config':image_proxy_config,
            'where':'image_proxy-config'
        })

    def post(self):
        params=self.params([
            'flickr_api_key',
            'flickr_api_secret',
            'flickr_rest_api_url',
        ])
        md.set_image_proxy_config(**params)
        self.redirect('/config/image_proxy')


class Memcache(BaseHandler):
    def get(self):
        stats = memcache.get_stats()
        self.render('memcache-config.html',{
            'stats':stats,
            'success':self.params('success'),
            'where':'memcache-config'
        })

    def post(self):
        success = memcache.flush_all()
        self.redirect('/config/memcache?success=%s' % success)


class CleanUpAccesses(BaseHandler):
    def get(self):
        self.render('clean-up-accesses.html',{'where':'clean-up-accesses'})

    def post(self):

        self.response.headers['Content-Type'] = 'text/plain'

        cursor = self.param('cursor', default_value=None)

        manual = not ( 'X-AppEngine-QueueName' in self.request.headers or 'X-AppEngine-Cron' in self.request.headers )

        tokens, next_cursor = md.get_access_tokens(size=50, cursor=cursor)
        for token in tokens:
            taskqueue.add(queue_name='clean-up-accesses', url='/q/verify_access', params={'tk':token.key()}, method='GET')
            logging.debug('Add token: %s' % token)
            if manual:
                self.write('Add token: %s\n' % token)

        if next_cursor:
            taskqueue.add(queue_name='clean-up-accesses', url='/config/clean_up_accesses', params={'cursor':next_cursor}, method='POST')
            logging.debug('More cursor: %s' % next_cursor)
            if manual:
                self.write('\nMore cursor: %s\n' % next_cursor)
                self.write('\nThe program is still working, and will run for some time.\n')
                self.write('Go: [https://appengine.google.com/queuedetails?&app_id=%s&queue_name=clean-up-accesses] to watch details.' % os.environ['APPLICATION_ID'])
                self.write('\n'*20)
        else:
            logging.debug('No more accesses.')
            if manual:
                self.write('\nThe End.\n')


def main():
    application = webapp.WSGIApplication([
        ('/config', AppConfig),
        ('/config/image_proxy', ImageProxyConfig),
        ('/config/memcache', Memcache),
        ('/config/clean_up_accesses', CleanUpAccesses),

    ], debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()

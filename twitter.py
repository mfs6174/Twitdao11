# -*- coding: utf-8 -*-
import oauth

from django.utils import simplejson as json
from google.appengine.api import urlfetch

import urllib
from cgi import parse_qsl
import mimetypes
import random

import logging

#default configs
CONSUMER_KEY = ''
CONSUMER_SECRET = ''

REQUEST_TOKEN_URL = 'https://api.twitter.com/oauth/request_token'
ACCESS_TOKEN_URL = 'https://api.twitter.com/oauth/access_token'

AUTHORIZE_URL = 'https://twitter.com/oauth/authorize'
AUTHENTICATE_URL = 'https://twitter.com/oauth/authenticate'

API_URL = 'https://api.twitter.com/1.1/'
SEARCH_API_URL = 'https://api.twitter.com/1.1/search/'


MAX_FETCH_COUNT = 5


_http_methods={
    'GET':urlfetch.GET,
    'POST':urlfetch.POST,
    'HEAD':urlfetch.HEAD,
    'PUT':urlfetch.PUT,
    'DELETE':urlfetch.DELETE
}

def _generate_boundary(length=16):
    s = '1234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ-_'
    a = []
    for i in range(length):
        a.append(random.choice(s))
    return ''.join(a)

class Twitter:

    def __init__(self,
        oauth_token=None,
        oauth_token_secret=None,
        consumer_key=CONSUMER_KEY,
        consumer_secret=CONSUMER_SECRET,
        request_token_url=REQUEST_TOKEN_URL,
        access_token_url=ACCESS_TOKEN_URL,
        authorize_url=AUTHORIZE_URL,
        authenticate_url=AUTHENTICATE_URL,
        api_url=API_URL,
        search_api_url=SEARCH_API_URL
    ):
        if oauth_token and oauth_token_secret:
            token = oauth.OAuthToken(oauth_token, oauth_token_secret)
        else:
            token = None
        self._consumer = oauth.OAuthConsumer(consumer_key, consumer_secret)
        self._signature_method = oauth.OAuthSignatureMethod_HMAC_SHA1()
        self._oauth_token = token

        self.http_status=0
        self.http_headers={}
        self.http_body=''
        
        #api config
        self.request_token_url=request_token_url
        self.access_token_url=access_token_url
        self.authorize_url=authorize_url
        self.authenticate_url=authenticate_url
        self.api_url=api_url
        self.search_api_url=search_api_url


    def _get_content_type(self, filename):
        return mimetypes.guess_type(filename)[0] or 'application/octet-stream'


    def _encode_multipart_formdata(self, fields, files=[]):
        """
        fields is a sequence of (name, value) elements for regular form fields.
        files is a sequence of (name, filename, value) elements for data to be uploaded as files
        Return (boundary, body)
        """
        boundary=_generate_boundary()
        crlf = '\r\n'

        l = []
        for k, v in fields:
            l.append('--' + boundary)
            l.append('Content-Disposition: form-data; name="%s"' % k)
            l.append('')
            l.append(v)
        for (k, f, v) in files:
            l.append('--' + boundary)
            l.append('Content-Disposition: form-data; name="%s"; filename="%s"' % (k, f))
            l.append('Content-Type: %s' % self._get_content_type(f))
            l.append('')
            l.append(v)
        l.append('--' + boundary + '--')
        l.append('')
        body = crlf.join(l)
        return boundary, body


    def _fetch(self, method, url, params={}, headers={}, files=None):
        payload=None
        if method.upper() in ['POST','PUT']:
            if files and type(files) == list:
                boundary, payload = self._encode_multipart_formdata(params.items(), files)
                headers['Content-Type']='multipart/form-data; boundary=%s' % boundary
            else:
                payload=urllib.urlencode(params)
        res=urlfetch.fetch(url, payload, _http_methods[method.upper()], headers)
        self.http_status=res.status_code
        self.http_headers=res.headers
        self.http_body=res.content
        logging.debug('[Twitter] Response Headers: %s' % res.headers)
        return res.content


    def _extend_fetch(self, method, url, params={}, headers={}, files=None):
        http_body=''
        for count in range(MAX_FETCH_COUNT):
            try:
                http_body = self._fetch(method, url, params, headers, files)
                if self.http_status!=200:
                    logging.debug('[HTTP Status %s] body %s' % (self.http_status, http_body) )
                if self.http_status in range(499, 600):
                    continue
                logging.debug('[Twitter] fetch count: %s ' % str(count+1))
                return http_body
            except urlfetch.DownloadError, e:
                logging.warning('[Twitter] urlfetch: %s' % e)
                continue
        raise Exception('Max fetch count exceeded.')


    def oauth_request(self, url, params={}, method = 'GET', files=None):
        oauth_request = oauth.OAuthRequest.from_consumer_and_token(
            self._consumer,
            self._oauth_token,
            http_url=url,
            http_method=method,
            parameters = params if not files else {}
        )
        oauth_request.sign_request(
            self._signature_method,
            self._consumer,
            self._oauth_token
        )

        if method.upper() == 'GET':
            resp = self._extend_fetch(method, oauth_request.to_url())
        else:
            resp = self._extend_fetch(
                method,
                oauth_request.get_normalized_http_url(),
                params,
                headers=oauth_request.to_header(),
                files=files
            )
        return resp


    def fetch_request_token(self, callback=None):
        """returns {'oauth_token':'the-request-token',
                   'oauth_token_secret':'the-request-secret',
                   'oauth_callback_confirmed':'true'}"""
        param = {}
        if callback:
            param.update({'oauth_callback':callback})
        response_body = self.oauth_request(self.request_token_url, param)
        request_token = dict(parse_qsl(response_body))

        if 'oauth_token' not in request_token:
            return None

        self._oauth_token = oauth.OAuthToken(
            request_token['oauth_token'],
            request_token['oauth_token_secret']
        )
        return request_token


    def fetch_access_token(self, verifier):
        """returns {'oauth_token':'the-access-token',
                   'oauth_token_secret':'the-access-secret',
                   'user_id':'1234567',
                   'screen_name':'darasion'}"""
        param = {}
        param.update({'oauth_verifier':verifier})
        response_body = self.oauth_request(self.access_token_url, param, 'POST')
        
        access_token = dict(parse_qsl(response_body))

        if 'oauth_token' not in access_token:
            return None

        self._oauth_token = oauth.OAuthToken(
            access_token['oauth_token'],
            access_token['oauth_token_secret']
        )
        return access_token


    def get_authenticate_url(self, request_token, force_login=False):
        if force_login:
            return "%s?oauth_token=%s&force_login=true" % (self.authenticate_url, request_token['oauth_token'])
        else:
            return "%s?oauth_token=%s" % (self.authenticate_url, request_token['oauth_token'])


    def get_authorize_url(self, request_token, force_login=False):
        if force_login:
            return "%s?oauth_token=%s&force_login=true" % (self.authorize_url, request_token['oauth_token'])
        else:
            return "%s?oauth_token=%s" % (self.authorize_url, request_token['oauth_token'])


    def api_call(self, http_method, api_method, parameters={}, files=None):
        try:
            return json.loads(self.oauth_request(''.join([
                self.api_url,
                api_method,
                '.json'
            ]), parameters, http_method, files))
        except:
            logging.warning('[Twitter] Still cant handle: Status: %s, Body: %s' % (self.http_status, self.http_body))
            raise


    def get_users_profile_image_url(self, screen_name, size='normal'):
        res=urlfetch.fetch('%s/users/profile_image/%s?size=%s' % (self.api_url, screen_name, size), follow_redirects=False)
        if res.status_code == 302 or res.status_code == 301:
            return res.headers['location']
        return None

    def search_api_call(self, q, **params):
        pms={'q':q}
        pms.update(params)
        data = urllib.urlencode(pms)
        return json.loads(urllib.urlopen(''.join([self.search_api_url, 'tweets.json']), data).read())

    def hacked_search(self, q, since_id=None, page=None):
        # since_id, page(next_page)
        # include_entities=1, contributor_details=true, domain=https://twitter.com, format=phoenix
        pms={
            'q':q,
            'include_entities':'1',
            'contributor_details':'true',
            'format':'phoenix',
            'domain':'https://twitter.com'
        }
        if since_id:
            pms['since_id']=since_id
        if page:
            pms['page']=page
        pms['rpp']=200

        data = urllib.urlencode(pms)
        url="https://twitter.com/phoenix_search.phoenix"

        res = json.loads(self.oauth_request(''.join([url, '?', data]), pms, 'GET'))
        try:
            logging.debug('RateLimit Class: %s' %  self.http_headers['X-RateLimit-Class'])
            logging.debug('RateLimit Limit: %s' % self.http_headers['X-RateLimit-Limit'])
            logging.debug('RateLimit Remaining: %s' % self.http_headers['X-RateLimit-Remaining'])
            logging.debug('RateLimit Reset: %s' % self.http_headers['X-RateLimit-Reset'])
        except:
            pass
        return res

    def hacked_following_followers_of(self, user_id):
        # Also followed by.
        # user_id, cursor=-1
        pms={'user_id':user_id,'cursor':'-1'}
        qs = urllib.urlencode(pms)
        url='https://twitter.com/users/following_followers_of.json'

        res = json.loads(self.oauth_request(''.join([url, '?', qs]), pms, 'GET'))
        try:
            logging.debug('RateLimit Class: %s' %  self.http_headers['X-RateLimit-Class'])
            logging.debug('RateLimit Limit: %s' % self.http_headers['X-RateLimit-Limit'])
            logging.debug('RateLimit Remaining: %s' % self.http_headers['X-RateLimit-Remaining'])
            logging.debug('RateLimit Reset: %s' % self.http_headers['X-RateLimit-Reset'])
        except:
            pass
        return res

    def hacked_follows_in_common_with(self, user_id):
        # You both follow.
        # user_id, cursor=-1
        pms={'user_id':user_id,'cursor':'-1'}
        qs = urllib.urlencode(pms)
        url='https://twitter.com/users/follows_in_common_with.json'

        res = json.loads(self.oauth_request(''.join([url, '?', qs]), pms, 'GET'))
        try:
            logging.debug('RateLimit Class: %s' %  self.http_headers['X-RateLimit-Class'])
            logging.debug('RateLimit Limit: %s' % self.http_headers['X-RateLimit-Limit'])
            logging.debug('RateLimit Remaining: %s' % self.http_headers['X-RateLimit-Remaining'])
            logging.debug('RateLimit Reset: %s' % self.http_headers['X-RateLimit-Reset'])
        except:
            pass
        return res

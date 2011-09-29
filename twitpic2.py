# -*- coding: utf-8 -*-

import mimetypes
import urllib
import random

import oauth

from django.utils import simplejson as json
from google.appengine.api import urlfetch

_http_methods={
    'GET':urlfetch.GET,
    'POST':urlfetch.POST,
    'HEAD':urlfetch.HEAD,
    'PUT':urlfetch.PUT,
    'DELETE':urlfetch.DELETE
}

_requires_authentication=[
    'upload',
    'comments/create',
    'comments/delete',
    'comments/create',
    'comments/delete',
    'faces/show',
    'faces/create',
    'faces/edit',
    'faces/delete',
    'event/create',
    'event/delete',
    'event/add',
    'event/remove',
    'tags/create',
    'tags/delete'
]

def _generate_boundary(length=16):
    s = '1234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ-_'
    a = []
    for i in range(length):
        a.append(random.choice(s))
    return ''.join(a)

def _get_content_type(filename):
    return mimetypes.guess_type(filename)[0] or 'application/octet-stream'

def _encode_multipart_formdata(fields, files=[]):
    """
    fields is a sequence of (name, value) elements for regular form fields.
    files is a sequence of (name, filename, value) elements for data to be uploaded as files
    Return (boundary, body)
    """
    boundary = _generate_boundary()
    crlf = '\r\n'

    l = []
    for k, v in fields:
        l.append('--' + boundary)
        l.append('Content-Disposition: form-data; name="%s"' % k)
        l.append('')
        l.append(str(v))
    for (k, f, v) in files:
        l.append('--' + boundary)
        l.append('Content-Disposition: form-data; name="%s"; filename="%s"' % (k, f))
        l.append('Content-Type: %s' % _get_content_type(f))
        l.append('')
        l.append(str(v))
    l.append('--' + boundary + '--')
    l.append('')
    body = crlf.join(l)
    return boundary, body


class TwitPic2(oauth.OAuthClient):
    """TwitPic OAuth Client API"""
    
    SIGNIN_URL        = 'https://api.twitter.com/oauth/authenticate'
    STATUS_UPDATE_URL = 'https://api.twitter.com/1/statuses/update.json'
    USER_INFO_URL     = 'https://api.twitter.com/1/account/verify_credentials.json'
    
    FORMAT = 'json'
    SERVER = 'http://api.twitpic.com/2/'
      
    def __init__(self, consumer_key=None, consumer_secret=None, 
                 service_key=None, access_token=None):
        """
        An object for interacting with the Twitpic API.
        
        The arguments listed below are generally required for most calls.
        
        Args:
          consumer_key:
            Twitter API Key [optional]
          consumer_secret:
            Twitter API Secret [optional]
          access_token:
            Authorized access_token in string format. [optional]
          service_key:
            Twitpic service key used to interact with the API. [optional]
        
        NOTE:
          The TwitPic OAuth Client does NOT support fetching 
          an access_token. Use your favorite Twitter API Client to 
          retrieve this.
        
        """
        self.server = self.SERVER
        self.consumer = oauth.OAuthConsumer(consumer_key, consumer_secret)
        self.signature_method = oauth.OAuthSignatureMethod_HMAC_SHA1()
        self.service_key = service_key        
        self.format = self.FORMAT

        self.http_status=0
        self.http_headers={}
        self.http_body=''

        if access_token:
            self.access_token = oauth.OAuthToken.from_string(access_token)
    
    def set_comsumer(self, consumer_key, consumer_secret):
        self.consumer = oauth.OAuthConsumer(consumer_key, consumer_secret)
    
    def set_access_token(self, accss_token):
        self.access_token = oauth.OAuthToken.from_string(access_token)
    
    def set_service_key(self, service_key):
        self.service_key = service_key

    def _fetch(self, method, url, params={}, headers={}, files=None):
        payload=None
        if method.upper() in ['POST','PUT']:
            if files and type(files) == list:
                boundary, payload = _encode_multipart_formdata(params.items(), files)
                headers['Content-Type']='multipart/form-data; boundary=%s' % boundary
            else:
                payload=urllib.urlencode(params)
        res=urlfetch.fetch(url, payload, _http_methods[method.upper()], headers)
        self.http_status=res.status_code
        self.http_headers=res.headers
        self.http_body=res.content
        return res.content

    def api_call(self, http_method, api_method, params={}, files=None):

        url = '%s%s.%s' % (self.server, api_method, self.format)

        if api_method not in _requires_authentication:
            resp = self._fetch(http_method, url, params, headers)
            return json.loads(resp)

        oauth_request = oauth.OAuthRequest.from_consumer_and_token(
            self.consumer,
            self.access_token,
            http_url=self.USER_INFO_URL
        )

        # Sign our request before setting Twitpic-only parameters
        oauth_request.sign_request(self.signature_method, self.consumer, self.access_token)

        # Set TwitPic parameters
        oauth_request.set_parameter('key', self.service_key)

        for key, value in params.iteritems():
            oauth_request.set_parameter(key, value)

        # Build request body parameters.
        params = oauth_request.parameters

        # Get the oauth headers.
        oauth_headers = oauth_request.to_header(realm='http://api.twitter.com/')

        # Add the headers required by TwitPic and any additional headers.
        headers = {
            'X-Verify-Credentials-Authorization': oauth_headers['Authorization'],
            'X-Auth-Service-Provider': self.USER_INFO_URL,
        }

        resp=self._fetch(http_method, url, params, headers, files)
        return json.loads(resp)

# -*- coding: utf-8 -*-
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.api import memcache
from google.appengine.api import urlfetch

from base import BaseHandler
from django.utils import simplejson as json
from datetime import datetime

import md
import logging
import urllib


_cached_headers=['last-modified', 'etag', 'cache-control', 'expires', 'content-type']

class ImageProxy(BaseHandler):

    def initialize(self, request, response):
        BaseHandler.initialize(self, request, response)
        self.image_proxy_config = md.get_image_proxy_config()

    def get_image(self, image_url, cache_id=None):
        if not cache_id: cache_id=image_url
        _cache=memcache.get(cache_id)
        if _cache:
            if self.request.if_modified_since and 'last-modified' in _cache:
                since = self.request.if_modified_since
                last = datetime.strptime(_cache['last-modified'], '%a, %d %b %Y %H:%M:%S GMT')
                if not last.tzinfo:
                    since=since.replace(tzinfo=None)
                if last<=since:
                    logging.debug('[ImageProxy] Hit Cache: last-modified')
                    self.response.set_status(304)
                    if 'content-type' in _cache:
                        self.response.headers['Content-Type']=_cache['content-type']
                    return
            if self.request.if_none_match and 'etag' in _cache:
                if str(self.request.if_none_match) == _cache['etag']:
                    logging.debug('[ImageProxy] Hit Cache: etag')
                    self.response.set_status(304)
                    if 'content-type' in _cache:
                        self.response.headers['Content-Type']=_cache['content-type']
                    return

        image=urlfetch.fetch(image_url)
        logging.debug('[ImageProxy] Response Headers: %s' % image.headers)

        _cache={}
        for h in _cached_headers:
            if h in image.headers:
                _cache[h]=image.headers[h]
                self.response.headers[h]=image.headers[h]
        memcache.set(cache_id, _cache)
        logging.debug('[ImageProxy] Cached Header: %s' % _cache)

        self.response.out.write(image.content)


def b58decode(s):
    alphabet = '123456789abcdefghijkmnopqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ'
    num, decoded, multi = len(s), 0, 1
    for i in range(num-1, -1, -1):
        decoded = decoded+multi*(alphabet.index(s[i]))
        multi = multi*len(alphabet)
    return decoded

def flickr_rest(api_url, **params):
    params.update( { 'format':'json', 'nojsoncallback':1 } )
    try:
        http_method = params.pop('http_method')
    except KeyError:
        http_method = urlfetch.GET
    res=urlfetch.fetch('%s?%s' % (api_url, urllib.urlencode(params)), method=http_method)
    content = json.loads(res.content)
    logging.debug('[ImageProxy] Flickr REST: %s' % content)
    return content

class Flickr(ImageProxy):
    def get(self, link_type, image_id):

        api_key = self.image_proxy_config.flickr_api_key
        rest_api_url = self.image_proxy_config.flickr_rest_api_url

        if not api_key:
            self.redirect('/images/flickr-not-ready.png')
            return

        photo_id = image_id        
        if link_type == 'short':
            photo_id = b58decode(image_id)

        image_url = memcache.get('Image-Flickr-URL-%s-%s' % (link_type, image_id) )
        if not image_url:
            fpi = flickr_rest(rest_api_url, method='flickr.photos.getInfo', api_key=api_key, photo_id=photo_id )
            if fpi['stat'] == 'fail':
                self.redirect('/images/flickr-not-ready.png')
                return
            p = fpi['photo']
            image_url = 'http://farm%s.static.flickr.com/%s/%s_%s_m.jpg' % (p['farm'], p['server'], p['id'], p['secret'])
            memcache.set('Image-Flickr-URL-%s-%s' % (link_type, image_id), image_url)

        cache_id = 'Image-Flickr-%s' % image_id
        self.get_image(image_url, cache_id)


class Twitpic(ImageProxy):
    def get(self, image_size, image_id):
        # Thumb(150px x 150px max), Mini(75px x 75px max)
        # http://twitpic.com/show/[size]/[image-id]
        image_url = 'http://twitpic.com/show/%s/%s' % (image_size, image_id)
        cache_id = 'Image-Twitpic-%s-%s' % (image_size, image_id)
        self.get_image(image_url, cache_id)


class Twitgoo(ImageProxy):
    def get(self, image_size, image_id):
        # Thumb/mini (up to 160x160), Img (up to 1600x1600)
        # http://twitgoo.com/show/[size]/[gooid]
        image_url='http://twitgoo.com/show/%s/%s' % (image_size, image_id)
        cache_id='Image-Twitgoo-%s-%s' % (image_size, image_id)
        self.get_image(image_url, cache_id)


class Yfrog(ImageProxy):
    def get(self, domain_tail, image_id):
        image_url='http://yfrog.%s/%s.th.jpg' % (domain_tail, image_id)
        cache_id='Image-Yfrog-%s-%s' % (domain_tail, image_id)
        self.get_image(image_url, cache_id)


class Imgly(ImageProxy):
    def get(self, image_size, image_id):
        # http://img.ly/show/[mini|thumb|medium|large|full]/<image-id>
        image_url='http://img.ly/show/%s/%s' % (image_size, image_id)
        cache_id='Image-Imgly-%s-%s' % (image_size, image_id)
        self.get_image(image_url, cache_id)


class Youtube(ImageProxy):
    def get(self, video_id):
        image_url='http://i.ytimg.com/vi/%s/1.jpg' % video_id
        cache_id='Image-Youtube-%s' % video_id
        self.get_image(image_url, cache_id)

        
class Moby(ImageProxy):
    def get(self, image_size, image_id):
        #full, square, view, medium, thumbnail, thumb
        image_url='http://moby.to/%s:%s' % (image_id, image_size)
        cache_id='Image-Moby-%s-%s' % (image_size, image_id)
        self.get_image(image_url, cache_id)


class Instagram(ImageProxy):
    def get(self, image_id, image_size):
        #size: One of t (thumbnail), m (medium), l (large). Defaults to m.
        if not image_size:
            image_size='l'
        image_url='http://instagr.am/p/%s/media/?size=%s' % (image_id, image_size)
        #self.get_image(image_url)
        self.redirect(image_url)


def picplz_url(image_id, image_size):
    # See: https://sites.google.com/site/picplzapi/
    api_url='http://api.picplz.com/api/v2/pic.json'
    try:
        res=urlfetch.fetch('%s?shorturl_id=%s' % (api_url, image_id))
        img=json.loads(res.content)
        if img['result']!='ok':
            return None
        else:
            return img['value']['pics'][0]['pic_files'][image_size]['img_url']
    except urlfetch.DownloadError:
        return None
    except KeyError, e:
        logging.warning(e)
        return None

class Picplz(ImageProxy):
    def get(self, image_id, image_size):
        # The default format list is: 640r, 320rh, 100sh
        if not image_size:
            image_size='320rh'
        image_url = picplz_url(image_id, image_size)
        if image_url:
            self.get_image(image_url)
        else:
            self.error(404)


class Plixi(ImageProxy):
    def get(self, image_id, image_size):
        # big - original
        # medium - 600px scaled
        # mobile - 320px scaled
        # small - 150px cropped
        # thumbnail - 79px cropped
        if not image_size:
            image_size='mobile'
        image_url = 'http://api.plixi.com/api/tpapi.svc/imagefromurl?url=http://plixi.com/p/%s&size=%s' % (image_id, image_size)
        self.get_image(image_url)

def main():
    application = webapp.WSGIApplication([
        ('/i/twitpic/(thumb|mini)/([0-9a-zA-Z]+)', Twitpic),
        ('/i/twitgoo/(thumb|mini|img)/([0-9a-zA-Z]+)', Twitgoo),
        ('/i/yfrog/([\.a-zA-Z]+)/([0-9a-zA-Z]+)', Yfrog),
        ('/i/imgly/(mini|thumb|medium|large|full)/([0-9a-zA-Z]+)', Imgly),
        ('/i/flickr/(long|short)/([0-9a-zA-Z]+)', Flickr),
        ('/i/y2b/([0-9a-zA-Z_\-]+)', Youtube),
        ('/i/moby/(full|square|view|medium|thumbnail|thumb)/([0-9a-zA-Z]+)', Moby),
        ('/i/instagram/(?P<image_id>[0-9a-zA-Z_\-]+)(?:/(?P<image_size>t|m|l))?', Instagram),
        ('/i/picplz/([0-9a-zA-Z]+)(?:/(?P<image_size>640r|320rh|100sh))?', Picplz),
        ('/i/plixi/(?P<image_id>[0-9a-zA-Z]+)(?:/(?P<image_size>big|medium|mobile|small|thumbnail))?', Plixi),

    ], debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()

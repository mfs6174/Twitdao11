# -*- coding: utf-8 -*-
from google.appengine.ext import webapp
from django.template.defaultfilters import stringfilter
from google.appengine.api import urlfetch
from django.utils import simplejson as json
#from google.appengine.api import memcache

import re
import urllib
import ttp

register = webapp.template.create_template_register()

_twitpic=re.compile('https?://twitpic\.com/(?P<id>[0-9a-zA-Z]+)', re.I)
_twitgoo=re.compile('https?://twitgoo\.com/(?P<id>[0-9a-zA-Z]+)', re.I)
_imgly=re.compile('https?://img\.ly/(?P<id>[0-9a-zA-Z]+)', re.I)
_yfrog=re.compile('https?://yfrog\.(?P<tail>[^/]+)(/[a-z])?/(?P<id>[0-9a-zA-Z]{2,})', re.I)
_flic_kr=re.compile('https?://flic\.kr/p/(?P<id>[0-9a-zA-Z]+)', re.I)
_flickr_com=re.compile('https?://(www\.|)flickr\.com/photos/[0-9a-zA-Z_]+/(?P<id>[0-9]+)', re.I)
_youtu_be=re.compile('https?://youtu\.be/(?P<id>[0-9a-zA-Z_\-]+)', re.I)
_youtube_com=re.compile('https?://(www\.|)youtube\.com/((watch\?v=)|(v/))(?P<id>[0-9a-zA-Z_\-]+)', re.I)
_moby_to=re.compile('https?://moby\.to/(?P<id>[0-9a-zA-Z]+)', re.I)
_instagram=re.compile('https?://instagr\.am/p/(?P<id>[0-9a-zA-Z_\-]+)', re.I)
_instagramcom=re.compile('https?://instagram\.com/p/(?P<id>[0-9a-zA-Z_\-]+)', re.I)
_picplz=re.compile('https?://picplz\.com/(?P<id>[0-9a-zA-Z]+)', re.I)
_plixi=re.compile('https?://plixi\.com/p/(?P<id>[0-9a-zA-Z]+)', re.I)

_youku=re.compile('https?://v\.youku\.com/v_show/id_(?P<id>[0-9a-zA-Z_\-=]+)\.html', re.I)
_tudou=re.compile('https?://(www\.|)tudou\.com/programs/view/(?P<id>[0-9a-zA-Z_\-]+)', re.I)
_56=re.compile('https?://(www\.|)56\.com/([0-9a-zA-Z]+)/v_(?P<id>[0-9a-zA-Z_\-]+)\.html', re.I)
_ku6=re.compile('https?://v\.ku6\.com/show/(?P<id>[0-9a-zA-Z_\-]+)\.html', re.I)

_bitly = re.compile('http://bit\.ly/(?P<id>[0-9a-zA-Z_\-]+)', re.I)
_jmp = re.compile('http://j\.mp/(?P<id>[0-9a-zA-Z_\-]+)', re.I)
_tco = re.compile('http://t\.co/(?P<id>[a-z0-9]*)', re.I)
_tcn = re.compile('http://t\.cn/(?P<id>[a-z0-9]*)', re.I)

_isgd = re.compile('http://is\.gd/(?P<id>[0-9a-zA-Z_\-]+)', re.I)
_googl = re.compile('http://goo\.gl/(?P<id>[0-9a-zA-Z_\-]{3,})', re.I)
_googlfb = re.compile('http://goo\.gl/fb/(?P<id>[0-9a-zA-Z_\-]+)', re.I)

@register.filter
@stringfilter
def image_preview(url):
    ''' show photo thumbnails '''
    try:
        url,is_short= url_unshort(url)
    except:
         return '<span class="unshorturl"><a href="%s" target="_blank" rel="noreferrer">%s</a></span>' % (url,url)
    m=_twitpic.search(url)
    if m:
        twitpic_id=m.group('id')
        if twitpic_id.lower() in ['photos','events','places','widgets','upload','account','logout','doc']:
            return ''
        return '<a href="%s" target="_blank" rel="noreferrer"><img src="/i/twitpic/%s/%s" /></a>' % ( url, 'thumb', twitpic_id )

    m=_twitgoo.search(url)
    if m:
        twitgoo_id=m.group('id')
        return '<a href="%s" target="_blank" rel="noreferrer"><img src="/i/twitgoo/%s/%s" /></a>' % ( url, 'thumb', twitgoo_id )

    m=_imgly.search(url)
    if m:
        imgly_id=m.group('id')
        return '<a href="%s" target="_blank" rel="noreferrer"><img src="/i/imgly/%s/%s" /></a>' % ( url, 'medium', imgly_id )

    m=_yfrog.search(url)
    if m:
        yfrog_id=m.group('id')
        yfrog_tail=m.group('tail')
        return '<a href="%s" target="_blank" rel="noreferrer"><img src="/i/yfrog/%s/%s" /></a>' % ( url, yfrog_tail, yfrog_id )

    m=_flic_kr.search(url)
    if m:
        flickr_id=m.group('id')
        return '<a href="%s" target="_blank" rel="noreferrer"><img src="/i/flickr/short/%s" /></a>' % ( url, flickr_id )

    m=_flickr_com.search(url)
    if m:
        flickr_id=m.group('id')
        return '<a href="%s" target="_blank" rel="noreferrer"><img src="/i/flickr/long/%s" /></a>' % ( url, flickr_id )

    m=_youtu_be.search(url)
    if m:
        youtube_id=m.group('id')
        return '<a href="%s" target="_blank" rel="noreferrer"><img src="/i/y2b/%s" /></a>' % ( url, youtube_id )

    m=_youtube_com.search(url)
    if m:
        youtube_id=m.group('id')
        return '<a href="%s" target="_blank" rel="noreferrer"><img src="/i/y2b/%s" /></a>' % ( url, youtube_id )

    m=_moby_to.search(url)
    if m:
        moby_id=m.group('id')
        return '<a href="%s" target="_blank" rel="noreferrer"><img src="/i/moby/thumb/%s" /></a>' % ( url, moby_id )

    m=_instagram.search(url)
    if m:
        insid=m.group('id')
        return '<a href="%s" target="_blank" rel="noreferrer"><img src="/i/instagram/%s" width="550" /></a>' % ( url, insid )
    m=_instagramcom.search(url)
    if m:
        insid=m.group('id')
        return '<a href="%s" target="_blank" rel="noreferrer"><img src="/i/instagram/%s" width="550" /></a>' % ( url, insid )

    m=_picplz.search(url)
    if m:
        pic_id=m.group('id')
        return '<a href="%s" target="_blank" rel="noreferrer"><img src="/i/picplz/%s" /></a>' % ( url, pic_id )

    m=_plixi.search(url)
    if m:
        pic_id=m.group('id')
        return '<a href="%s" target="_blank" rel="noreferrer"><img src="/i/plixi/%s" /></a>' % ( url, pic_id )
    
    m=_youku.search(url)
    if m:
        youku_id=m.group('id')
        return '<embed src="http://player.youku.com/player.php/sid/%s/v.swf" quality="high" width="480" height="400" align="middle" allowScriptAccess="sameDomain" type="application/x-shockwave-flash"></embed>' % youku_id
    
    m=_tudou.search(url)
    if m:
        tudou_id=m.group('id')
        return '<embed src="http://www.tudou.com/v/%s/v.swf" type="application/x-shockwave-flash" allowscriptaccess="always" allowfullscreen="true" wmode="opaque" width="480" height="400"></embed>' % tudou_id

    m=_56.search(url)
    if m:
        _56_id=m.group('id')
        return '<embed src="http://player.56.com/v_%s.swf"  type="application/x-shockwave-flash" width="480" height="395" allowNetworking="all" allowScriptAccess="always"></embed>' % _56_id

    m=_ku6.search(url)
    if m:
        ku6_id=m.group('id')
        return '<embed src="http://player.ku6.com/refer/%s/v.swf" quality="high" width="480" height="400" align="middle" allowScriptAccess="always" allowfullscreen="true" type="application/x-shockwave-flash"></embed>' % ku6_id
	if is_short == 1:
		return '<span class="unshorturl"><a href="%s" target="_blank" rel="noreferrer">%s</a></span>' % (url,url)
    return '<span class="unshorturl"><a href="%s" target="_blank" rel="noreferrer">%s</a></span>' % (url,url)

def url_unshort(url):
    m=_bitly.search(url)
    if m:
        bitly_id=m.group('id')
        try:
            res=urlfetch.fetch('http://api.unshort.me/?r=http://bit.ly/%s&t=json' % bitly_id)
            url_json = json.loads(res.content)
        
            newurl = url_json['resolvedURL']
            if newurl != "http://unshort.me":
                return newurl,1
        except urlfetch.DownloadError:
            return url,0

    m=_jmp.search(url)
    if m:
        jmp_id=m.group('id')
        try:
            res=urlfetch.fetch('http://api.unshort.me/?r=http://j.mp/%s&t=json' % jmp_id)
            url_json = json.loads(res.content)
        
            newurl = url_json['resolvedURL']
            if newurl != "http://unshort.me":
                return newurl,1
        except urlfetch.DownloadError:
            return url,0

    m=_tco.search(url)
    if m:
        tco_id=m.group('id')
        try:
            res=urlfetch.fetch('http://api.unshort.me/?r=http://t.co/%s&t=json' % tco_id)
            url_json = json.loads(res.content)
        
            newurl = url_json['resolvedURL']
            if newurl != "http://unshort.me":
                return newurl,1
        except urlfetch.DownloadError:
            return url,0

    m=_tcn.search(url)
    if m:
        tcn_id=m.group('id')
        try:
            res=urlfetch.fetch('http://api.unshort.me/?r=http://t.cn/%s&t=json' % tcn_id)
            url_json = json.loads(res.content)
        
            newurl = url_json['resolvedURL']
            if newurl != "http://unshort.me":
                return newurl,1
        except urlfetch.DownloadError:
            return url,0

    m=_isgd.search(url)
    if m:
        isgd_id=m.group('id')
        try:
            res=urlfetch.fetch('http://api.unshort.me/?r=http://is.gd/%s&t=json' % isgd_id)
            url_json = json.loads(res.content)
        
            newurl = url_json['resolvedURL']
            if newurl != "http://unshort.me":
                return newurl,1
        except urlfetch.DownloadError:
            return url,0
    m=_googl.search(url)
    if m:
        googl_id=m.group('id')
        try:
            res=urlfetch.fetch('http://api.unshort.me/?r=http://goo.gl/%s&t=json' % googl_id)
            url_json = json.loads(res.content)
        
            newurl = url_json['resolvedURL']
            if newurl != "http://unshort.me":
                return newurl,1
        except urlfetch.DownloadError:
            return url,0
    m=_googlfb.search(url)
    if m:
        googl_id=m.group('id')
        try:
            res=urlfetch.fetch('http://api.unshort.me/?r=http://goo.gl/fb/%s&t=json' % googl_id)
            url_json = json.loads(res.content)
        
            newurl = url_json['resolvedURL']
            if newurl != "http://unshort.me":
                return newurl,1
        except urlfetch.DownloadError:
            return url,0
    return url,0


#def get_url_cache(self, short_service, cache_id=None):

def _m_google_gwt_url(url):
    return 'http://www.google.com/gwt/n?u=%s' % urllib.quote(url)
def _m_baidu_gate_url(url):
    return 'http://gate.baidu.com/tc?from=opentc&src=%s' % urllib.quote(url)
def _m_media_url(url, op=None):
    if op=='google-gwt':
        url=_m_google_gwt_url(url)
    elif op=='baidu-gate':
        url=_m_baidu_gate_url(url)
    m=_twitpic.search(url)
    if m:
        twitpic_id=m.group('id')
        if twitpic_id.lower() in ['photos','events','places','widgets','upload','account','logout','doc']:
            return ''
        return '<a href="%s" target="_blank" rel="noreferrer"><img src="/i/twitpic/%s/%s" /></a>' % ( url, 'thumb', twitpic_id )
    m=_twitgoo.search(url)
    if m:
        twitgoo_id=m.group('id')
        return '<a href="%s" target="_blank" rel="noreferrer"><img src="/i/twitgoo/%s/%s" /></a>' % ( url, 'thumb', twitgoo_id )
    m=_imgly.search(url)
    if m:
        imgly_id=m.group('id')
        return '<a href="%s" target="_blank" rel="noreferrer"><img src="/i/imgly/%s/%s" /></a>' % ( url, 'thumb', imgly_id )
    m=_yfrog.search(url)
    if m:
        yfrog_id=m.group('id')
        yfrog_tail=m.group('tail')
        return '<a href="%s" target="_blank" rel="noreferrer"><img src="/i/yfrog/%s/%s" /></a>' % ( url, yfrog_tail, yfrog_id )
    m=_flic_kr.search(url)
    if m:
        flickr_id=m.group('id')
        return '<a href="%s" target="_blank" rel="noreferrer"><img src="/i/flickr/short/%s" /></a>' % ( url, flickr_id )
    m=_flickr_com.search(url)
    if m:
        flickr_id=m.group('id')
        return '<a href="%s" target="_blank" rel="noreferrer"><img src="/i/flickr/long/%s" /></a>' % ( url, flickr_id )
    m=_youtu_be.search(url)
    if m:
        youtube_id=m.group('id')
        return '<a href="%s" target="_blank" rel="noreferrer"><img src="/i/y2b/%s" /></a>' % ( url, youtube_id )
    m=_youtube_com.search(url)
    if m:
        youtube_id=m.group('id')
        return '<a href="%s" target="_blank" rel="noreferrer"><img src="/i/y2b/%s" /></a>' % ( url, youtube_id )
    m=_moby_to.search(url)
    if m:
        moby_id=m.group('id')
        return '<a href="%s" target="_blank" rel="noreferrer"><img src="/i/moby/thumb/%s" /></a>' % ( url, moby_id )
    m=_instagram.search(url)
    if m:
        insid=m.group('id')
        return '<a href="%s" target="_blank" rel="noreferrer"><img src="/i/instagram/%s" /></a>' % ( url, insid )
    m=_picplz.search(url)
    if m:
        pic_id=m.group('id')
        return '<a href="%s" target="_blank" rel="noreferrer"><img src="/i/picplz/%s" /></a>' % ( url, pic_id )
    m=_plixi.search(url)
    if m:
        pic_id=m.group('id')
        return '<a href="%s" target="_blank" rel="noreferrer"><img src="/i/plixi/%s" /></a>' % ( url, pic_id )
    return None

@register.filter
@stringfilter
def m_media_preview(text, op=None):
    p=ttp.Parser()
    urls=p.parse(text).urls
    medias=[]
    for url in urls:
        u=_m_media_url(url, op)
        if u:
            medias.append(u)
    return ''.join(medias)

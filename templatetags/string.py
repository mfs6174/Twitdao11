# -*- coding: utf-8 -*-
from google.appengine.ext import webapp
from django.utils import simplejson as json
from django.utils.safestring import mark_safe
from django.template.defaultfilters import stringfilter

import ttp
import utils

import time
import calendar
import rfc822
import htmllib
import urllib

register = webapp.template.create_template_register()

@register.filter
@stringfilter
def twitter_text_py(text):
    p = ttp.Parser()
    return p.parse(text).html

@register.filter
@stringfilter
def tweet_id_encode(text):
    return utils.tweet_id_encode(text)
tweet_id_encode.is_safe=True

@register.filter
@stringfilter
def tweet_id_decode(text):
    return utils.tweet_id_decode(text)
tweet_id_decode.is_safe=True

def _m_escape(text):
    return ''.join({'&':'&#38;', '"':'&#34;', '\'':'&#39;', '>':'&#62;', '<':'&#60;'}.get(c, c) for c in text)
def _m_format_tag(tag, text):
    return '<a href="/a/search?q=%s">%s%s</a>' % (urllib.quote('#' + text.encode('utf-8')), tag, text)
def _m_format_username(at_char, user):
    return '<a href="/m/u-%s">%s%s</a>' % (user, at_char, user)
def _m_format_list(at_char, user, list_name):
    return '<a href="/m/l-%s/%s">%s%s/%s</a>' % (user, list_name, at_char, user, list_name)
def _m_google_format_url(url, text):
    return '<a target="_blank" href="http://www.google.com/gwt/n?u=%s">%s</a>' % (urllib.quote(_m_escape(url).encode('utf-8')), text)
def _m_baidu_format_url(url, text):
    return '<a target="_blank" href="http://gate.baidu.com/tc?from=opentc&src=%s">%s</a>' % (urllib.quote(_m_escape(url).encode('utf-8')), text)
def _m_format_url(url, text):
    return '<a target="_blank" href="%s">%s</a>' % (_m_escape(url), text)

@register.filter
@stringfilter
def m_twitter_text(text, op=None):
    p = ttp.Parser()
    p.format_tag=_m_format_tag
    p.format_username=_m_format_username
    p.format_list=_m_format_list
    if op=='google-gwt':
        p.format_url=_m_google_format_url
    elif op=='baidu-gate':
        p.format_url=_m_baidu_format_url
    else:
        p.format_url=_m_format_url
    return p.parse(text).html

@register.filter
@stringfilter
def human_readable(date_str):
    '''Get a human redable string representing the posting time

    Returns:
      A human readable string representing the posting time
    '''
    if not date_str:
        return ''#TODO 似乎要仔细检查啊。
    fudge = 1.25
    delta  = long(time.time()) - long(calendar.timegm(rfc822.parsedate(date_str)))

    if delta < (1 * fudge):
        return 'a second ago'
    elif delta < (60 * (1/fudge)):
        return '%d seconds ago' % (delta)
    elif delta < (60 * fudge):
        return 'a minute ago'
    elif delta < (60 * 60 * (1/fudge)):
        return '%d minutes ago' % (delta / 60)
    elif delta < (60 * 60 * fudge):
        return 'about an hour ago'
    elif delta < (60 * 60 * 24 * (1/fudge)):
        return 'about %d hours ago' % (delta / (60 * 60))
    elif delta < (60 * 60 * 24 * fudge):
        return 'about a day ago'
    else:
        return 'about %d days ago' % (delta / (60 * 60 * 24))
human_readable.is_safe=True

@register.filter
@stringfilter
def time_format(date_str, fmt_str="%Y-%m-%d"):
    try:
        dtp=rfc822.parsedate(date_str)
        return time.strftime(fmt_str, dtp)
    except:
        return None
time_format.is_safe=True

@register.filter
@stringfilter
def milliseconds(date_str):
    dtp=rfc822.parsedate(date_str)
    if dtp:
        return long(time.mktime(dtp)*1000)
    else:
        return None
milliseconds.is_safe=True

@register.filter
@stringfilter
def unescape(s):
    p = htmllib.HTMLParser(None)
    p.save_bgn()
    p.feed(s)
    return p.save_end()

@register.filter
def to_json(obj):
    return mark_safe(json.dumps(obj))

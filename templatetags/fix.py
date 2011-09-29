# -*- coding: utf-8 -*-
from google.appengine.ext import webapp
from django.template.defaultfilters import stringfilter

import re

register = webapp.template.create_template_register()

@register.filter
@stringfilter
def secure_image(image_url):
    ''' *.twimg.com to https://*.amazonaws.com '''
    
    #comment this line when need https.
    return image_url

    m=re.search(r'a([0-9]+)\..+(/profile_images/.+)', image_url, re.I)
    if m:
        return 'https://s3.amazonaws.com/twitter_production%s' % m.group(2)
    return image_url
secure_image.is_safe=True

_origin_image_re=re.compile('_(normal|mini|bigger)\.(png|gif|jpg|jpeg)$', re.I)
@register.filter
@stringfilter
def origin_image(image_url):
    return _origin_image_re.sub('.\g<2>', image_url)
origin_image.is_safe=True
# -*- coding: utf-8 -*-
from google.appengine.dist import use_library
use_library('django','1.2')

from django.conf import settings
settings.configure(INSTALLED_APPS=('zombie',))

from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.api import users

from Cookie import SimpleCookie
import os

template.register_template_library('templatetags.string')
template.register_template_library('templatetags.fix')
template.register_template_library('templatetags.entities')
template.register_template_library('templatetags.tags')

class BaseHandler(webapp.RequestHandler):

    def initialize(self, request, response):
        webapp.RequestHandler.initialize(self, request, response)
        self.current = os.environ['PATH_INFO']
        self.logout_url = users.create_logout_url("/")
        self.template_vals = {
            'self':self
        }

    def render(self,tempalte_name, template_values={}, out=True):
        self.template_vals.update(template_values)
        directory = os.path.dirname(__file__)
        path = os.path.join(directory, os.path.join('templates', tempalte_name))
        result = template.render(path, self.template_vals)
        if out:
            self.response.out.write(result)
        return result

    def param(self, name, **kw):
        return self.request.get(name, **kw)

    def write(self, c):
        return self.response.out.write(c)
    
    def params(self, param_list, **default_vals):
        params={}
        for i in param_list:
            param=self.request.get(i)
            if param:
                params[i] = param
            elif i in default_vals:
                params[i]=default_vals[i]
            elif i=='include_entities': #temp
                params[i]='t'
        return params

    def jedirect(self, uri, time=5000, text="Redirecting..."):
        self.write('''<script type="text/javascript">
        setTimeout(function(){window.location="%s"},%s)
        </script>''' % (uri, time))
        self.write('%s' % text)

    def set_cookie(self, key, value='', max_age=None,
                   path='/', domain=None, secure=None, httponly=False,
                   version=None, comment=None):
        cookies = SimpleCookie()
        cookies[key] = value
        for var_name, var_value in [
            ('max-age', max_age),
            ('path', path),
            ('domain', domain),
            ('secure', secure),
            ('HttpOnly', httponly),
            ('version', version),
            ('comment', comment),
            ]:
            if var_value is not None and var_value is not False:
                cookies[key][var_name] = str(var_value)
        header_value = cookies[key].output(header='').lstrip()
        self.response.headers.add_header('Set-Cookie', header_value)
    
    def get_cookie(self, key, default=None):
        if key in self.request.cookies:
            return self.request.cookies[key]
        else:
            return default

    def delete_cookie(self, key):
        self.set_cookie(key, '', max_age=0)


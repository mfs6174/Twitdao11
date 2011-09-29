# -*- coding: utf-8 -*-
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.api import users

from base import BaseHandler

import md

_mobile = [
    '2.0 MMP',
    '240x320',
    '400X240',
    'AvantGo',
    'BlackBerry',
    'Blazer',
    'Cellphone',
    'Danger',
    'DoCoMo',
    'Elaine/3.0',
    'EudoraWeb',
    'Googlebot-Mobile',
    'hiptop',
    'IEMobile',
    'KYOCERA/WX310K',
    'LG/U990',
    'MIDP-2.',
    'MMEF20',
    'MOT-V',
    'NetFront',
    'Newt',
    'Nintendo Wii',
    'Nitro', #Nintendo DS
    'Nokia',
    'Opera Mini',
    'Opera Mobi', #Opera Mobile
    'Palm',
    'PlayStation Portable',
    'portalmmm',
    'Proxinet',
    'ProxiNet',
    'SHARP-TQ-GX10',
    'SHG-i900',
    'Small',
    'SonyEricsson',
    'Symbian OS',
    'SymbianOS',
    'TS21i-10',
    'UP.Browser',
    'UP.Link',
    'webOS', #Palm Pre, etc.
    'Windows CE',
    'WinWAP',
    'YahooSeeker/M1A1-R2D2',
]

_touch = [
    'iPhone',
    'iPod',
    'Android',
    'BlackBerry9530',
    'LG-TU915 Obigo', #LG touch browser
    'LGE VX',
    'webOS', #Palm Pre, etc.
    'Nokia5800',
]

def _is_mobile(ua):
    for b in _mobile + _touch:
        if ua.find(b)!=-1:
            return True
    return False


class Index(BaseHandler):
    def get(self):
        if not users.get_current_user():
            login_url = users.create_login_url("/")
            self.render('index.html', {'login_url':login_url})
        else:
            default_token = md.get_default_access_token()
            if default_token:
                if _is_mobile(self.request.headers['user-agent']):
                    self.redirect('/m/u-/home')
                else:
                    self.redirect('/t')
                return
            else:
                self.redirect('/settings')


def main():
    application = webapp.WSGIApplication([
        ('/', Index),
    ], debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()

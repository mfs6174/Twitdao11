# -*- coding: utf-8 -*-
from google.appengine.ext import db
from google.appengine.api import memcache
from google.appengine.api import users

import hashlib
import logging
import sys
import pickle



_app_config_cache=None

class AppConfig(db.Model):
    consumer_key = db.StringProperty(default='')
    consumer_secret = db.StringProperty(default='')

    request_token_url = db.StringProperty(default='https://api.twitter.com/oauth/request_token')
    access_token_url = db.StringProperty(default='https://api.twitter.com/oauth/access_token')

    authorize_url = db.StringProperty(default='https://twitter.com/oauth/authorize')
    authenticate_url = db.StringProperty(default='https://twitter.com/oauth/authenticate')

    api_url = db.StringProperty(default='https://api.twitter.com/1/')
    search_api_url = db.StringProperty(default='http://search.twitter.com/')

    twitpic_api_key = db.StringProperty(default='')

def set_app_config(
    consumer_key=None,
    consumer_secret=None, 
    request_token_url=None,
    access_token_url=None,
    authorize_url=None,
    authenticate_url=None,
    api_url=None,
    search_api_url=None,
    twitpic_api_key=None,
):
    global _app_config_cache
    params={'key_name':'app_config'}
    if consumer_key:
        params['consumer_key'] = consumer_key
    if consumer_secret:
        params['consumer_secret'] = consumer_secret
    if request_token_url:
        params['request_token_url'] = request_token_url
    if access_token_url:
        params['access_token_url'] = access_token_url
    if authorize_url:
        params['authorize_url'] = authorize_url
    if authenticate_url:
        params['authenticate_url'] = authenticate_url
    if api_url:
        params['api_url'] = api_url
    if search_api_url:
        params['search_api_url'] = search_api_url
    if twitpic_api_key:
        params['twitpic_api_key'] = twitpic_api_key
    app_config = AppConfig(**params)
    logging.debug('[App Config] Set: %s' % params)
    app_config.put()
    _app_config_cache = app_config
    memcache.set('app_config', app_config)
    return app_config

def get_app_config():
    global _app_config_cache
    if _app_config_cache:
        logging.debug('[MD] hit _app_config_cache %s' % _app_config_cache)
        return _app_config_cache
    app_config = memcache.get('app_config')
    _app_config_cache = app_config
    if not app_config:
        app_config = AppConfig.get_by_key_name('app_config')
        if not app_config:
            return set_app_config()
        _app_config_cache = app_config
        memcache.set('app_config', app_config)
    return app_config



_image_proxy_config_cache=None

class ImageProxyConfig(db.Model):
    flickr_api_key = db.StringProperty(default='')
    flickr_api_secret = db.StringProperty(default='')
    flickr_rest_api_url = db.StringProperty(default='http://api.flickr.com/services/rest/')

def set_image_proxy_config(
    flickr_api_key=None,
    flickr_api_secret=None,
    flickr_rest_api_url=None
):
    global _image_proxy_config_cache
    params={'key_name':'image_proxy_config'}
    if flickr_api_key:
        params['flickr_api_key'] = flickr_api_key
    if flickr_api_secret:
        params['flickr_api_secret'] = flickr_api_secret
    if flickr_rest_api_url:
        params['flickr_rest_api_url'] = flickr_rest_api_url
    image_proxy_config = ImageProxyConfig(**params)
    logging.debug('[ImageProxy Config] Set: %s' % params)
    image_proxy_config.put()
    _image_proxy_config_cache = image_proxy_config
    memcache.set('image_proxy_config', image_proxy_config)
    return image_proxy_config

def get_image_proxy_config():
    global _image_proxy_config_cache
    if _image_proxy_config_cache:
        return _image_proxy_config_cache
    image_proxy_config = memcache.get('image_proxy_config')
    _image_proxy_config_cache = image_proxy_config
    if not image_proxy_config:
        image_proxy_config = ImageProxyConfig.get_by_key_name('image_proxy_config')
        if not image_proxy_config:
            return set_image_proxy_config()
        _image_proxy_config_cache = image_proxy_config
        memcache.set('image_proxy_config', image_proxy_config)
    return image_proxy_config



class PickledProperty(db.Property):
    data_type = db.Blob

    def get_value_for_datastore(self, model_instance):
        value = self.__get__(model_instance, model_instance.__class__)
        if value is not None:
            return db.Blob(pickle.dumps(value))

    def make_value_from_datastore(self, value):
        if value is not None:
            return pickle.loads(str(value))


class TwitdaoUser(db.Model):
    app_user = db.UserProperty(auto_current_user_add=True)
    default_token = db.ReferenceProperty(default=None)

    def __str__(self):
        return str(self.app_user)


_default_token_settings={
    'show_media':True,
    'm_show_avatar':False,
    'm_show_media':False,
    'm_optimizer':None
}

class AccessToken(db.Model):
    #twitdao info
    twitdao_user = db.ReferenceProperty(reference_class=TwitdaoUser, collection_name="access_tokens")
    first_auth_at = db.DateTimeProperty(auto_now_add=True)
    last_auth_at = db.DateTimeProperty(auto_now=True)
    settings = PickledProperty(default=_default_token_settings)
    #access token
    user_id = db.IntegerProperty()
    screen_name = db.StringProperty()
    oauth_token = db.StringProperty()
    oauth_token_secret = db.StringProperty()

    def __str__(self):
        return '(%s, %s, key=%s)' % (self.user_id, self.screen_name, self.key())

class NoUserError(Exception):
    '''Raise when we can't find any user.'''
    pass

def _default_app_user():
    app_user = users.get_current_user()
    if not app_user:
        raise NoUserError('Have you logged in?')
    return app_user

def _app_user_key(app_user=None):
    '''Identifier of the user. '''
    if not app_user:
        app_user = _default_app_user()
    return 'token-%s-%s-%s-%s-%s' % (
        app_user.nickname(),
        app_user.email(),
        app_user.user_id(),
        app_user.federated_identity(),
        app_user.federated_provider()
    )


def set_default_access_token(access_token, app_user=None):
    '''
    设置app_user的默认access token.
    '''
    if not app_user:
        app_user = _default_app_user()
    twitdao_user = TwitdaoUser.all().filter('app_user =', app_user).get()
    twitdao_user.default_token = access_token
    twitdao_user.put()
    
    default_key = _app_user_key(app_user)
    memcache.set( default_key, access_token)
    return access_token


def get_access_tokens(size=50, cursor=None):
    '''
    获取 access tokens.

    返回 token 列表和一个 cursor.
    如果返回的 cursor!=None, 则仍有更多tokens; 如果返回的 cursor==None, 则token已经取尽.
    '''
    q=AccessToken.all()
    if cursor:
        q.with_cursor(cursor)
    tokens=q.fetch(size)
    next_cursor=q.cursor()
    if len(tokens)<size:
        next_cursor = None
    return tokens, next_cursor


def get_user_access_tokens(app_user=None, size=10, cursor=None):
    '''
    获取 app_user 的 access tokens.

    返回 token 列表和一个 cursor.
    如果返回的 cursor!=None, 则仍有更多tokens; 如果返回的 cursor==None, 则token已经取尽.

    如果未指定 app_user 则默认app_user就是当前登录用户。
    '''
    if not app_user:
        app_user = _default_app_user()
    tdu = TwitdaoUser.all().filter('app_user =', app_user).get()

    next_cursor=None
    tokens=None
    if tdu:
        if cursor:
            q=tdu.access_tokens.with_cursor(cursor)
        else:
            q=tdu.access_tokens
        tokens=q.fetch(size)
        next_cursor=q.cursor()
    else:
        return None,None

    if len(tokens)<size:
        next_cursor = None

    return tokens, next_cursor


def get_default_access_token(app_user=None):
    '''
    获取 app_user 的默认 access token.

    如果未指定 app_user 则默认app_user就是当前登录用户。
    '''
    if not app_user:
        app_user = _default_app_user()
    default_key = _app_user_key(app_user)
    token = memcache.get(default_key)
    if not token:
        twitdao_user = TwitdaoUser.all().filter('app_user =', app_user).get()
        if twitdao_user:
            # Try to prevent the "ReferenceProperty failed to be resolved" error.
            try:
                token = twitdao_user.default_token
                if not token: return None
                memcache.set_multi({str(token.key()):token, default_key:token})
            except:
                logging.warning('Exception: %s' % sys.exc_info()[0])
                return None
        else:
            return None
    return token


def get_access_token(token_key=None, app_user=None):
    '''
    获取token_key所代表的access token.

    如果指定了 app_user , 则只取 app_user 的 access token
    否则直接取得 access_token。
    '''
    if app_user:
        token=memcache.get(str(token_key))
        if not token:
            token = AccessToken.get(token_key)
        
        if not token:
            return None
        elif token.twitdao_user.app_user != app_user:
            return None
        else:
            memcache.set(str(token_key),token)
            return token
    else:
        token=memcache.get(str(token_key))
        if not token:
            token = AccessToken.get(token_key)
            if not token: return None
            memcache.set(str(token_key),token)
        return token


def save_access_token(
    user_id,
    screen_name,
    oauth_token,
    oauth_token_secret,
    app_user
):
    tdu = TwitdaoUser.all().filter('app_user =', app_user).get()
    if not tdu:
        tdu = TwitdaoUser()
        tdu.put()

    tk = tdu.access_tokens.filter('user_id =', long(user_id)).get()
    if tk:
        tk.screen_name=screen_name
        tk.oauth_token=oauth_token
        tk.oauth_token_secret=oauth_token_secret
        tk.twitdao_user=tdu
        tk.put()
    else:
        tk = AccessToken(
            app_user = app_user,
            twitdao_user=tdu,
            user_id=long(user_id),
            screen_name=screen_name,
            oauth_token=oauth_token,
            oauth_token_secret=oauth_token_secret
        )
        tk.put()

    # Set the token as default only if default_token is None or the Error is raised.
    try:
        # Try to prevent the "ReferenceProperty failed to be resolved" error.
        if not tdu.default_token:
            tdu.default_token = tk
            tdu.put()
    except:
        logging.warning('Exception: %s' % sys.exc_info()[0])
        tdu.default_token = tk
        tdu.put()

    return tk


def delete_access_token(token_key=None, app_user=None):
    '''
    删除token_key所代表的 access token.

    如果指定了 app_user, 则只删除app_user 的 access token.
    否则直接删除 access token.
    '''
    token = AccessToken.get(token_key)
    if not token:
        return None

    if not app_user:
        memcache.delete_multi(keys=[str(token_key), _app_user_key(token.twitdao_user.app_user)])
        token.delete()
    elif token.twitdao_user.app_user != app_user:
        return None
    else:
        memcache.delete_multi(keys=[str(token_key), _app_user_key(app_user)])
        token.delete()
        return token


def _cleanup_settings(settings):
    if not isinstance(settings, dict):
        return _default_token_settings
    skeys=settings.keys()
    for k in skeys:
        if k not in _default_token_settings:
            del settings[k]
    return settings

def set_token_settings(token_key, app_user=None, **settings):
    token = AccessToken.get(token_key)
    if not token:
        return None

    if not app_user:
        settings=_cleanup_settings(settings)
        old_settings=_cleanup_settings(token.settings)
        old_settings.update(settings)
        token.settings=old_settings
        memcache.delete_multi({str(token_key):token, _app_user_key(token.twitdao_user.app_user):token})
        token.put()
    elif token.twitdao_user.app_user != app_user:
        return None
    else:
        settings=_cleanup_settings(settings)
        old_settings=_cleanup_settings(token.settings)
        old_settings.update(settings)
        token.settings=old_settings
        memcache.delete_multi({str(token_key):token, _app_user_key(app_user):token})
        token.put()

def get_proxy_access_token():
	return get_access_token('agdnYWUtdHVpchILEgtBY2Nlc3NUb2tlbhipRgw','')

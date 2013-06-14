# -*- coding: utf-8 -*-
from google.appengine.api import memcache

from twitter import Twitter
import md

USER_CACHE_TIME = 10*60
TWEET_CACHE_TIME = 60*60

class Twitdao():
    def __init__(self, token=None):
        self.token = token

        config = md.get_app_config()
        
        if token:
            self.twitter = Twitter(
                oauth_token=self.token.oauth_token,
                oauth_token_secret=self.token.oauth_token_secret,
                    
                consumer_key=config.consumer_key,
                consumer_secret=config.consumer_secret,
                request_token_url=config.request_token_url,
                access_token_url=config.access_token_url,
                authorize_url=config.authorize_url,
                authenticate_url=config.authenticate_url,
                api_url=config.api_url,
                search_api_url=config.search_api_url
            )
        else:
            self.twitter = Twitter(                    
                consumer_key=config.consumer_key,
                consumer_secret=config.consumer_secret,
                request_token_url=config.request_token_url,
                access_token_url=config.access_token_url,
                authorize_url=config.authorize_url,
                authenticate_url=config.authenticate_url,
                api_url=config.api_url,
                search_api_url=config.search_api_url
            )

    def fetch_request_token(self, callback=None):
        return self.twitter.fetch_request_token(callback)

    def fetch_access_token(self, verifier):
        access_token = self.twitter.fetch_access_token(verifier)
        return access_token

    def get_authenticate_url(self, request_token, force_login=False):
        return self.twitter.get_authenticate_url(request_token, force_login)

    def get_authorize_url(self, request_token, force_login=False):
        return self.twitter.get_authorize_url(request_token, force_login)

    #==========================================================================
    def _cache_timeline(self, timeline, **params):
        if not 'errors' in timeline:
            trim_user=params['trim_user'] if 'trim_user' in params else None
            include_entities=params['include_entities'] if 'include_entities' in params else None
            td=dict(('%s-%s-%s' % (tweet['id_str'], trim_user, include_entities), tweet) for tweet in timeline)
            return memcache.set_multi(td, time=TWEET_CACHE_TIME, key_prefix="tweet-")
        return False
    
    def _cache_tweet(self, tweet, **params):
        if not 'errors' in tweet:
            trim_user=params['trim_user'] if 'trim_user' in params else None
            include_entities=params['include_entities'] if 'include_entities' in params else None
            return memcache.set( 'tweet-%s-%s-%s' % (tweet['id_str'], trim_user, include_entities), tweet, time=TWEET_CACHE_TIME,)
        return False

    def _get_cached_tweet(self, id, **params):
        trim_user=params['trim_user'] if 'trim_user' in params else None
        include_entities=params['include_entities'] if 'include_entities' in params else None
        return memcache.get( 'tweet-%s-%s-%s' % (id, trim_user, include_entities) )
    
    def _del_cached_tweet(self, id, **params):
        trim_user=params['trim_user'] if 'trim_user' in params else None
        include_entities=params['include_entities'] if 'include_entities' in params else None
        return memcache.delete( 'tweet-%s-%s-%s' % (id, trim_user, include_entities) )

    #好像不好。
    def _cache_users(self, users, **params):
        if not 'errors' in users:
            include_entities = params['include_entities'] if 'include_entities' in params else None
            us=dict(('%s-%s' % (user['id_str'], include_entities), user) for user in users)
            us.update(dict(('%s-%s' % (user['screen_name'], include_entities), user) for user in users))
            return memcache.set_multi(us, key_prefix="user-", time=USER_CACHE_TIME)
        return False

    def _cache_user(self, user, **params):
        if not 'errors' in user:
            include_entities = params['include_entities'] if 'include_entities' in params else None
            return memcache.set_multi({
                ('id-%s-%s' % (user['id_str'], include_entities)):user,
                ('screen_name-%s-%s' % (user['screen_name'], include_entities)):user
            }, key_prefix="user-", time=USER_CACHE_TIME)
        return False

    def _get_cached_user_by_id(self, id, **params):
        include_entities = params['include_entities'] if 'include_entities' in params else None
        return memcache.get('user-id-%s-%s' % (id, include_entities))

    def _get_cached_user_by_screen_name(self, screen_name, **params):
        include_entities = params['include_entities'] if 'include_entities' in params else None
        return memcache.get('user-screen_name-%s-%s' % (screen_name, include_entities))

    #删不全啊。
    def _del_cached_user_by_id(self, id, **params):
        include_entities = params['include_entities'] if 'include_entities' in params else None
        return memcache.delete('user-id-%s-%s' % (id, include_entities))

    def _del_cached_user_by_screen_name(self, screen_name, **params):
        include_entities = params['include_entities'] if 'include_entities' in params else None
        return memcache.delete('user-screen_name-%s-%s' % (screen_name, include_entities))

    def public_timeline(self, **params):
        #trim_user, include_entities
        timeline = self.twitter.api_call('GET','statuses/sample', params)
        return timeline

    def home_timeline(self, **params):
        #since_id, max_id, count, page, trim_user, include_rts, include_entities
        timeline = self.twitter.api_call('GET','statuses/home_timeline', params)
        self._cache_timeline(timeline, **params)
        return timeline

    def friends_timeline(self, **params):
        #since_id, max_id, count, page, trim_user, include_rts, include_entities
        timeline = self.twitter.api_call('GET','statuses/friends_timeline', params)
        self._cache_timeline(timeline, **params)
        return timeline

    def user_timeline(self, **params):
        #user_id, screen_name, since_id, max_id, count, page, trim_user, include_rts, include_entities
        timeline = self.twitter.api_call('GET','statuses/user_timeline', params)
        self._cache_timeline(timeline, **params)
        return timeline

    def mentions(self, **params):
        #since_id, max_id, count, page, trim_user, include_rts, include_entities
        timeline = self.twitter.api_call('GET','statuses/mentions_timeline', params)
        self._cache_timeline(timeline, **params)
        return timeline

    def retweeted_by_me(self, **params):
        #since_id, max_id, count, page, trim_user, include_entities
        timeline = self.twitter.api_call('GET','statuses/retweeted_by_me', params)
        self._cache_timeline(timeline, **params)
        return timeline

    def retweeted_to_me(self, **params):
        #since_id, max_id, count, page, trim_user, include_entities
        timeline = self.twitter.api_call('GET','statuses/retweeted_to_me', params)
        self._cache_timeline(timeline, **params)
        return timeline

    def retweets_of_me(self, **params):
        #since_id, max_id, count, page, trim_user, include_entities
        timeline = self.twitter.api_call('GET','statuses/retweets_of_me', params)
        self._cache_timeline(timeline, **params)
        return timeline

    # Tweets Resources
    def statuses_show(self, id, **params):
        #trim_user, include_entities
        tweet = self._get_cached_tweet(id, **params)
        if not tweet:
            tweet = self.twitter.api_call('GET', 'statuses/show/%s' % id, params)
            self._cache_tweet(tweet, **params)
        return tweet

    def statuses_update(self, status, **params):
        #in_reply_to_status_id, lat, long, place_id, display_coordinates, trim_user, include_entities
        pms={'status':status}
        pms.update(params)
        tweet = self.twitter.api_call('POST', 'statuses/update', pms)
        return tweet

    def statuses_destroy(self, id, **params):
        #trim_user, include_entities
        tweet = self.twitter.api_call('POST', 'statuses/destroy/%s' % id, params)
        self._del_cached_tweet(id, **params)
        return tweet

    def statuses_retweet(self, id, **params):
        #trim_user, include_entities
        tweet = self.twitter.api_call('POST', 'statuses/retweet/%s' % id, params)
        return tweet

    def statuses_retweets(self, id, **params):
        #count, trim_user, include_entities
        tweets = self.twitter.api_call('GET', 'statuses/retweets/%s' % id, params)
        return tweets

    def statuses_retweeted_by(self, id, **params):
        #count, page, trim_user, include_entities
        users = self.twitter.api_call('GET', 'statuses/%s/retweeted_by' % id, params)
        return users

    def statuses_retweeted_by_ids(self, id, **params):
        #count, page, trim_user, include_entities
        ids = self.twitter.api_call('GET', 'statuses/%s/retweeted_by/ids' % id, params)
        return ids

    #User resources
    #users_show
    def users_show_by_id(self, user_id, **params):
        user=None
        _tdfr=False
        if '_twitdao_force_refresh' in params:
            _tdfr=params['_twitdao_force_refresh']
            del params['_twitdao_force_refresh']
        if not _tdfr:
            user=self._get_cached_user_by_id(user_id, **params)
        if not user:
            params.update({'user_id':user_id})
            user = self.twitter.api_call('GET', 'users/show', params)
            self._cache_user(user, **params)
        return user

    #users_show
    def users_show_by_screen_name(self, screen_name, **params):
        user=None
        _tdfr=False
        if '_twitdao_force_refresh' in params:
            _tdfr=params['_twitdao_force_refresh']
            del params['_twitdao_force_refresh']
        if not _tdfr:
            user=self._get_cached_user_by_screen_name(screen_name, **params)
        if not user:
            params.update({'screen_name':screen_name})
            user = self.twitter.api_call('GET', 'users/show', params)
            self._cache_user(user, **params)
        return user

    def users_lookup(self, user_id=None, screen_name=None, **params):
        #include_entities
        pms={}
        if user_id:
            pms = {'user_id':user_id}
        elif screen_name:
            pms ={'screen_name':screen_name}
        pms.update(params)
        users = self.twitter.api_call('POST', 'users/lookup', pms)
        return users

    def users_search(self, q, **params):
        #per_page, page, include_entities
        pms = {'q':q}
        pms.update(params)
        users = self.twitter.api_call('GET', 'users/search', pms)
        return users

    def users_suggestions(self):
        sugs = self.twitter.api_call('GET', 'users/suggestions')
        return sugs

    def users_suggestions_slug(self, slug):
        sugs = self.twitter.api_call('GET', 'users/suggestions/%s' % slug)
        return sugs

    def users_profile_image(self, screen_name, **params):
        #size
        url = self.twitter.api_call('GET', 'users/profile_image/%s' % screen_name, params)
        return url

    def statuses_friends(self, **params):
        #user_id, screen_name, cursor, include_entities
        friends = self.twitter.api_call('GET', 'friends/list', params)
        return friends

    def statuses_followers(self, **params):
        #user_id, screen_name, cursor, include_entities
        followers = self.twitter.api_call('GET', 'followers/list', params)
        return followers

    #List Resources
    def user_lists_post(self, name, **params):
        '''Creates a new list for the authenticated user. Accounts are limited to 20 lists.'''
        #mode, description
        pms = {'name':name}
        pms.update(params)
        ls = self.twitter.api_call('POST', '%s/lists' % self.token.screen_name, pms)
        return ls

    def user_lists_id_post(self, id, **params):
        '''Updates the specified list.
        #name, mode, description'''
        ls = self.twitter.api_call('POST', '%s/lists/%s' % (self.token.screen_name, id), params)
        return ls

    def user_lists_get(self, screen_name=None, **params):
        '''List the lists of the specified user. Private lists will be included if the authenticated users
        is the same as the user who's lists are being returned.'''
        #cursor
        if not screen_name:
            screen_name = self.token.screen_name
        lists = self.twitter.api_call('GET', '%s/lists' % screen_name, params)
        return lists

    def user_list_id_get(self, id, screen_name=None):
        '''Show the specified list. Private lists will only be shown if the authenticated user owns the specified list.'''
        if not screen_name:
            screen_name = self.token.screen_name
        ls = self.twitter.api_call('GET', '%s/lists/%s' % (screen_name, id) )
        return ls

    def user_list_id_delete(self, id):
        '''Deletes the specified list. Must be owned by the authenticated user.'''
        ls = self.twitter.api_call('POST', '%s/lists/%s' % (self.token.screen_name, id), {'_method':'DELETE'})
        return ls

    def user_list_id_statuses(self, id, screen_name, **params):
        '''Show tweet timeline for members of the specified list.'''
        #since_id, max_id, per_page, page, include_entities
        ls = self.twitter.api_call('GET', '%s/lists/%s/statuses' % (screen_name, id), params)
        return ls

    def user_list_memberships(self, screen_name, **params):
        '''List the lists the specified user has been added to.'''
        #cursor
        lists = self.twitter.api_call('GET', '%s/lists/memberships' % screen_name, params)
        return lists

    def user_list_subscriptions(self, screen_name, **params):
        '''List the lists the specified user follows.'''
        #cursor
        lists = self.twitter.api_call('GET', '%s/lists/subscriptions' % screen_name, params)
        return lists


    #List Subscribers Resources
    def user_list_id_subscribers_get(self, screen_name, list_id, **params):
        '''Returns the subscribers of the specified list.'''
        #cursor, include_entities
        users = self.twitter.api_call('GET', '%s/%s/subscribers' % (screen_name, list_id), params )
        return users

    def user_list_id_subscribers_post(self, screen_name, list_id):
        '''Make the authenticated user follow the specified list.'''
        return self.twitter.api_call('POST', '%s/%s/subscribers' % (screen_name, list_id) )

    def user_list_id_subscribers_delete(self, screen_name, list_id, **params):
        '''Unsubscribes the authenticated user form the specified list.'''
        params['_method'] = 'DELETE'
        return self.twitter.api_call('POST', '%s/%s/subscribers' % (screen_name, list_id), params )

    def user_list_id_subscribers_id(self, screen_name, list_id, id, **params):
        '''Check if a user is a subscriber of the specified list.'''
        #include_entities
        return self.twitter.api_call('POST', '%s/%s/subscribers/%s' % (screen_name, list_id, id), params )


    #List Members Resources
    def user_list_id_members_get(self, screen_name, list_id, **params):
        ''' Returns the members of the specified list. '''
        #cursor, include_entities
        return self.twitter.api_call('GET', '%s/%s/members' % (screen_name, list_id), params )

    def user_list_id_members_post(self, screen_name, list_id, id):
        '''Add a member to a list. The authenticated user must own the list to be able to add members to it. 
        Lists are limited to having 500 members.'''
        params={}
        params['id'] = id
        return self.twitter.api_call('POST', '%s/%s/members' % (screen_name, list_id), params )
    
    def user_list_id_members_create_all(self, screen_name, list_id, **params):
        '''Adds multiple members to a list, by specifying a comma-separated list of member ids or screen names. 
        The authenticated user must own the list to be able to add members to it. Lists are limited to having 500 members, 
        and you are limited to adding up to 100 members to a list at a time with this method.'''
        #screen_name, user_id
        return self.twitter.api_call('POST', '%s/%s/create_all' %(screen_name, list_id) ,params )

    def user_list_id_members_delete(self, screen_name, list_id, id):
        '''Removes the specified member from the list. The authenticated user must be the list's owner to remove members from the list.'''
        params={}
        params['_method'] = 'DELETE'
        params['id'] = id
        return self.twitter.api_call('POST', '%s/%s/members' % (screen_name, list_id), params )

    def user_list_id_members_id(self, screen_name, list_id, id, **params):
        '''Check if a user is a member of the specified list.'''
        #include_entities
        return self.twitter.api_call('GET', '%s/%s/members/%s' % (screen_name, list_id, id), params )


    #Direct Messages Resources
    def direct_messages(self, **params):
        #since_id, max_id, count, page, include_entities
        messages = self.twitter.api_call('GET', 'direct_messages', params)
        return messages
    
    def direct_messages_sent(self, **params):
        #since_id, max_id, count, page, include_entities
        message = self.twitter.api_call('GET', 'direct_messages/sent', params)
        return message

    def direct_messages_new(self, screen_name, user_id, text, **params):
        #include_entities
        pms = {}
        if user_id:
            params['user_id'] = user_id
        elif screen_name:
            params['screen_name'] = screen_name
        params['text'] = text
        pms.update(params)
        message = self.twitter.api_call('POST', 'direct_messages/new', pms)
        return message

    def direct_messages_destroy(self, id, **params):
        #include_entities
        message = self.twitter.api_call('POST', 'direct_messages/destroy/%s' % id, params)
        return message

    #Favorites Resources
    def favorites(self, **params):
        #id, page, include_entities
        favorites = None
        if 'id' in params:
            id = params['id']
            del params['id']
            favorites = self.twitter.api_call('GET', 'favorites/%s' % id, params)
        else:
            favorites = self.twitter.api_call('GET', 'favorites/list', params)
        return favorites

    def favorites_create(self, id, **params):
        #include_entities
        tweet = self.twitter.api_call('POST', 'favorites/create/%s' % id, params)
        return tweet

    def favorites_destroy(self, id, **params):
        #include_entities
        tweet = self.twitter.api_call('POST', 'favorites/destroy/%s' % id, params)
        return tweet


    #Friendship Resources
    def friendships_create(self, **params):
        #user_id, screen_name, follow, include_entities
        user = self.twitter.api_call('POST', 'friendships/create', params)
        return user

    def friendships_destroy(self, **params):
        #user_id, screen_name, include_entities
        user = self.twitter.api_call('POST', 'friendships/destroy', params)
        return user
    
    def friendships_show(self, **params):
        #source_id, source_screen_name, target_id, target_screen_name
        return self.twitter.api_call('GET', 'friendships/show', params)


    #Account Resources
    def account_verify_credentials(self, **params):
        #include_entities
        return self.twitter.api_call('GET', 'account/verify_credentials', params)

    def account_rate_limit_status(self):
        return self.twitter.api_call('GET', 'account/rate_limit_status')

    def account_update_delivery_device(self, device, **params):
        #device(sms, none), include_entities
        return self.twitter.api_call('POST', 'account/update_delivery_device', params)

    def account_update_profile_colors(self, **params):
        #profile_background_color, profile_text_color, profile_link_color, profile_sidebar_fill_color, profile_sidebar_border_color, include_entities 
        return self.twitter.api_call('POST', 'account/update_profile_colors', params)

    def account_update_profile_image(self, image, **params):
        #include_entities
        #image-> ('param_name', file_name, image_content)        
        return self.twitter.api_call('POST', 'account/update_profile_image', params, [image])

    def account_update_profile_background_image(self, image, **params):
        #tile, include_entities
        #image-> ('param_name', file_name, image_content)
        return self.twitter.api_call('POST', 'account/update_profile_background_image', params, [image])

    def account_update_profile(self, **params):
        #name, url, location, description, include_entities
        return self.twitter.api_call('POST', 'account/update_profile', params)


    #Block Resources
    def blocks_create(self, **params):
        #user_id, screen_name, include_entities
        user = self.twitter.api_call('POST', 'blocks/create', params)
        return user
    
    def blocks_destroy(self, **params):
        #user_id, screen_name, include_entities
        user = self.twitter.api_call('POST', 'blocks/destroy', params)
        return user
    
    def blocks_blocking(self, **params):
        #page, include_entities
        blocking = self.twitter.api_call('GET', 'blocks/list', params)
        return blocking#user list

    #Spam Reporting resources
    def report_spam(self, **params):
        #user_id, screen_name, include_entities
        user = self.twitter.api_call('POST', 'users/report_spam', params)
        return user
    
    #Saved Searches Resources
    def saved_searches(self):
        return self.twitter.api_call('GET','saved_searches/list')

    def API_limit_rate(self):
        return self.twitter.api_call('GET','account/rate_limit_status')

    def saved_searches_show(self, id):
        return self.twitter.api_call('GET','saved_searches/show/%s' % id)

    def saved_searches_create(self, **params):
        #query
        return self.twitter.api_call('POST','saved_searches/create/%s', params)
    
    def saved_searches_destroy(self, id):
        return self.twitter.api_call('POST','saved_searches/destroy/%s' % id)

    #Search API
    def search(self, q, **params):
        #lang, locate, rpp, page, since_id, until, geocode, show_user, result_type
        timeline = self.twitter.search_api_call(q, **params)
        return timeline

    #Hacked Search
    def hacked_search(self, q, since_id=None, page=None):
        return self.twitter.hacked_search(q, since_id, page)

    #Hacked 
    def hacked_following_followers_of(self, user_id):
        # Also followed by.
        return self.twitter.hacked_following_followers_of(user_id)

    def hacked_follows_in_common_with(self, user_id):
        # You both follow.
        return self.twitter.hacked_follows_in_common_with(user_id)


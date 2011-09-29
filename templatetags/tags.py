from google.appengine.ext import webapp
register = webapp.template.create_template_register()

from django.template import Node
from django.template import TemplateSyntaxError, VariableDoesNotExist, Variable

from datetime import datetime

import rfc822

@register.tag
def tweet_stats(parser, token):
    try:
        tag_name, tweet_count, created_at=token.split_contents()
    except ValueError, e:
        raise TemplateSyntaxError(e)
    return TweetStatsNode(tweet_count, created_at)

class TweetStatsNode(Node):
    def __init__(self, tweet_count, created_at):
        self.tweet_count=Variable(tweet_count)
        self.created_at=Variable(created_at)
    def render(self, context):
        try:
            tweet_count=self.tweet_count.resolve(context)
            created_at=self.created_at.resolve(context)
            tc=float(tweet_count)
            ca=datetime(*rfc822.parsedate(created_at)[0:6])
            ts=tc/(datetime.now()-ca).days
        except:
            return 'NaN'
        return '%9.2f' % ts

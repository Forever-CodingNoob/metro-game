import random,os
from scripts import getREDISurl
import redis
from datetime import timedelta
import pytz
class Config:
    SECRET_KEY="".join([chr(random.randint(32,126)) for i in range(10)])

    '''flask session'''
    REDIS_URI = getREDISurl()
    SESSION_TYPE = 'redis'
    SESSION_REDIS = redis.from_url(REDIS_URI)
    PERMANENT_SESSION_LIFETIME = timedelta(hours=12)
    SESSION_KEY_PREFIX = 'metro-game:'

    '''timezone'''
    TIMEZONE = pytz.timezone('Asia/Taipei')

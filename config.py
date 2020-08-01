import random,os
from scripts import getREDISurl
import redis
class Config:
    SECRET_KEY="".join([chr(random.randint(32,126)) for i in range(10)])

    '''flask session'''
    REDIS_URI = getREDISurl()
    SESSION_TYPE = 'redis'
    SESSION_REDIS = redis.from_url(REDIS_URI)

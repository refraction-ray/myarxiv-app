from werkzeug.contrib.cache import RedisCache
from .conf import conf

cache = RedisCache(host=conf['REDIS_CACHE_HOST'], port=conf['REDIS_CACHE_PORT'],
                   password=conf['REDIS_CACHE_PASSWORD'] or None, db=conf['REDIS_CACHE_DB'],
                   default_timeout=conf['REDIS_CACHE_TIMEOUT'], key_prefix=conf['REDIS_CACHE_PREFIX'])

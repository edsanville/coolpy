from typing import *
import sqlite3
import os
import pickle
import datetime
import logging
from pathlib import Path

F = TypeVar("F", bound=Callable[..., Any])

log = logging.getLogger('cached_function')


def cached_function(func: F, name: str | None=None, days=28.0) -> F:
    if name is None:
        name = func.__name__
        if hasattr(func, '__module__'):
            name = func.__module__ + '.' + name

    seconds = int(days * 24 * 60 * 60)

    db_path = os.path.expanduser(f'~/.cache/{name}-cache.sqlite')

    cache = sqlite3.connect(db_path)
    cache.execute('create table if not exists cache (args blob, kwargs blob, return_value blob, timestamp integer, unique(args, kwargs))')
    cache.execute('create index if not exists cache_args on cache(args)')
    cache.execute('create index if not exists cache_timestamp on cache(timestamp)')
    cache.execute('create index if not exists cache_kwargs on cache(kwargs)')

    cache.execute('delete from cache where timestamp < ?', (datetime.datetime.now().timestamp() - seconds, ))
    cache.commit()

    def cached_func(*args, **kwargs):
        log.debug(f'Checking cache for {name} with args={args} kwargs={kwargs}')

        row = cache.execute('select return_value, timestamp from cache where args is ? and kwargs is ?', (pickle.dumps(args), pickle.dumps(kwargs))).fetchone()
        cache.commit()

        now_timestamp = int(datetime.datetime.now().timestamp())

        if row is not None:
            return_value, timestamp = row
            if timestamp > now_timestamp - seconds:
                log.debug('Cache hit!')
                return pickle.loads(return_value)
            else:
                log.debug(f'Too old: {timestamp} < {datetime.datetime.now().timestamp()} - {seconds}')
        else:
            log.debug('Cache miss')

        return_value = func(*args, **kwargs)

        cache.execute('insert or replace into cache (args, kwargs, return_value, timestamp) values (?, ?, ?, ?)', (pickle.dumps(args), pickle.dumps(kwargs), pickle.dumps(return_value), now_timestamp))
        cache.commit()

        return return_value

    cached_func = cast(F, cached_func)

    return cached_func


def is_cache_hit(func: F, name: str | None=None, days=28.0) -> Callable[..., bool]:
    if name is None:
        name = func.__name__
        if hasattr(func, '__module__'):
            name = func.__module__ + '.' + name

    log.debug(f'Using name: "{name}"')

    seconds = int(days * 24 * 60 * 60)

    db_path = os.path.expanduser(f'~/.cache/{name}-cache.sqlite')
    cache = sqlite3.connect(db_path)
    cache.execute('create table if not exists cache (args blob, kwargs blob, return_value blob, timestamp integer, unique(args, kwargs))')
    cache.execute('create index if not exists cache_args on cache(args)')
    cache.execute('create index if not exists cache_timestamp on cache(timestamp)')
    cache.execute('create index if not exists cache_kwargs on cache(kwargs)')

    cache.execute('delete from cache where timestamp < ?', (datetime.datetime.now().timestamp() - seconds, ))
    cache.commit()

    def cached_func(*args, **kwargs):
        log.debug(f'Checking cache for {name} with args={args} kwargs={kwargs}')

        row = cache.execute('select return_value, timestamp from cache where args is ? and kwargs is ?', (pickle.dumps(args), pickle.dumps(kwargs))).fetchone()
        cache.commit()

        now_timestamp = int(datetime.datetime.now().timestamp())

        if row is not None:
            return_value, timestamp = row
            if timestamp > now_timestamp - seconds:
                return True
            else:
                return False
        else:
            return False

    cached_func = cast(F, cached_func)

    return cached_func


if __name__ == '__main__':
    import requests

    logging.basicConfig(level=logging.DEBUG)
    get = cached_function(requests.get)

    response = get('https://www.sqlitetutorial.net/sqlite-delete/', headers={'User-Agent': 'Mozilla/5.0 (platform; rv:gecko-version) Gecko/gecko-trail Firefox/firefox-version'})
    
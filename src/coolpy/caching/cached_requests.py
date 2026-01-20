import time
from .cached_function import *
import logging
import requests
from requests import Session
from coolpy.tui import color_text

log = logging.getLogger(__name__)
log.debug(f'Initialized CachedRequests logger {__name__}')

session = requests.Session()

def session_request(*args, **kwargs):
    return session.request(*args, **kwargs)


class CachedRequests:
    expiration_days: float
    throttle_seconds: float

    def __init__(self, expiration_days: float=1, throttle_seconds: float=0.0):
        self.expiration_days = expiration_days
        self.throttle_seconds = throttle_seconds
        self.cached_request = cached_function(session_request, name='cached_requests', days=expiration_days)
        self.is_cache_hit = is_cache_hit(session_request, name='cached_requests', days=expiration_days)


    def request(self, *args, **kwargs):
        is_cache_hit = self.is_cache_hit(*args, **kwargs)
        log.debug(f'Request args: {args}, kwargs: {kwargs}')
        log.debug(color_text(f'Cache hit: {is_cache_hit}', 'green' if is_cache_hit else 'yellow'))
        response = self.cached_request(*args, **kwargs)

        RETRYABLE_STATUS_CODES = {408, 425, 429, 500, 502, 503, 504}
        if is_cache_hit and response.status_code in RETRYABLE_STATUS_CODES:
            log.warning(color_text(f'Retrying request due to status code {response.status_code}', 'yellow'))
            response = session_request(*args, **kwargs)
            log.debug(f'{self.throttle_seconds=}')
            time.sleep(self.throttle_seconds)

        if not is_cache_hit:
            log.debug(f'{self.throttle_seconds=}')
            time.sleep(self.throttle_seconds)

        return response
    

    def get(self, *args, **kwargs):
        return self.request('GET', *args, **kwargs)
    

    def post(self, *args, **kwargs):
        return self.request('POST', *args, **kwargs)
    

    def put(self, *args, **kwargs):
        return self.request('PUT', *args, **kwargs)


if __name__ == '__main__':
    requests = CachedRequests(expiration_days=28, throttle_seconds=5)

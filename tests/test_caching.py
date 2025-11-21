#!/usr/bin/env python3
import logging
logging.basicConfig(level=logging.DEBUG)

from coolpy.caching import CachedRequests

def test_cached_requests():
    cached_requests = CachedRequests(expiration_days=1, throttle_seconds=0.1)

    url = 'https://httpbin.org/get'
    params = {'test': 'cached_requests'}

    # First request should not be a cache hit
    response1 = cached_requests.get(url, params=params)

    # Second request should be a cache hit
    response2 = cached_requests.get(url, params=params)

    # Responses should be the same
    assert response2.status_code == response1.status_code
    assert response1.text == response2.text


def test_function_caching():
    import time
    from coolpy.caching import cached_function, is_cache_hit

    def slow_add(a: float, b: float) -> float:
        time.sleep(2)
        return a + b
    
    fast_add = cached_function(slow_add)

    is_hit = is_cache_hit(slow_add)

    result1 = fast_add(1, 2)
    assert result1 == 3

    # Second call should be a cache hit
    assert is_hit(1, 2)
    result2 = fast_add(1, 2)
    assert result2 == 3


if __name__ == '__main__':
    test_cached_requests()
    test_function_caching()

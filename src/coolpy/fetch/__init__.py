import requests
from typing import Dict


def fetch(url: str, options: Dict[str, any]={}) -> requests.Response:
    """Fetch a url with JS-like syntax.

    Args:
        url (str): URL to fetch
        options (Dict[str, any]): Fetch options, including method, headers, and body.

    Returns:
        _type_: _description_
    """
    return requests.request(method=options.get('method', 'GET'), 
        url=url,
        headers=options.get('headers', {}),
        data=options.get('body', None)
        )

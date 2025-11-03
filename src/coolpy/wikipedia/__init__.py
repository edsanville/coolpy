import requests
from dataclasses import dataclass


class Wikipedia:
    """A simple Wikipedia API wrapper."""

    API_URL = "https://en.wikipedia.org/w/api.php"
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }

    @staticmethod
    def query(params: dict) -> dict:
        """Query wikipedia.

        Args:

            params (dict): The parameters for the Wikipedia API.

        Returns:
            dict: The JSON response from the Wikipedia API.
        """
        response = requests.get(Wikipedia.API_URL, params=params, headers=Wikipedia.HEADERS)
        response.raise_for_status()
        return response.json()

    @staticmethod
    def query_list(eititle: str, einamespace: int) -> list[dict]:
        """Query the embeddedin list for a given title and namespace.

        Args:
            eititle (str): The title to query.
            einamespace (int): The namespace to query.

        Returns:
            list[dict]: A list of pages that use the specified template.
        """
        params = {
            "action": "query",
            "list": "embeddedin",
            "eititle": eititle,
            "format": "json",
            "eilimit": 500,
            "einamespace": einamespace
        }

        items: list[dict] = []
        while True:
            response = Wikipedia.query(params)
            items.extend(response.get("query", {}).get("embeddedin", []))

            if "continue" not in response:
                break

            params.update(response["continue"])

        return items
    
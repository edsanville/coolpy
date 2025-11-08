import requests


class Wikipedia:
    """A simple Wikipedia API wrapper."""

    API_URL = "https://en.wikipedia.org/w/api.php"
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    session = requests.Session()

    @staticmethod
    def query(params: dict) -> dict:
        """Query wikipedia.

        Args:

            params (dict): The parameters for the Wikipedia API.

        Returns:
            dict: The JSON response from the Wikipedia API.
        """
        response = Wikipedia.session.get(Wikipedia.API_URL, params=params, headers=Wikipedia.HEADERS)
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
    
    @staticmethod
    def get_language_links(title: str, namespace: int=0) -> dict[str, str]:
        """Get the language links for a given page title.

        Args:
            title (str): The title of the page.
            namespace (int, optional): The namespace of the page. Defaults to 0.

        Returns:
            dict[str, str]: A dictionary mapping language codes to their corresponding titles.
        """
        params = {
            "action": "query",
            "prop": "langlinks",
            "lllimit": "max",
            "llprop": "url",
            "format": "json",
            "titles": title,
            "namespace": namespace
        }

        wikilinks: dict[str, str] = {
            'en': f"https://en.wikipedia.org/wiki/{title.replace(' ', '_')}"
        }
        while True:
            response = Wikipedia.query(params)
            langlinks = response["query"]["pages"].popitem()[1].get("langlinks", [])
            wikilinks.update({link["lang"]: link["url"] for link in langlinks})

            if "continue" not in response:
                break

            params.update(response["continue"])

        return wikilinks


    @staticmethod
    def get_language_links_titles(title: str, namespace: int=0) -> dict[str, str]:
        """Get the language links for a given page title.

        Args:
            title (str): The title of the page.
            namespace (int, optional): The namespace of the page. Defaults to 0.

        Returns:
            dict[str, str]: A dictionary mapping language codes to their corresponding titles.
        """

        wikilink_urls = Wikipedia.get_language_links(title, namespace)

        return { lang: url.split("/")[-1] for lang, url in wikilink_urls.items() }

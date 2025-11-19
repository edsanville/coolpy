from coolpy.caching import CachedRequests
import json
import logging
import PIL.Image
from PIL.Image import Image

l = logging.getLogger(__name__)

class Wikipedia:
    """A simple Wikipedia API wrapper."""

    API_URL = "https://en.wikipedia.org/w/api.php"
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    session = CachedRequests(expiration_days=30, throttle_seconds=0.05)

    @staticmethod
    def query(params: dict) -> dict:
        """Query wikipedia.

        Args:

            params (dict): The parameters for the Wikipedia API.

        Returns:
            dict: The JSON response from the Wikipedia API.
        """
        sorted_params = dict(sorted(params.items()))
        sorted_headers = dict(sorted(Wikipedia.HEADERS.items()))
        response = Wikipedia.session.get(Wikipedia.API_URL, params=sorted_params, headers=sorted_headers)
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
    def get_language_links(title: str, language_isos: set[str] | None=None) -> dict[str, str]:
        """Get the language links for a given page title.

        Args:
            title (str): The title of the page.
            language_isos (set[str] | None): A set of language ISO codes to filter the results. If None, all languages are returned.

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
        }

        wikilinks: dict[str, str] = {
            'en': f"https://en.wikipedia.org/wiki/{title.replace(' ', '_')}"
        }
        while True:
            response = Wikipedia.query(params)
            langlinks = response["query"]["pages"].popitem()[1].get("langlinks", [])

            for link in langlinks:
                if language_isos is not None and link['lang'] not in language_isos:
                    continue
                wikilinks[link["lang"]] = link["url"]

            if "continue" not in response:
                break

            params.update(response["continue"])

        return wikilinks


    @staticmethod
    def get_language_links_titles(title: str, language_isos: set[str] | None=None) -> dict[str, str]:
        """Get the language links for a given page title.

        Args:
            title (str): The title of the page.

        Returns:
            dict[str, str]: A dictionary mapping language codes to their corresponding titles.
        """

        wikilink_urls = Wikipedia.get_language_links(title, language_isos)
        titles: dict[str, str] = {}
        for lang, url in wikilink_urls.items():
            components = url.split("wiki/")
            assert len(components) == 2, f"Unexpected URL format: {url}"
            titles[lang] = components[1]

        return titles


    @staticmethod
    def get_wikicode(title: str) -> str:
        """Get the wikicode for a given page title.

        Args:
            title (str): The title of the page.
        """

        params = {
            "action": "query",
            "prop": "revisions",
            "rvprop": "content",
            "format": "json",
            "titles": title,
        }

        response = Wikipedia.query(params)
        page = response["query"]["pages"].popitem()[1]
        content: str = page["revisions"][0]["*"]
        return content


    @staticmethod
    def get_lead_image_url(title: str) -> str:
        """Get the lead image URL for a given page title.

        Args:
            title (str): The title of the page.
        """
        params = {
            "action": "query",
            "prop": "pageimages",
            "piprop": "original",
            "format": "json",
            "titles": title,

            "pithumbsize": 500
        }

        response = Wikipedia.query(params)
        url: str = response["query"]["pages"].popitem()[1]["original"]["source"]
        return url        


    @staticmethod
    def get_pil_image(image_url: str, size: tuple[int, int] | None=None) -> Image:
        """Get the image data for a given image title.

        Args:
            image_title (str): The title of the image.
            size (tuple[int, int] | None): The desired size of the image. If None, the original size is returned.
        """
        from io import BytesIO

        response = Wikipedia.session.get(image_url, headers=Wikipedia.HEADERS)
        response.raise_for_status()
        data: bytes = response.content
        image: Image = PIL.Image.open(BytesIO(data)).convert('RGB')

        if size is not None:
            ratio = max(size[0] / image.size[0], size[1] / image.size[1])
            targetSize = (int(image.size[0] * ratio), int(image.size[1] * ratio))
            image = image.resize(targetSize)
        
        return image
    

    @staticmethod
    def get_lead_image_pil(title: str, size: tuple[int, int] | None=None) -> Image:
        """Get the lead image for a given page title.

        Args:
            title (str): The title of the page.
        """
        image_url = Wikipedia.get_lead_image_url(title)
        image = Wikipedia.get_pil_image(image_url, size)
        return image

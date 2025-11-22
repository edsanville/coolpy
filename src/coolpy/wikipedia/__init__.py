from coolpy.caching import CachedRequests
import json
import logging
import PIL.Image
from PIL.Image import Image

logging.basicConfig()
l = logging.getLogger(__name__)

class Wikipedia:
    """A simple Wikipedia API wrapper."""

    API_URL = "https://en.wikipedia.org/w/api.php"
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    session: CachedRequests = None

    def __init__(self, expiration_days: int = 30, throttle_seconds: float = 0.05):
        self.session = CachedRequests(expiration_days=expiration_days, throttle_seconds=throttle_seconds)

    def query(self, params: dict) -> dict:
        """Query wikipedia.

        Args:

            params (dict): The parameters for the Wikipedia API.

        Returns:
            dict: The JSON response from the Wikipedia API.
        """
        sorted_params = dict(sorted(params.items()))
        sorted_headers = dict(sorted(Wikipedia.HEADERS.items()))
        response = self.session.get(Wikipedia.API_URL, params=sorted_params, headers=sorted_headers)
        response.raise_for_status()
        return response.json()

    def query_list(self, eititle: str, einamespace: int=0) -> list[dict]:
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
            response = self.query(params)
            items.extend(response.get("query", {}).get("embeddedin", []))

            if "continue" not in response:
                break

            params.update(response["continue"])

        return items

    def get_language_links(self, title: str | list[str], language_isos: set[str] | None=None) -> dict[str, str] | dict[str, dict[str, str]]:
        """Get the language links for a given page title.

        Args:
            title (str | list[str]): The title(s) of the page(s).
            language_isos (set[str] | None): A set of language ISO codes to filter the results. If None, all languages are returned.

        Returns:
            dict[str, dict[str, str]]] | dict[str, str]: A dictionary mapping `results[title][lang]` or `results[lang]` to their corresponding URLs, depending on whether a single title or a list of titles was provided.
        """

        if isinstance(title, str):
            titles = [title]

        params = {
            "action": "query",
            "prop": "langlinks",
            "lllimit": "max",
            "llprop": "url",
            "format": "json",
            "titles": '|'.join(titles),
        }

        results: dict[str, dict[str, str]] = {}

        while True:
            response = self.query(params)

            for page in response["query"]["pages"].values():

                wikilinks = results.setdefault(page['title'], {
                    'en': f"https://en.wikipedia.org/wiki/{page['title'].replace(' ', '_')}"
                })

                langlinks = page.get("langlinks", [])
                # l.error(color_text(str(langlinks), 'red'))
                for link in langlinks:
                    if language_isos is not None and link['lang'] not in language_isos:
                        continue
                    wikilinks[link["lang"]] = link["url"]

            if "continue" not in response:
                break

            params['llcontinue'] = response["continue"]["llcontinue"]

        if isinstance(title, str):
            return results[title]
        else:
            return results
    

    def get_language_links_titles(self, title: str, language_isos: set[str] | None=None) -> dict[str, str]:
        """Get the language links for a given page title.

        Args:
            title (str): The title of the page.

        Returns:
            dict[str, str]: A dictionary mapping language codes to their corresponding titles.
        """

        wikilink_urls = self.get_language_links(title, language_isos)
        titles: dict[str, str] = {}
        for lang, url in wikilink_urls.items():
            components = url.split("wiki/")
            assert len(components) == 2, f"Unexpected URL format: {url}"
            titles[lang] = components[1]

        return titles


    def get_wikicode(self, title: str) -> str:
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

        response = self.query(params)
        page = response["query"]["pages"].popitem()[1]
        content: str = page["revisions"][0]["*"]
        return content


    def get_lead_image_url(self, title: str) -> str | None:
        """Get the lead image URL for a given page title.

        Args:
            title (str): The title of the page.
        """
        params = {
            "action": "query",
            "prop": "pageimages",
            "piprop": "thumbnail",
            "format": "json",
            "titles": title,

            "pithumbsize": 500
        }

        response = self.query(params)
        pages = response["query"]["pages"].popitem()[1]
        piprop = params['piprop']

        if piprop not in pages:
            return None

        url: str = pages[piprop]["source"]
        return url        


    def get_pil_image(self, image_url: str, size: tuple[int, int] | None=None) -> Image:
        """Get the image data for a given image title.

        Args:
            image_title (str): The title of the image.
            size (tuple[int, int] | None): The desired size of the image. If None, the original size is returned.
        """
        from io import BytesIO
        PIL.Image.MAX_IMAGE_PIXELS = 500_000_000
        
        l.debug(f"Fetching image from URL: {image_url}")
        response = self.session.get(image_url, headers=self.HEADERS)
        response.raise_for_status()
        data: bytes = response.content
        image: Image = PIL.Image.open(BytesIO(data)).convert('RGB')
            

        if size is not None:
            ratio = max(size[0] / image.size[0], size[1] / image.size[1])
            targetSize = (int(image.size[0] * ratio), int(image.size[1] * ratio))
            image = image.resize(targetSize)
        
        return image
    

    def get_lead_image_pil(self, title: str, size: tuple[int, int] | None=None) -> Image | None:
        """Get the lead image for a given page title.

        Args:
            title (str): The title of the page.
        """
        image_url = self.get_lead_image_url(title)

        if image_url is None:
            return None
        
        try:
            image = self.get_pil_image(image_url, size)
        except Exception as e:
            l.info(f"Error getting image from {image_url}: {e}")
            return None
        
        return image

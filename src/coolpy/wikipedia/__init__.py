from urllib.parse import unquote_plus
from coolpy.caching import CachedRequests
import json
import logging
import PIL.Image
from PIL.Image import Image
from typing import overload
from .Wikicode import Wikicode, Template

logging.basicConfig()
l = logging.getLogger(__name__)

BATCH_SIZE = 15

class Wikipedia:
    """A simple Wikipedia API wrapper."""

    API_URL = "https://en.wikipedia.org/w/api.php"
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    session: CachedRequests

    def __init__(self, expiration_days: int = 30, throttle_seconds: float = 1.0):
        self.session = CachedRequests(expiration_days=expiration_days, throttle_seconds=throttle_seconds)
        l.debug(f'Initialized Wikipedia session with expiration_days={expiration_days} and throttle_seconds={throttle_seconds}')

    def query(self, params: dict) -> dict:
        """Query wikipedia.

        Args:

            params (dict): The parameters for the Wikipedia API.

        Returns:
            dict: The JSON response from the Wikipedia API.
        """
        sorted_params = dict(sorted(params.items()))
        sorted_headers = dict(sorted(Wikipedia.HEADERS.items()))
        l.debug(f'Querying {Wikipedia.API_URL} with params: {sorted_params} and headers: {sorted_headers}')
        response = self.session.get(Wikipedia.API_URL, params=sorted_params, headers=sorted_headers)

        if not response.ok:
            l.error(f'Error querying Wikipedia API: {response.status_code} - {response.text}')
            l.error(f'Response Headers: {response.headers}')

        response.raise_for_status()
        results = response.json()
        l.debug(f'Response: {results}...')
        return results
    

    def query_all(self, params: dict, collect_key: str, batch_key: str | None = None) -> list[dict]:
        """Query wikipedia and return all results.

        Args:
            params (dict): The parameters for the Wikipedia API.
            collect_key (str): The key in the response to collect results from.
        """
        items: list[dict] = []

        if batch_key is not None:
            # Batch the params entry, and recursively call this function
            original_value = params[batch_key]
            for start_index in range(0, len(original_value), BATCH_SIZE):
                batch = original_value[start_index:start_index + BATCH_SIZE]
                params[batch_key] = '|'.join(batch)
                results = self.query_all(params, collect_key)
                items.extend(results)
            return items

        while True:
            response = self.query(params)
            results = response.get("query", {})[collect_key]

            if type(results) is dict:
                items.extend(results.values())
            else:
                items.extend(results)

            if "continue" not in response:
                break

            params.update(response["continue"])

        return items


    def get_embeddedin(self, eititle: str, einamespace: int=0) -> list[dict]:
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

        return self.query_all(params, "embeddedin")


    def get_redirects(self, titles: list[str]) -> list[dict]:
        """Get the redirects for a given list of titles.

        Args:
            titles (list[str]): The titles to query.
        Returns:
            list[dict]: A list of redirects for the specified titles.
        """

        params = {
                "action": "query",
                "prop": "redirects",
                "format": "json",
                "rdlimit": "max",
                "titles": titles,
        }

        return self.query_all(params, "pages", batch_key="titles")


    def get_category_members(self, category: str) -> list[dict]:
        """Get the members of a given category.

        Args:
            category (str): The name of the category.

        Returns:
            list[dict]: A list of pages that are members of the specified category.
        """
        params = {
            "action": "query",
            "list": "categorymembers",
            "cmtitle": f"Category:{category}",
            "format": "json",
            "cmlimit": 500,
        }

        return self.query_all(params, "categorymembers")

    @overload
    def get_language_links(self, title: str, language_isos: set[str] | None=None) -> dict[str, str]: ...
    
    @overload
    def get_language_links(self, title: list[str], language_isos: set[str] | None=None) -> dict[str, dict[str, str]]: ...

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
        else:
            titles = title

        results: dict[str, dict[str, str]] = {}

        for start_index in range(0, len(titles), BATCH_SIZE):
            batch = titles[start_index:start_index + BATCH_SIZE]

            params = {
                "action": "query",
                "prop": "langlinks",
                "lllimit": "max",
                "llprop": "url",
                "format": "json",
                "titles": '|'.join(batch),
            }


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
            assert(len(results) == 1)
            return list(results.values())[0]
        else:
            return results
    
    @overload
    def get_language_links_titles(self, title: str, language_isos: set[str] | None=None) -> dict[str, str]: ...

    @overload
    def get_language_links_titles(self, title: list[str], language_isos: set[str] | None=None) -> dict[str, dict[str, str]]: ...

    def get_language_links_titles(self, title: str | list[str], language_isos: set[str] | None=None) -> dict[str, str] | dict[str, dict[str, str]]:
        """Get the language links for a given page title.

        Args:
            title (str | list[str]): The title(s) of the page(s).

        Returns:
            dict[str, str] | dict[str, dict[str, str]]: Either `results[title][lang]` or `results[lang]` depending on whether a single title or a list of titles was provided.
        """

        if isinstance(title, str):
            titles = [title]
        else:
            titles = title

        wikilink_urls: dict[str, dict[str, str]] = self.get_language_links(titles, language_isos)

        def title_from_url(title: str) -> str:
            components = title.split("wiki/")
            assert len(components) == 2, f"Unexpected URL format: {title}"
            return unquote_plus(components[1])


        results = {title: {lang: title_from_url(url) for lang, url in wikilinks.items()} for title, wikilinks in wikilink_urls.items()}

        if isinstance(title, str):
            assert(len(results) == 1)
            return list(results.values())[0]
        else:
            return results


    def get_wikicode(self, title: str) -> Wikicode:
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
        return Wikicode.parse(content)


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

    @staticmethod
    def remove_parentheses(title: str) -> str:
        if title.endswith(')'):
            return title[:title.rfind(' (')]
        return title


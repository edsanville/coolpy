#!/usr/bin/env python3
from pprint import pprint
import logging
logging.basicConfig(level=logging.DEBUG)


from coolpy.wikipedia import Wikipedia


def test_wikipedia():
    wiki = Wikipedia()
    items = wiki.query_list("Template:Starbox_begin", 0)
    assert len(items) > 0
    print(f"Found {len(items)} items.")

    wikilinks_dict = wiki.get_language_links('New Hampshire', language_isos={'en', 'fr', 'de', 'es', 'it', 'ja', 'zh'})
    assert len(wikilinks_dict) > 1
    pprint(wikilinks_dict)

    results = wiki.get_language_links([item['title'] for item in items[:200]], language_isos={'en', 'fr', 'de', 'es', 'it', 'ja', 'zh'})
    # assert len(results) == 2
    # assert 'New Hampshire' in results
    # assert 'Python (programming language)' in results
    # assert len(results['New Hampshire']) > 1
    # assert len(results['Python (programming language)']) > 1
    pprint(results)

    wikilinks = wiki.get_language_links_titles("Python (programming language)", language_isos={'en', 'fr', 'de', 'es', 'it', 'ja', 'zh'})
    assert len(wikilinks) == 7
    print(f"Found {len(wikilinks)} language links.")

    wikilinks = wiki.get_language_links_titles("Python (programming language)")
    assert len(wikilinks) > 0
    print(f"Found {len(wikilinks)} language links.")

    image = wiki.get_lead_image_pil("Halley's Comet", size=(400, 400))
    print(f"Downloaded lead image with size {image.size}.")

if __name__ == "__main__":
    test_wikipedia()

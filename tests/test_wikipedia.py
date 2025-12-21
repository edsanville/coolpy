#!/usr/bin/env python3
from pprint import pprint
import logging
logging.basicConfig(level=logging.INFO)


from coolpy.wikipedia import Wikipedia


def test_wikipedia():
    wiki = Wikipedia()
    items = wiki.get_embeddedin("Template:Starbox_begin")
    assert len(items) > 0
    print(f"Found {len(items)} items.")

    wikilinks_dict = wiki.get_language_links('New Hampshire', language_isos={'en', 'fr', 'de', 'es', 'it', 'ja', 'zh'})
    assert len(wikilinks_dict) > 1
    pprint(wikilinks_dict)

    starbox_article_titles = [item['title'] for item in items[:200]]
    results = wiki.get_language_links(starbox_article_titles, language_isos={'en', 'fr', 'de', 'es', 'it', 'ja', 'zh'})
    # assert len(results) == 2
    # assert 'New Hampshire' in results
    # assert 'Python (programming language)' in results
    # assert len(results['New Hampshire']) > 1
    # assert len(results['Python (programming language)']) > 1
    pprint(results)

    results = wiki.get_language_links_titles(starbox_article_titles, language_isos={'en', 'fr', 'de', 'es', 'it', 'ja', 'zh'})
    assert len(results) == len(starbox_article_titles)

    wikilinks = wiki.get_language_links_titles("Python (programming language)", language_isos={'en', 'fr', 'de', 'es', 'it', 'ja', 'zh'})
    assert len(wikilinks) == 7
    print(f"Found {len(wikilinks)} language links.")

    wikilinks = wiki.get_language_links_titles("Python (programming language)")
    assert len(wikilinks) > 0
    print(f"Found {len(wikilinks)} language links.")

    image = wiki.get_lead_image_pil("Halley's Comet", size=(400, 400))
    print(f"Downloaded lead image with size {image.size}.")

    potential_moons_of_saturn = wiki.get_category_members("Moons of Saturn") + wiki.get_embeddedin('Template:Moons_of_Saturn')
    assert len(potential_moons_of_saturn) > 0
    print(f"Found {len(potential_moons_of_saturn)} category members.")

    planet_articles = wiki.get_embeddedin('Template:Infobox planet')
    assert len(planet_articles) > 0
    print(f"Found {len(planet_articles)} planet articles.")

    saturn_moon_titles = {item['title'] for item in potential_moons_of_saturn}.intersection({item['title'] for item in planet_articles})
    print(f"Found {len(saturn_moon_titles)} Saturn moons that are also planet articles.")

    wikicode = wiki.get_wikicode("Halley's Comet")
    val = wikicode.get_template('Infobox comet').get('aphelion').value.strip_code()
    print(val)

if __name__ == "__main__":
    test_wikipedia()

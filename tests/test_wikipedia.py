#!/usr/bin/env python3
import logging
logging.basicConfig(level=logging.DEBUG)


from coolpy.wikipedia import Wikipedia


def test_wikipedia():
    items = Wikipedia.query_list("Template:Starbox_begin", 0)
    assert len(items) > 0
    print(f"Found {len(items)} items.")

    wikilinks = Wikipedia.get_language_links_titles("Python (programming language)", language_isos={'en', 'fr', 'de', 'es', 'it', 'ja', 'zh'})
    assert len(wikilinks) == 7
    print(f"Found {len(wikilinks)} language links.")

    wikilinks = Wikipedia.get_language_links_titles("Python (programming language)")
    assert len(wikilinks) > 0
    print(f"Found {len(wikilinks)} language links.")

if __name__ == "__main__":
    test_wikipedia()

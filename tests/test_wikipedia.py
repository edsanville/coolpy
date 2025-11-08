#!/usr/bin/env python3
from coolpy.wikipedia import Wikipedia


def test_wikipedia():
    items = Wikipedia.query_list("Template:Starbox_begin", 0)
    assert len(items) > 0
    print(f"Found {len(items)} items.")

    wikilinks = Wikipedia.get_language_links_titles("Python (programming language)", language_isos={'en', 'fr', 'de', 'es', 'it', 'ja', 'zh'})
    assert len(wikilinks) == 7
    for wikilink in wikilinks:
        print(f"{wikilink:5s}: {wikilinks[wikilink]:80.80s}")
    print(f"Found {len(wikilinks)} language links.")

if __name__ == "__main__":
    test_wikipedia()

from coolpy.wikipedia import Wikipedia


def test_wikipedia():
    items = Wikipedia.query_list("Template:Starbox_begin", 0)
    assert len(items) > 0
    print(f"Found {len(items)} items.")

    wikilinks = Wikipedia.get_language_links("Python (programming language)")
    assert len(wikilinks) > 0
    print(wikilinks)
    print(f"Found {len(wikilinks)} language links.")

if __name__ == "__main__":
    test_wikipedia()

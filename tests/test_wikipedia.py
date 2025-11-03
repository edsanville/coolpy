from coolpy.wikipedia import Wikipedia


def test_wikipedia():
    items = Wikipedia.query_list("Template:Starbox_begin", 0)
    assert len(items) > 0
    print(f"Found {len(items)} items.")

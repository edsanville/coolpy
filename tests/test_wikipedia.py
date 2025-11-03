from coolpy.wikipedia import Wikipedia


items = Wikipedia.query_list("Template:Starbox_begin", 0)
print(items)
print(f"Found {len(items)} items.")

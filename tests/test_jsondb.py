import coolpy.jsondb as jsondb
import random


def test_jsondb():
    from dataclasses import dataclass
    import os

    @dataclass
    class InnerClass:
        x: int
        y: str

    @dataclass
    class TestClass:
        index: int
        b: float = None
        c: list[int] = None
        d: dict[str, float] = None
        e: set[str] = None
        f: InnerClass = None

    db_path = "test_db.jsondb"
    if os.path.exists(db_path):
        os.remove(db_path)

    db = jsondb.JsonDB(db_path, TestClass)

    # Test inserting items
    NUM_ITEMS = 10

    with db.transaction():
        for i in range(NUM_ITEMS):
            test = TestClass(
                index=i,
                b=3.14,
                c=[1, 2, i],
                d={"x": 1.0, "y": 2.0},
                e={"foo", "bar"},
                f=InnerClass(x=10, y="test")
            )

            db.insert(test)

    all_items = list(db.load_all())
    assert len(all_items) == NUM_ITEMS

    # Test querying

    query_results = db.query("c", 5)
    assert len(query_results) == 1
    assert 5 in query_results[0].c
    query_results = db.query("d.x", 1.0)
    assert len(query_results) == NUM_ITEMS
    query_results = db.query("e", "foo")
    assert len(query_results) == NUM_ITEMS

    # Test inserting and updating the indices

    with db.transaction():
        db.insert(TestClass(
            index=NUM_ITEMS + 1,
            b=50.5,
            c=[5, 603, 7],
            d={"x": 3.0, "y": 4.0},
            e={"baz"},
            f=InnerClass(x=20, y="example")
        ))

    query_results = db.query("c", 603)
    assert len(query_results) == 1
    assert 603 in query_results[0].c

    # Test replacing an item
    with db.transaction():
        item_to_replace = all_items[0]
        item_to_replace.b = 99.9
        db.replace(item_to_replace, 'index', item_to_replace.index)

    query_results = db.query("index", item_to_replace.index)
    assert len(query_results) == 1
    assert query_results[0].b == 99.9

    # Test upserting an item
    with db.transaction():
        upsert_item = TestClass(
            index=5,
            b=77.7,
            c=[42, 43],
            d={"z": 9.9},
            e={"upsert"},
            f=InnerClass(x=30, y="upserted")
        )

        db.upsert(upsert_item, 'index')

    query_results = db.query("index", upsert_item.index)
    assert len(query_results) == 1
    assert "upsert" in query_results[0].e

    print("JSONDB test passed.")

if __name__ == "__main__":
    test_jsondb()

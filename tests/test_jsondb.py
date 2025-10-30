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
        a: int
        b: float
        c: list[int]
        d: dict[str, float]
        e: set[str]
        f: InnerClass = None

    db_path = "test_db.jsondb"
    if os.path.exists(db_path):
        os.remove(db_path)

    db = jsondb.JsonDB(db_path, TestClass)

    with db.transaction():
        for i in range(10):
            test = TestClass(
                a=42,
                b=random.uniform(0, 100),
                c=[1, 2, random.choice(range(10))],
                d={"x": 1.0, "y": 2.0},
                e={"foo", "bar"},
                f=InnerClass(x=10, y="test")
            )

            db.insert(test)

    all_items = db.load_all()
    assert len(all_items) == 10

    query_results = db.query("c", 5)

    with db.transaction():
        db.insert(TestClass(
            a=100,
            b=50.5,
            c=[5, 6, 7],
            d={"x": 3.0, "y": 4.0},
            e={"baz"},
            f=InnerClass(x=20, y="example")
        ))

    query_results = db.query("c", 5)

    print(query_results)

    print("JSONDB test passed.")

if __name__ == "__main__":
    test_jsondb()

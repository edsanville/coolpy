import coolpy.merge as merge
from dataclasses import dataclass

def test_merge():
    @dataclass
    class TestClass:
        a: int
        b: float
        c: list[int]
        d: dict[str, float]
        e: set[str]

    obj1 = TestClass(
        a=1,
        b=2.0,
        c=[1, 2, 3],
        d={"x": 1.0},
        e={"foo"}
    )

    obj2 = TestClass(
        a=10,
        b=20.0,
        c=[4, 5],
        d={"y": 2.0},
        e={"bar"}
    )

    merged: TestClass = merge.merge(obj1, obj2)

    assert merged.a == 10
    assert merged.b == 20.0
    assert merged.c == [1, 2, 3, 4, 5]
    assert merged.d == {"x": 1.0, "y": 2.0}
    assert merged.e == {"foo", "bar"}

    print("Merge test passed.")

if __name__ == "__main__":
    test_merge()

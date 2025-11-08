import coolpy.coding as coding
from dataclasses import dataclass


def test_coding():

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

    test = TestClass(
        a=42,
        b=3.14,
        c=[1, 2, 3],
        d={"x": 1.0, "y": 2.0},
        e={"foo", "bar"},
        f=InnerClass(x=10, y="test")
    )

    print(coding.encode(test))


if __name__ == "__main__":
    test_coding()


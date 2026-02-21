def add(a: int, b: int) -> int:
    """Return the sum of two integers."""
    if not isinstance(a, int) or not isinstance(b, int):
        raise TypeError("add expects integers")

    print(f"[debug] adding {a} and {b}")
    return a + b


def main() -> None:
    print("add(2, 3) =", add(2, 3))


if __name__ == "__main__":
    main()

def add(a: int, b: int) -> int:
    print(f"[debug] adding {a} and {b}")
    return a + b


def main() -> None:
    print("add(2, 3) =", add(2, 3))


if __name__ == "__main__":
    main()
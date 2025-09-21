def list_reserve[T](arr: list[T], size: int) -> None:
    pass


def int_list(size: int, value: int = 0) -> list[int]:
    return [value] * size


def float_list(size: int, value: float = 0.0) -> list[float]:
    return [value] * size


def str_list(size: int, value: str = "") -> list[str]:
    return [value] * size


def lg[T](lst: list[T], index: int) -> T:
    return lst[index]

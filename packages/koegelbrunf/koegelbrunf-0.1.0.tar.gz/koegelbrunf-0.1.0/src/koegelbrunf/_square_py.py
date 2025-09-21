def square(n: int) -> int:
    """Return n squared.

    Parameters
    ----------
    n : int
        Integer value to square.

    Returns
    -------
    int
        n * n
    """
    if not isinstance(n, int):
        raise TypeError("square expects an int")
    return n * n

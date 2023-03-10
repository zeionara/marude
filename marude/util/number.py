from tasty import pipe


def get_width(number: int):
    return number | pipe | str | pipe | len

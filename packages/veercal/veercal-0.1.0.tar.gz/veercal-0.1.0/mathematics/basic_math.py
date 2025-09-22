def add(a, b):
    """ this is my basic add """
    return a + b


def substract(a, b):
    """this is my basic substraction"""
    return a - b


def divide(a, b):
    if b == 0:
        raise ValueError("this is not allowed, change you b value")
    return a / b


def multiplication(a, b):
    return a * b


if __name__ == "__main__":
    print("This is print from basic math")
    print(add(5, 6))
    print(multiplication(4, 5))

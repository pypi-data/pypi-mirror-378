def add(a, b):
    """this is addition of two numbers"""
    return a + b


def substract(a, b):
    """this is substraction of two numbers"""
    return a - b


def multiply(a, b):
    """this is multiplication of two numbers"""
    return a * b


def divide(a, b):
    """this division of two numbers"""
    if b == 0:
        raise ValueError("can not divide by zero")
    return a / b


def power(a, b):
    """this is power function, a is raised to power of b"""
    return a**b

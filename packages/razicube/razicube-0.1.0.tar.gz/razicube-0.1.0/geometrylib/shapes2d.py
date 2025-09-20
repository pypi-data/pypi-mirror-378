import math
from .utils import validate_positive

class Square:
    @staticmethod
    def area(side):
        validate_positive(side)
        return side ** 2

    @staticmethod
    def perimeter(side):
        validate_positive(side)
        return 4 * side

class Rectangle:
    @staticmethod
    def area(length, width):
        validate_positive(length, width)
        return length * width

    @staticmethod
    def perimeter(length, width):
        validate_positive(length, width)
        return 2 * (length + width)

class Circle:
    @staticmethod
    def area(radius):
        validate_positive(radius)
        return math.pi * radius ** 2

    @staticmethod
    def perimeter(radius):
        validate_positive(radius)
        return 2 * math.pi * radius

class Triangle:
    @staticmethod
    def area(base, height):
        validate_positive(base, height)
        return 0.5 * base * height

    @staticmethod
    def perimeter(a, b, c):
        validate_positive(a, b, c)
        return a + b + c

class IsoscelesTriangle(Triangle):
    @staticmethod
    def perimeter(equal_side, base):
        validate_positive(equal_side, base)
        return 2 * equal_side + base

class EquilateralTriangle(Triangle):
    @staticmethod
    def perimeter(side):
        validate_positive(side)
        return 3 * side

class Parallelogram:
    @staticmethod
    def area(base, height):
        validate_positive(base, height)
        return base * height

    @staticmethod
    def perimeter(base, side):
        validate_positive(base, side)
        return 2 * (base + side)

class Rhombus:
    @staticmethod
    def area(diagonal1, diagonal2):
        validate_positive(diagonal1, diagonal2)
        return 0.5 * diagonal1 * diagonal2

    @staticmethod
    def perimeter(side):
        validate_positive(side)
        return 4 * side

class Trapezoid:
    @staticmethod
    def area(a, b, height):
        validate_positive(a, b, height)
        return 0.5 * (a + b) * height

    @staticmethod
    def perimeter(a, b, c, d):
        validate_positive(a, b, c, d)
        return a + b + c + d

class RegularPolygon:
    @staticmethod
    def area(side, n):
        validate_positive(side, n)
        return (n * side ** 2) / (4 * math.tan(math.pi / n))

    @staticmethod
    def perimeter(side, n):
        validate_positive(side, n)
        return n * side
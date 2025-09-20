import math
from .utils import validate_positive

class Cube:
    @staticmethod
    def surface_area(side):
        validate_positive(side)
        return 6 * side ** 2

    @staticmethod
    def volume(side):
        validate_positive(side)
        return side ** 3

class RectangularPrism:
    @staticmethod
    def surface_area(length, width, height):
        validate_positive(length, width, height)
        return 2 * (length*width + length*height + width*height)

    @staticmethod
    def volume(length, width, height):
        validate_positive(length, width, height)
        return length * width * height

class Cylinder:
    @staticmethod
    def surface_area(radius, height):
        validate_positive(radius, height)
        return 2 * math.pi * radius * (radius + height)

    @staticmethod
    def volume(radius, height):
        validate_positive(radius, height)
        return math.pi * radius ** 2 * height

class Cone:
    @staticmethod
    def surface_area(radius, height):
        validate_positive(radius, height)
        slant = math.sqrt(radius**2 + height**2)
        return math.pi * radius * (radius + slant)

    @staticmethod
    def volume(radius, height):
        validate_positive(radius, height)
        return (1/3) * math.pi * radius ** 2 * height

class Sphere:
    @staticmethod
    def surface_area(radius):
        validate_positive(radius)
        return 4 * math.pi * radius ** 2

    @staticmethod
    def volume(radius):
        validate_positive(radius)
        return 4/3 * math.pi * radius ** 3

class Pyramid:
    @staticmethod
    def surface_area(base_area, perimeter_base, slant_height):
        validate_positive(base_area, perimeter_base, slant_height)
        return base_area + 0.5 * perimeter_base * slant_height

    @staticmethod
    def volume(base_area, height):
        validate_positive(base_area, height)
        return (1/3) * base_area * height

class Prism:
    @staticmethod
    def surface_area(base_area, perimeter_base, height):
        validate_positive(base_area, perimeter_base, height)
        return 2 * base_area + perimeter_base * height

    @staticmethod
    def volume(base_area, height):
        validate_positive(base_area, height)
        return base_area * height
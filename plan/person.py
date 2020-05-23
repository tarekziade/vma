from enum import Enum


class Gender(Enum):
    MAN = 0
    WOMAN = 1


class Person:
    def __init__(self, age, vma, gender=Gender.MAN, max_hr=None):
        self.age = age
        self.vma = vma
        self.gender = gender
        if max_hr is None:
            max_hr = 220 - age
        self.max_hr = max_hr

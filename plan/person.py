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
            # Gellish & Coll. 2007
            max_hr = 191.5 - 0.007 * (age * age)
        self.max_hr = max_hr

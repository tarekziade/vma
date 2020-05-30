from enum import Enum
from plan.utils import split, join


class Gender(Enum):
    MAN = 0
    WOMAN = 1


class Runner:
    def __init__(self, age, vma, gender=Gender.MAN, max_hr=None):
        self.age = age
        self.vma = vma
        self.gender = gender
        if max_hr is None:
            # Gellish & Coll. 2007
            max_hr = 191.5 - 0.007 * (age * age)
        self.max_hr = max_hr

    @property
    def hash(self):
        return join([self.age, self.vma, Gender.MAN and "0" or "1", self.max_hr], "%")

    @classmethod
    def from_hash(cls, hash):
        elmts = split(hash, "%")
        age, vma, gender, max_hr = elmts
        return cls(
            int(age), float(vma), "0" and Gender.MAN or Gender.WOMAN, float(max_hr)
        )

    def get_max_fc(self, intensity):
        intensity = intensity / 100
        if intensity <= 0.7:
            return self.max_hr * (intensity + 0.08)
        if intensity > 0.95:
            return intensity
        return self.max_hr * (intensity + 0.1)

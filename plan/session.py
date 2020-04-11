# encoding: utf8
from enum import Enum


class WeekType(Enum):
    GENERAL = 1
    SPECIFIC = 2

    def __str__(self):
        if self == WeekType.GENERAL:
            return "Préparation générale"
        return "Préparation spécifique"


class SessionType(Enum):
    RECOVERY = 1
    ENDURANCE = 2
    LONG_RUN = 3
    MARATHON = 4
    HALF = 5
    TEN = 6
    FIVE = 7
    EXTENSIVE_INTERVALS = 8
    INTENSIVE_INTERVALS = 9
    SPRINT = 10

    def distance(self):
        if self == SessionType.MARATHON:
            return 42.2
        if self == SessionType.HALF:
            return 21.1
        if self == SessionType.TEN:
            return 10
        if self == SessionType.FIVE:
            return 5
        return -1

    def intensity(self):
        if self == SessionType.MARATHON:
            return (80, 85)
        if self == SessionType.HALF:
            return (85, 90)
        if self == SessionType.TEN:
            return (90, 92)
        if self == SessionType.FIVE:
            return (92, 95)
        return -1

    def __str__(self):
        if self == SessionType.RECOVERY:
            return "Récupération"
        if self == SessionType.ENDURANCE:
            return "Endurance"
        if self == SessionType.LONG_RUN:
            return "Sortie longue"
        if self == SessionType.MARATHON:
            return "Marathon"
        if self == SessionType.HALF:
            return "Semi"
        if self == SessionType.TEN:
            return "10K"
        if self == SessionType.FIVE:
            return "5K"
        if self == SessionType.EXTENSIVE_INTERVALS:
            return "Fractionné extensif"
        if self == SessionType.INTENSIVE_INTERVALS:
            return "Fractionné intensif"
        return "Sprint"

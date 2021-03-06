from enum import Enum


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

    def __int__(self):
        if self == SessionType.RECOVERY:
            return 1
        if self == SessionType.ENDURANCE:
            return 2
        if self == SessionType.LONG_RUN:
            return 3
        if self == SessionType.MARATHON:
            return 4
        if self == SessionType.HALF:
            return 5
        if self == SessionType.TEN:
            return 6
        if self == SessionType.FIVE:
            return 7
        if self == SessionType.EXTENSIVE_INTERVALS:
            return 8
        if self == SessionType.INTENSIVE_INTERVALS:
            return 9
        return 10

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

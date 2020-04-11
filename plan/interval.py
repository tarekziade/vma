# encoding: utf8
import random
from plan.session import SessionType, WeekType


def vma_percent(vma, percent=100):
    return percent / 100 * vma


class Repetition:
    distances = {}
    combo = {}

    def __init__(self, race, name, vma, vmap=None):
        self.name = name
        self.vma = vma
        if vmap is not None:
            self.vma_percent = vmap
        else:
            # going at the race speed
            low, high = race.intensity()
            self.vma_percent = (low + high) / 2
        self.speed = vma_percent(self.vma, self.vma_percent)
        self.recovery_speed = vma_percent(self.vma, 60)
        self.distance = self.distances[name][0]
        self.duration = round(self.distance / self.speed * 3600)

        recovery_coef = self.distances[name][1]
        # coef can be a % of the duration or a duration
        if recovery_coef >= 1.:
            self.recovery_duration = recovery_coef
        else:
            self.recovery_duration = self.duration * recovery_coef

        self.recovery_distance = self.recovery_speed * self.recovery_duration / 3600

    @classmethod
    def pick(cls, race, week_num, vma, week_type, num_week):
        # first, pick a type
        type = random.choice(list(cls.combo[race].keys()))
        # then pick the number of repetitions and vma percent
        picked = cls.combo[race][type]
        if isinstance(picked, tuple):
            repetitions, vmap = picked
        else:
            repetitions = picked
            vmap = None

        # +10% every week
        repetitions *= 1 + 0.05 * week_num

        if week_type == WeekType.GENERAL:
            coef = (0.70, 0.80)
        else:
            coef = (0.60, 0.80)

        print("%s %s %s" % (week_num, week_type, num_week))
        if week_num == num_week:
            # race week, reduce the volume
            repetitions *= coef[0]
        elif week_num == num_week - 1:
            repetitions *= coef[1]

        instance = cls(race, type, vma, vmap)
        return instance, round(repetitions)

    def __str__(self):
        return self.name


class IntensiveRepetition(Repetition):

    distances = {"100M": (0.1, 0.6), "200M": (0.2, 0.6),
                 "300M": (0.3, 0.6)}
    combo = {
        SessionType.FIVE: {"100M": (12, 110), "200M": (8, 105), "300M": (6, 100)},
        SessionType.TEN: {"100M": (14, 110), "200M": (10, 105), "300M": (8, 100)},
        SessionType.HALF: {"100M": (16, 110), "200M": (12, 100), "300M": (8, 95)},
        SessionType.MARATHON: {"100M": (18, 105), "200M": (14, 100), "300M": (10,
            95)},
    }


class ExtensiveRepetition(Repetition):
    distances = {"400M": (0.4, 0.3), "500M": (0.5, 0.3),
                 "600M": (0.6, 0.3), "800M": (0.8, 0.3)}

    combo = {
        SessionType.FIVE: {"400M": (4, 100), "500M": (3, 95), "600M": (2, 90),
            "800M": (2, 90)},
        SessionType.TEN: {"400M": (6, 95), "500M": (5, 95), "600M": (4, 90),
            "800M": (3, 90)},
        SessionType.HALF: {"400M": (8, 95), "500M": (6, 95), "600M": (5, 90),
            "800M": (4, 90)},
        SessionType.MARATHON: {"400M": (10, 95), "500M": (8, 90), "600M": (7,
            85), "800M": (5, 85)},
    }


class SpeRepetition(Repetition):
    distances = {
        "1000M": (1.0, 60),
        "2000M": (2.0, 60),
        "3000M": (3.0, 120),
        "4000M": (4.0, 180),
        "5000M": (5.0, 180),
        "10000M": (10.0, 180),
    }

    combo = {
        SessionType.FIVE: {"1000M": 3, "2000M": 2, "3000M": 1},
        SessionType.TEN: {"1000M": 4, "2000M": 2, "3000M": 2, "4000M": 1},
        SessionType.HALF: {"1000M": 5, "2000M": 3, "3000M": 2, "4000M": 1},
        SessionType.MARATHON: {
            "1000M": 6,
            "2000M": 4,
            "3000M": 2,
            "4000M": 2,
            "5000M": 2,
            "10000M": 1,
        },
    }


def pick_repetition(type, race, week_num, vma, week_type, num_weeks):
    if type == SessionType.INTENSIVE_INTERVALS:
        klass = IntensiveRepetition
    elif type == SessionType.EXTENSIVE_INTERVALS:
        klass = ExtensiveRepetition
    else:
        klass = SpeRepetition
    return klass.pick(race, week_num, vma, week_type, num_weeks)

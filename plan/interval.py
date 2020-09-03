# encoding: utf8
import random

from plan.sessiontype import SessionType
from plan.week import WeekType
from plan.utils import (
    round_duration,
    duration_to_str,
    seconds_to_str,
    speed_to_str,
    join,
    split,
    vma_percent,
)


EASY, NORMAL, HARD = 1, 2, 3


names = [
    "100M",
    "200M",
    "300M",
    "400M",
    "500M",
    "600M",
    "800M",
    "1000M",
    "2000M",
    "3000M",
    "4000M",
    "5000M",
    "10000M",
    "pyramid",
]


def name2code(name):
    return names.index(name)


def code2name(code):
    return names[int(code)]


class Repetition:
    distances = {}
    combo = {}
    type = 0

    def __init__(self, race, name, vma, vmap=None, level=NORMAL, repetitions=1):
        self.name = name
        self.vma = vma
        self.level = level
        if vmap is not None:
            self.vma_percent = vmap
        else:
            # going at the race speed
            low, high = race.intensity()
            self.vma_percent = (low + high) / 2
        self.speed = vma_percent(self.vma, self.vma_percent)
        self.recovery_speed = vma_percent(self.vma, 60)
        self.distance = self.distances[name][0]
        self.duration = round_duration(self.distance / self.speed * 3600)

        recovery_coef = self.distances[name][level]
        # coef can be a % of the duration or a duration
        if recovery_coef >= 1.0:
            self.recovery_duration = recovery_coef
        else:
            self.recovery_duration = self.duration * recovery_coef

        self.recovery_distance = self.recovery_speed * self.recovery_duration / 3600
        self.repetitions = repetitions

    @property
    def hash(self):
        key = join(
            [
                name2code(self.name),
                self.type,
                self.vma_percent,
                self.level,
                self.repetitions,
            ]
        )
        return key

    @classmethod
    def pick(cls, race, week_num, vma, week_type, num_week, level):
        # first, pick a type
        type = random.choice(list(cls.combo[race].keys()))
        # then pick the number of repetitions and vma percent
        picked = cls.combo[race][type]
        if isinstance(picked, tuple):
            repetitions, vmap = picked
        else:
            repetitions = picked
            vmap = None

        # +5, 10, 15% every week
        if level == EASY:
            progression = 0.05
        elif level == NORMAL:
            progression = 0.1
        else:
            progression = 0.15

        repetitions *= 1 + progression * week_num

        if week_type == WeekType.GENERAL:
            coef = (0.70, 0.80)
        else:
            coef = (0.60, 0.80)
        if week_num == num_week:
            # race week, reduce the volume
            repetitions *= coef[0]
        elif week_num == num_week - 1:
            repetitions *= coef[1]

        return cls(race, type, vma, vmap, level, round(repetitions))

    def __str__(self):
        return self.name


class IntensiveRepetition(Repetition):
    # distance is a mapping with:
    # - key: name
    # - value: distance, recovery easy, recovery normal, recovery hard
    # each recovery value is between 0 and 1 (percentage of the interval
    # distance). if it's over 1., it's a time in seconds.
    distances = {
        "100M": (0.1, 0.9, 0.8, 0.7),
        "200M": (0.2, 0.9, 0.8, 0.7),
        "300M": (0.3, 0.9, 0.8, 0.7),
    }
    combo = {
        SessionType.FIVE: {"100M": (12, 110), "200M": (8, 105), "300M": (6, 100)},
        SessionType.TEN: {"100M": (14, 110), "200M": (10, 105), "300M": (8, 100)},
        SessionType.HALF: {"100M": (16, 110), "200M": (12, 100), "300M": (8, 95)},
        SessionType.MARATHON: {"100M": (18, 105), "200M": (14, 100), "300M": (10, 95)},
    }
    type = 1


class VariableIntensiveRepetition(IntensiveRepetition):

    variations = {
        "pyramid": ["100M", "200M", "300M", "300M", "200M", "100M"],
        "downup": ["300M", "200M", "100M", "100M", "200M", "300M"],
    }

    combo = {
        SessionType.FIVE: {"100M": 110, "200M": 105, "300M": 100},
        SessionType.TEN: {"100M": 110, "200M": 105, "300M": 100},
        SessionType.HALF: {"100M": 110, "200M": 100, "300M": 95},
        SessionType.MARATHON: {"100M": 105, "200M": 100, "300M": 95},
    }
    type = 11

    def __init__(self, name, race, steps, vma, level=NORMAL):
        self.race = race
        self.steps = steps
        self.vma = vma
        self.level = level
        self.name = name
        self.recovery_speed = vma_percent(self.vma, 60)
        self.repetitions = 2
        self.between_duration = 2.0
        self.between_duration_distance = 0.1

    @property
    def hash(self):
        return "TODO"

    def step_info(self, step):
        (
            distance,
            speed,
            duration,
            recovery_speed,
            recovery_distance,
            recovery_duration,
        ) = step
        info = "%dM en %s à %skm/h.<br/>Contre-effort de %s à %skm/h." % (
            distance * 1000,
            seconds_to_str(duration),
            speed_to_str(speed),
            seconds_to_str(recovery_duration),
            speed_to_str(recovery_speed),
        )
        return info

    def get_totals(self):
        total_distance = 0
        total_duration = 0
        for step in self.steps:
            (
                distance,
                speed,
                duration,
                recovery_speed,
                recovery_distance,
                recovery_duration,
            ) = step
            total_distance += distance + recovery_distance
            total_duration += duration + recovery_duration

        total_distance = self.repetitions * (
            total_distance + self.between_duration_distance
        )
        total_duration = self.repetitions * (total_duration + self.between_duration)
        return total_distance, total_duration / 60

    @classmethod
    def pick(cls, race, week_num, vma, week_type, num_week, level):
        variation_name = random.choice(list(cls.variations.keys()))
        variation = cls.variations[variation_name]

        steps = []
        for step in variation:
            distance, hard, medium, easy = cls.distances[step]
            vmap = cls.combo[race][step]
            speed = vma_percent(vma, vmap)
            recovery_speed = vma_percent(vma, 60)
            duration = round_duration(distance / speed * 3600)
            if level == EASY:
                recovery_coef = easy
            elif level == NORMAL:
                recovery_coef = medium
            else:
                recovery_coef = hard
            recovery_duration = duration * recovery_coef
            recovery_distance = recovery_speed * recovery_duration / 3600
            steps.append(
                (
                    distance,
                    speed,
                    duration,
                    recovery_speed,
                    recovery_distance,
                    recovery_duration,
                )
            )

        return cls(variation_name, race, steps, vma, level)


class ExtensiveRepetition(Repetition):
    # distance, recovery easy, recovery normal, recovery hard
    distances = {
        "400M": (0.4, 0.8, 0.7, 0.6),
        "500M": (0.5, 0.8, 0.7, 0.6),
        "600M": (0.6, 0.8, 0.7, 0.6),
        "800M": (0.8, 0.8, 0.7, 0.6),
    }

    combo = {
        SessionType.FIVE: {
            "400M": (4, 100),
            "500M": (3, 95),
            "600M": (2, 90),
            "800M": (2, 90),
        },
        SessionType.TEN: {
            "400M": (6, 95),
            "500M": (5, 95),
            "600M": (4, 90),
            "800M": (3, 90),
        },
        SessionType.HALF: {
            "400M": (8, 95),
            "500M": (6, 95),
            "600M": (5, 90),
            "800M": (4, 90),
        },
        SessionType.MARATHON: {
            "400M": (10, 95),
            "500M": (8, 90),
            "600M": (7, 85),
            "800M": (5, 85),
        },
    }
    type = 2


class SpeRepetition(Repetition):
    distances = {
        "1000M": (1.0, 90, 60, 45),
        "2000M": (2.0, 90, 60, 45),
        "3000M": (3.0, 180, 120, 90),
        "4000M": (4.0, 180, 120, 90),
        "5000M": (5.0, 180, 120, 90),
        "10000M": (10.0, 180, 120, 90),
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
    type = 3


def repetition_from_hash(hash, session):
    hash = split(hash)
    name = code2name(hash[0])
    type = int(hash[1])
    vmap = float(hash[2])
    level = int(hash[3])
    repetitions = int(hash[4])
    if type == IntensiveRepetition.type:
        klass = IntensiveRepetition
    elif type == ExtensiveRepetition.type:
        klass = ExtensiveRepetition
    else:
        klass = SpeRepetition
    return klass(
        session.race, name, session.vma, vmap, level, round_duration(repetitions)
    )


def pick_repetition(type, race, week_num, vma, week_type, num_weeks, level):
    if type == SessionType.INTENSIVE_INTERVALS:
        klass = random.choice([IntensiveRepetition] * 4 + [VariableIntensiveRepetition])
    elif type == SessionType.EXTENSIVE_INTERVALS:
        klass = ExtensiveRepetition
    else:
        klass = SpeRepetition
    return klass.pick(race, week_num, vma, week_type, num_weeks, level)


class Interval:
    def __init__(self, session, type):
        self.vma = session.vma
        self.session = session
        self.type = type

        if isinstance(type, VariableIntensiveRepetition):
            self.repetitions = type.repetitions
            self.distance, self.duration = type.get_totals()
        else:
            self.repetitions = type.repetitions
            # split in two
            if self.repetitions > 8:
                repetitions, remainder = divmod(self.repetitions, 2)
                self.repetitions = [repetitions + remainder] * 2
                self.between_duration = 2.0
            else:
                self.between_duration = 0.0
                self.repetitions = (self.repetitions,)

            self.duration = round_duration(
                self.type.duration / 60 * sum(self.repetitions)
                + self.type.recovery_duration / 60 * sum(self.repetitions)
                + self.between_duration / 60
            )
            self.distance = (
                self.type.distance * type.repetitions
                + self.type.recovery_distance * sum(self.repetitions)
            )

    @property
    def hash(self):
        return "I" + join([self.type.hash], ";")

    @classmethod
    def from_hash(cls, hash, session):
        hash = hash[1:]
        hash = split(hash, ";")
        type = repetition_from_hash(hash[0], session)
        return cls(session, type)

    def __str__(self):
        if isinstance(self.type, VariableIntensiveRepetition):
            distances = [step[0] * 1000 for step in self.type.steps]
            if self.type.repetitions == 1:
                r = "-".join("%dM" % distance for distance in distances)
            else:
                r = (
                    "%dx(" % self.type.repetitions
                    + "-".join("%dM" % distance for distance in distances)
                    + ") R=%s" % (duration_to_str(self.type.between_duration))
                )
            info = [self.type.step_info(step) for step in self.type.steps]
            info.append(
                "Durée totale de %s" % duration_to_str(self.type.get_totals()[1])
            )
            info = "<br/>".join(info)
        else:
            if len(self.repetitions) == 1:
                r = "%d x %s" % (self.repetitions[0], self.type)
            else:
                r = "2x(%d x %s) R=%s" % (
                    self.repetitions[0],
                    self.type,
                    duration_to_str(self.between_duration),
                )

            info = (
                "Effort de %s à %skm/h.<br/>Contre-effort de %s à %skm/h.<br/>Durée totale de %s"
                % (
                    seconds_to_str(self.type.duration),
                    speed_to_str(self.type.speed),
                    seconds_to_str(self.type.recovery_duration),
                    speed_to_str(self.type.recovery_speed),
                    duration_to_str(self.duration),
                )
            )

        return """%s <i class="question circle icon" data-variation="mini inverted" data-html="%s"></i>
           """ % (
            r,
            info,
        )

    def json(self):
        return {
            "repetitions": self.repetitions,
            "type": str(self.type),
            "recovery_speed": speed_to_str(self.type.recovery_speed),
            "duration": duration_to_str(self.duration),
            "distance": self.distance,
        }

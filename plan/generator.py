# encoding: utf8
from enum import Enum
import itertools
import datetime as dt

import humanize


class WeekType(Enum):
    GENERAL = 1
    SPECIFIC = 2

    def __str__(self):
        if self == WeekType.GENERAL:
            return "Préparation générale"
        return "Préparation spécifique"


class IntensiveRepetitionType(Enum):
    _30_30 = 1
    _200M = 2
    _300M = 3

    def check_repetitions(self, race, repetitions):
        if self == IntensiveRepetitionType._30_30:
            return min(20, repetitions)
        if self == IntensiveRepetitionType._200M:
            return min(20, repetitions)
        return min(15, repetitions)

    def distance(self):
        if self == IntensiveRepetitionType._30_30:
            return 0
        if self == IntensiveRepetitionType._200M:
            return 0.2
        return 0.3

    def __str__(self):
        if self == IntensiveRepetitionType._30_30:
            return "30-30"
        if self == IntensiveRepetitionType._200M:
            return "200M"
        return "300M"


class ExtensiveRepetitionType(Enum):
    _400M = 1
    _500M = 2
    _600M = 3
    _800M = 4

    def check_repetitions(self, race, repetitions):
        if race == SessionType.FIVE:
            coefs = [12, 8, 4, 3]
        elif race == SessionType.TEN:
            coefs = [14, 8, 6, 4]
        elif race == SessionType.HALF:
            coefs = [18, 12, 10, 8]
        else:
            coefs = [20, 14, 12, 10]
        coef = coefs[int(self) - 1]
        return min(coef, repetitions)

    def __int__(self):
        if self == ExtensiveRepetitionType._400M:
            return 1
        if self == ExtensiveRepetitionType._500M:
            return 2
        if self == ExtensiveRepetitionType._600M:
            return 3
        return 4

    def distance(self):
        if self == ExtensiveRepetitionType._400M:
            return 0.4
        if self == ExtensiveRepetitionType._500M:
            return 0.5
        if self == ExtensiveRepetitionType._600M:
            return 0.6
        return 0.8

    def __str__(self):
        if self == ExtensiveRepetitionType._400M:
            return "400M"
        if self == ExtensiveRepetitionType._500M:
            return "500M"
        if self == ExtensiveRepetitionType._600M:
            return "600M"
        return "800M"


class SpeRepetitionType(Enum):
    _1000M = 1
    _2000M = 2
    _3000M = 3
    _4000M = 4
    _5000M = 5
    _10000M = 6

    @classmethod
    def pick(cls, race, week_num, coef=1):
        if race == SessionType.FIVE:
            week_num = min(week_num, 3 * coef)
            repetitions = min(week_num * 2, 4 * coef)
        elif race == SessionType.TEN:
            max_volume = 10 * 0.8
            week_num = min(week_num, 4 * coef)
            repetitions = (3 + week_num) * coef
            while repetitions * week_num > max_volume:
                repetitions -= 1
        elif race == SessionType.HALF:
            week_num = min(week_num, 5 * coef)
            repetitions = min(week_num * 2, 8*coef)
        elif race == SessionType.MARATHON:
            week_num = min(week_num, 6 * coef * coef)
            repetitions = min(week_num * 2, 10 * coef)
        instance = cls(round(week_num))
        return instance, repetitions

    def distance(self):
        if self == SpeRepetitionType._1000M:
            return 1
        if self == SpeRepetitionType._2000M:
            return 2
        if self == SpeRepetitionType._3000M:
            return 3
        if self == SpeRepetitionType._4000M:
            return 4
        if self == SpeRepetitionType._5000M:
            return 5
        return 10

    def repetitions(self, race, week):
        if self == SpeRepetitionType._1000M:
            return 1
        if self == SpeRepetitionType._2000M:
            return 2
        if self == SpeRepetitionType._3000M:
            return 3
        if self == SpeRepetitionType._4000M:
            return 4
        if self == SpeRepetitionType._5000M:
            return 5
        return 10

    def check_repetitions(self, race, repetitions):
        return repetitions

    def __str__(self):
        if self == SpeRepetitionType._1000M:
            return "1k"
        if self == SpeRepetitionType._2000M:
            return "2k"
        if self == SpeRepetitionType._3000M:
            return "3k"
        if self == SpeRepetitionType._4000M:
            return "4k"
        if self == SpeRepetitionType._5000M:
            return "5k"
        return "10k"


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


class Week:
    def __init__(self, plan, num, type, spw, race):
        self.type = type
        self.spw = spw
        self.race = race
        self.num = num
        self.plan = plan
        self.race_week = type == WeekType.SPECIFIC and num == plan.total_weeks
        self.taper_week = type == WeekType.SPECIFIC and num == plan.total_weeks - 1
        self.regular_week = not self.race_week and not self.taper_week
        if self.race_week:
            coef = 0.5
        elif self.taper_week:
            coef = 0.6
        else:
            coef = 1.0

        if self.race_week:
            self.sessions = [
                self._session(SessionType.INTENSIVE_INTERVALS, coef),
                self._session(SessionType.ENDURANCE, coef),
                self._session(self._extensive_or_spe(), coef),
            ]
        else:
            self.sessions = [
                self._session(SessionType.INTENSIVE_INTERVALS, coef),
                self._session(self._extensive_or_spe(), coef),
                self._session(SessionType.LONG_RUN, coef),
            ]
            if self.spw == 4:
                self.sessions.insert(1, self._session(SessionType.ENDURANCE,
                    coef))
            elif self.spw == 5:
                self.sessions.insert(1, self._session(SessionType.ENDURANCE,
                    coef))
                self.sessions.insert(3, self._session(SessionType.ENDURANCE,
                    coef))

        for num, session in enumerate(self.sessions):
            session.num = num + 1

        self.duration = sum([session.duration for session in self.sessions])
        self.distance = sum([session.distance for session in self.sessions])

    def __str__(self):
        res = [
            "Semaine %d | %s | %s"
            % (self.num, self.type, duration_to_str(self.duration)),
            self.description,
        ]
        for session in self.sessions:
            res.append(str(session))
        return "\n".join(res)

    @property
    def description(self):
        if self.type == WeekType.GENERAL:
            desc = (
                "Alternance de fractionné intensif/extensif pour faire "
                " progresser la VMA."
            )
            if self.num == 1:
                desc = "Début du plan! " + desc
            elif self.num == self.plan.gen_weeks:
                desc = "Dernière semaine de préparation générale."
            else:
                desc = "Augmentation progressive des volumes."
        else:
            if self.num == self.plan.gen_weeks + 1:
                desc = (
                    "Début de la prépa spécifique. "
                    "Fractionné intensif pour entretenir la VMA, et allure "
                    "spécifique."
                )
            elif self.num == len(self.plan.weeks):
                desc = (
                    "Semaine de la course, objectif repos. Attention à la "
                    "qualité du sommeil pour bien récupérer."
                )
            elif self.num == len(self.plan.weeks) - 1:
                desc = "Réduction du volume."
            else:
                desc = "Augmentation progressive des volumes."
        return desc

    def json(self):
        res = {
            "type": str(self.type),
            "num": self.num,
            "duration": duration_to_str(self.duration),
            "description": self.description,
            "distance": self.distance,
        }
        res["sessions"] = [session.json() for session in self.sessions]
        total = sum([session.duration for session in self.sessions])
        total_distance = sum([session.distance for session in self.sessions])
        summary = {
            "type": "",
            "description": "",
            "duration": duration_to_str(total),
            "distance": "%skm" % speed_to_str(total_distance),
        }
        res["sessions"].append(summary)
        return res

    def _extensive_or_spe(self):
        if self.type == WeekType.GENERAL:
            return SessionType.EXTENSIVE_INTERVALS
        return self.race

    def _session(self, type, coef=1):
        return Session(self, type, coef)


def seconds_to_str(seconds):
    td = dt.timedelta(seconds=seconds)
    hours, minutes = td.seconds // 3600, (td.seconds // 60) % 60
    seconds = seconds - hours * 3600 - minutes * 60
    if seconds > 0:
        res = "%ss" % seconds
    else:
        res = ""
    if minutes > 0:
        res = "%smn" % minutes + res
    if hours > 0:
        res = "%dh" % hours + res
    return res


def duration_to_str(duration):
    td = dt.timedelta(minutes=duration)
    hours, minutes = td.seconds // 3600, (td.seconds // 60) % 60
    if hours == 0:
        return "%dmn" % minutes
    if minutes == 0:
        return "%dh" % hours
    return "%dh%dmn" % (hours, minutes)


def vma_to_speed(vma, percent=100):
    return round(vma * percent / 50) / 2.0


def speed_to_str(speed):
    if int(speed) == speed:
        return "%d" % speed
    return "%.1f" % speed


WARMUP = (60, 65)
ENDURANCE = (65, 75)


class Continuous:
    def __init__(self, session, duration, intensity=ENDURANCE):
        self.duration = duration
        vma = session.week.plan.vma
        self.speed_low = vma_to_speed(vma, intensity[0])
        self.speed_high = vma_to_speed(vma, intensity[1])
        speed_avg = (self.speed_low + self.speed_high) / 2.0
        self.distance = self.duration / 60 * speed_avg

    @classmethod
    def for_race(cls, session, race):
        intensity = race.intensity()
        distance = race.distance()
        vma = session.week.plan.vma
        speed_low = vma_to_speed(vma, intensity[0])
        speed_high = vma_to_speed(vma, intensity[1])
        speed_avg = (speed_low + speed_high) / 2.0
        duration = (distance / speed_avg * 60)
        return cls(session, duration, intensity)

    def __str__(self):
        return "%s (entre %s et %s km/h)" % (
            duration_to_str(self.duration),
            speed_to_str(self.speed_low),
            speed_to_str(self.speed_high),
        )

    def json(self):
        return {
            "duration": self.duration,
            "speed_low": self.speed_low,
            "speed_high": self.speed_high,
            "distance": self.distance,
        }


def vma_percent(vma, percent=100):
    return percent / 100 * vma


class Interval:
    def __init__(self, session, repetitions, type):
        self.vma = session.vma
        self.session = session
        self.repetitions = type.check_repetitions(session.race, repetitions)
        self.type = type
        self.recovery_speed = vma_percent(self.vma, 60)
        if isinstance(self.type, SpeRepetitionType):
            self.recovery_duration = 60
            self.recovery_distance = self.recovery_speed * self.recovery_duration / 3600
        elif isinstance(self.type, IntensiveRepetitionType):
            self.recovery_distance = type.distance() * 0.6
            self.recovery_duration = round(
                self.recovery_distance / self.recovery_speed * 3600
            )
        else:
            self.recovery_distance = type.distance() * 0.3
            self.recovery_duration = round(
                self.recovery_distance / self.recovery_speed * 3600
            )

        self.repetition_speed = vma_percent(self.vma, 95)
        self.repetition_distance = type.distance()
        self.repetition_duration = round(type.distance() / self.repetition_speed * 3600)
        self.duration = (
            self.repetition_duration / 60 * repetitions
            + self.recovery_duration / 60 * repetitions
        )
        self.distance = (
            self.repetition_distance * repetitions
            + self.recovery_distance * repetitions
        )

    def __str__(self):
        return "%d x %s | effort de %s | contre-effort de %s | %s" % (
            self.repetitions,
            self.type,
            seconds_to_str(self.repetition_duration),
            seconds_to_str(self.recovery_duration),
            duration_to_str(self.duration),
        )

    def json(self):
        return {
            "repetitions": self.repetitions,
            "type": str(self.type),
            "recovery_speed": speed_to_str(self.recovery_speed),
            "duration": duration_to_str(self.duration),
            "distance": self.distance,
        }


class Session:
    def __init__(self, week, type, coef=1.0):
        self.type = type
        self.race = week.race
        self.week = week
        self.num = 0
        self.vma = week.plan.vma

        if type in (SessionType.ENDURANCE, SessionType.LONG_RUN):
            if self.race in (SessionType.FIVE, SessionType.TEN):
                self.base_time = 40
            elif self.race == SessionType.HALF:
                self.base_time = 50
            else:
                self.base_time = 60
            if type == SessionType.LONG_RUN:
                self.base_time *= 1.6

            self.base_time *= coef
            self.core = Continuous(
                self, self.base_time + ((week.num - 1) * self.base_time * 0.1)
            )
            self.warmup = None
            self.cool_down = None
            self.duration = self.core.duration
            self.distance = self.core.distance
        elif self.week.race_week and type == self.race:
            self.base_time = 0
            if self.race in (SessionType.FIVE, SessionType.TEN):
                warmup_time = 15
            elif self.race == SessionType.HALF:
                warmup_time = 20
            else:
                warmup_time = 25
            self.warmup = Continuous(self, warmup_time, WARMUP)
            self.cool_down = None
            self.core = Continuous.for_race(self, self.race)
            self.duration = (
                self.warmup.duration + self.core.duration
            )
            self.distance = (
                self.warmup.distance + self.core.distance
            )
        else:
            self.base_time = 0
            if self.race in (SessionType.FIVE, SessionType.TEN):
                warmup_time = 15
            elif self.race == SessionType.HALF:
                warmup_time = 20
            else:
                warmup_time = 25
            self.warmup = Continuous(self, warmup_time, WARMUP)
            self.cool_down = Continuous(self, 15)
            self.core = self._build_interval(coef)
            self.duration = (
                self.warmup.duration + self.core.duration + self.cool_down.duration
            )
            self.distance = (
                self.warmup.distance + self.core.distance + self.cool_down.distance
            )

        self.distance = round(self.distance * 2) / 2
        self.week = week

    def _graduation(self, base):
        # XXX inclue tapering at the end
        return base + ((self.week.num - 1) * base * 0.1)

    def _build_interval(self, coef):
        # XXX definir des max de repetition et de distance
        # sur le 10 ca enchine 10x200, 11x300, 13x200, 14x300
        #
        if self.type == SessionType.INTENSIVE_INTERVALS:
            type = self.week.num % len(IntensiveRepetitionType) + 1
            type = IntensiveRepetitionType(type)
            repetitions = self._graduation(10 * coef)
        elif self.type == SessionType.EXTENSIVE_INTERVALS:
            type = self.week.num % len(ExtensiveRepetitionType) + 1
            type = ExtensiveRepetitionType(type)
            repetitions = self._graduation(6 * coef)
        else:
            # spe
            type, repetitions = SpeRepetitionType.pick(
                self.race, self.week.num - self.week.plan.gen_weeks,
                coef
            )

        return Interval(self, repetitions, type)

    def __str__(self):
        duration = duration_to_str(self.duration)
        if self.type in (SessionType.ENDURANCE, SessionType.LONG_RUN):
            return "- Entraînement %d | %s | %s" % (self.num, self.type, duration)
        res = ["- Entraînement %d | %s | %s" % (self.num, self.type, duration)]
        res += ["  - Echauffement | %s" % self.warmup]
        res += ["  - %s" % self.core]
        res += ["  - Retour au calme | %s" % self.cool_down]
        return "\n".join(res)

    # XXX crap
    def _to_html(self, *elements):
        res = "<ul>"
        for el in elements:
            res += "<li>%s</li>" % el
        res += "</ul>"
        return res

    def json(self):
        res = {
            "type": str(self.type),
            "num": self.num,
            "duration": duration_to_str(self.duration),
            "distance": "%skm" % speed_to_str(self.distance),
        }
        if self.type in (SessionType.ENDURANCE, SessionType.LONG_RUN):
            res["description"] = "Effort continu de " + str(self.core)
            return res
        res["warmup"] = self.warmup.json()
        res["cool_down"] = self.cool_down is not None and self.cool_down.json() or {}
        res["core"] = self.core.json()
        if self.cool_down is not None:
            res["description"] = self._to_html(
                "Echauffement %s" % self.warmup,
                "%s" % self.core,
                "Retour au calme %s" % self.cool_down,
            )
        elif self.week.race_week and self.type == self.race:

            res["description"] = self._to_html(
                "Echauffement %s" % self.warmup,
                "Course!!! %s" % self.core
            )
        else:
            res["description"] = self._to_html(
                "Echauffement %s" % self.warmup,
                "%s" % self.core
            )
        return res


class TrainingPlan:
    def __init__(self, race, vma):
        self.race = race
        self.vma = vma
        self.spw = None
        self.gen_weeks = None
        self.spe_weeks = None
        self.weeks = []
        self.total_weeks = None

    def __str__(self):
        res = ["Plan %s sur %d semaines" % (str(self.race), len(self.weeks))]
        res += [""]
        for week in self.weeks:
            res.append(str(week))
            res.append("")
        return "\n".join(res)

    def json(self):
        res = {"title": "Plan %s sur %d semaines" % (str(self.race), len(self.weeks))}
        res["weeks"] = [week.json() for week in self.weeks]
        desc = ["Le plan est organisé en deux parties. "]
        desc.append(
            "La première partie est une préparation générale de %d "
            "semaines. " % self.gen_weeks
        )
        desc.append(
            "La deuxième partie est une préparation spécifique de %d "
            "semaines. " % self.spe_weeks
        )
        res["description"] = "\n".join(desc)
        return res

    def build(self, weeks, spw):
        if weeks < 8:
            raise ValueError("Plan sur 8 semaines minimum")
        if spw < 3:
            raise ValueError("Plan avec 3 séances par semaine minimum")
        if spw > 5:
            raise ValueError("5 séances max")

        self.spw = spw
        self.total_weeks = weeks
        # we cut the training in 2 halves
        self.gen_weeks, rest = divmod(weeks, 2)
        self.spe_weeks = weeks - self.gen_weeks + rest

        # and generate weeks...
        for week_num in range(1, self.gen_weeks + 1):
            self.weeks.append(Week(self, week_num, WeekType.GENERAL, spw, self.race))

        for week_num in range(self.gen_weeks + 1, self.gen_weeks + self.spe_weeks + 1):
            self.weeks.append(Week(self, week_num, WeekType.SPECIFIC, spw, self.race))


def plan(race=SessionType.TEN, vma=18.5, weeks=8, spw=5):
    training = TrainingPlan(race, vma)
    training.build(weeks, spw)
    return training


if __name__ == "__main__":
    print(plan().json())

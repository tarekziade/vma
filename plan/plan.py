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
        # typical week with 3 quality sessions.
        self.sessions = [
            self._session(SessionType.INTENSIVE_INTERVALS),
            self._session(self._extensive_or_spe()),
            self._session(SessionType.LONG_RUN),
        ]
        # we add endurance runs
        if self.spw == 4:
            self.sessions.insert(1, self._session(SessionType.ENDURANCE))
        elif self.spw == 5:
            self.sessions.insert(1, self._session(SessionType.ENDURANCE))
            self.sessions.insert(3, self._session(SessionType.ENDURANCE))

        for num, session in enumerate(self.sessions):
            session.num = num + 1

        self.duration = sum([session.duration for session in self.sessions])

    def __str__(self):
        res = [
            "Semaine %d | %s | %s"
            % (self.num, self.type, duration_to_str(self.duration))
        ]
        for session in self.sessions:
            res.append(str(session))
        return "\n".join(res)

    def json(self):
        res = {"type": str(self.type), "num": self.num,
               "duration": duration_to_str(self.duration)}
        res["sessions"] = [session.json() for session in self.sessions]
        total = sum([session.duration for session in self.sessions])
        summary = {"type": "", "description": "",
                   "duration": duration_to_str(total)}
        res["sessions"].append(summary)
        return res

    def _extensive_or_spe(self):
        if self.type == WeekType.GENERAL:
            return SessionType.EXTENSIVE_INTERVALS
        return self.race

    def _session(self, type):
        return Session(self, type)


def duration_to_str(duration):
    td = dt.timedelta(minutes=duration)
    hours, minutes = td.seconds // 3600, (td.seconds // 60) % 60
    if hours == 0:
        return "%dmn" % minutes
    if minutes == 0:
        return "%dh" % hours
    return "%dh%dmn" % (hours, minutes)


def vma_to_speed(vma, percent=100):
    return round(vma * percent / 50) / 2.


def speed_to_str(speed):
    if int(speed) == speed:
        return '%d' % speed
    return '%.1f' % speed


WARMUP = (60, 65)
ENDURANCE = (65, 75)


class Continuous:
    def __init__(self, session, duration, intensity=ENDURANCE):
        self.duration = int(5 * round(float(duration) / 5))
        vma = session.week.plan.vma
        self.speed_low = vma_to_speed(vma, intensity[0])
        self.speed_high = vma_to_speed(vma, intensity[1])

    def __str__(self):
        return "%s (entre %s et %s km/h)" % (
                duration_to_str(self.duration),
                speed_to_str(self.speed_low),
                speed_to_str(self.speed_high)
                )

    def json(self):
        return {"duration": self.duration,
                "speed_low": self.speed_low,
                "speed_high": self.speed_high}

class Interval:
    def __init__(self, session, repetitions, type):
        self.session = session
        self.repetitions = repetitions
        self.type = type
        # calculer la duree en fonction de la VMA
        self.duration = 30
        self.duration = int(5 * round(float(self.duration) / 5))

    def __str__(self):
        return "%d x %s (%s)" % (
            self.repetitions,
            self.type,
            duration_to_str(self.duration),
        )

    def json(self):
        return {"repetitions": self.repetitions,
                "type": str(self.type),
                "duration": duration_to_str(self.duration)}


class Session:
    def __init__(self, week, type):
        self.type = type
        self.race = week.race
        self.week = week
        self.num = 0
        if type in (SessionType.ENDURANCE, SessionType.LONG_RUN):
            if self.race in (SessionType.FIVE, SessionType.TEN):
                self.base_time = 40
            elif self.race == SessionType.HALF:
                self.base_time = 50
            else:
                self.base_time = 60
            if type == SessionType.LONG_RUN:
                self.base_time *= 1.6

            self.core = Continuous(
                self, self.base_time + ((week.num - 1) * self.base_time * 0.1)
            )
            self.warmup = None
            self.cool_down = None
            duration = self.core.duration
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
            self.core = self._build_interval()

            duration = (
                self.warmup.duration + self.core.duration + self.cool_down.duration
            )
        self.duration = duration
        self.week = week

    def _graduation(self, base):
        # XXX inclue tapering at the end
        return base + ((self.week.num - 1) * base * 0.1)

    def _build_interval(self):
        # XXX definir des max de repetition et de distance
        if self.type == SessionType.INTENSIVE_INTERVALS:
            type = self.week.num % len(IntensiveRepetitionType) + 1
            type = IntensiveRepetitionType(type)
            repetitions = self._graduation(10)
        elif self.type == SessionType.EXTENSIVE_INTERVALS:
            type = self.week.num % len(ExtensiveRepetitionType) + 1
            type = ExtensiveRepetitionType(type)
            repetitions = self._graduation(6)
        else:
            # spe
            type = self.week.num % len(SpeRepetitionType) + 1
            type = SpeRepetitionType(type)
            repetitions = self._graduation(4)

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
        res = {"type": str(self.type), "num": self.num,
               "duration": duration_to_str(self.duration)}
        if self.type in (SessionType.ENDURANCE, SessionType.LONG_RUN):
            res["description"] = "Effort continu de " + str(self.core)
            return res
        res["warmup"] = self.warmup.json()
        res["cool_down"] = self.cool_down.json()
        res["core"] = self.core.json()
        res["description"] = self._to_html("Echauffement %s" % self.warmup,
                              "%s" % self.core,
                              "Retour au calme %s" % self.cool_down)
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
        res = ["Plan d'entraînement sur %d semaines" % len(self.weeks)]
        res += [""]
        for week in self.weeks:
            res.append(str(week))
            res.append("")
        return "\n".join(res)

    def json(self):
        res = {"title": "Plan d'entraînement sur %d semaines" % len(self.weeks)}
        res["weeks"] = [week.json() for week in self.weeks]
        return res

    def build(self, weeks, spw):
        if weeks < 8:
            raise ValueError("Plan sur 8 semaines minimum")
        if spw < 3:
            raise ValueError("Plan avec 3 séances par semaine minimum")
        if spw > 5:
            raise ValueError("5 séances max")

        self.spw = spw
        self.total_weeeks = weeks
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

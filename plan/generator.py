# encoding: utf8
from enum import Enum
import datetime as dt
import zlib, base64

from plan.interval import repetition_from_hash, pick_repetition, NORMAL, EASY, HARD
from plan.session import SessionType, WeekType


def distance_acceleration(initial_speed, final_speed, duration):
    average_speed = (initial_speed + final_speed) / 2.0
    return duration * average_speed


class Week:
    def __init__(self, plan, num, type, spw, race, sessions_builder=None):
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

        if sessions_builder is None:
            if self.race_week:
                self.sessions = [
                    self._session(SessionType.INTENSIVE_INTERVALS, coef),
                    self._session(SessionType.ENDURANCE, coef),
                    self._session(self._extensive_or_spe(), coef),
                ]
            else:
                # 3 runs a week is one extensivee or spe, one endurance, and one
                # long run

                if self.spw == 3:
                    self.sessions = [
                        self._session(SessionType.ENDURANCE, coef),
                        self._session(self._extensive_or_spe(), coef),
                        self._session(SessionType.LONG_RUN, coef),
                    ]

                else:
                    self.sessions = [
                        self._session(SessionType.INTENSIVE_INTERVALS, coef),
                        self._session(self._extensive_or_spe(), coef),
                        self._session(SessionType.LONG_RUN, coef),
                    ]
                    if self.spw == 4:
                        self.sessions.insert(
                            1, self._session(SessionType.ENDURANCE, coef)
                        )
                    elif self.spw == 5:
                        self.sessions.insert(
                            1, self._session(SessionType.ENDURANCE, coef)
                        )
                        self.sessions.insert(
                            3, self._session(SessionType.ENDURANCE, coef)
                        )

            for num, session in enumerate(self.sessions):
                session.num = num + 1
        else:
            self.sessions = sessions_builder(self)

        self.duration = sum([session.duration for session in self.sessions])
        self.distance = sum([session.distance for session in self.sessions])

    @classmethod
    def from_hash(self, hash, plan, num, type, spw, race):
        elmts = hash[1:-1].split("_")

        def builder(week):
            sessions = []
            for session_hash in elmts:
                sessions.append(Session.from_hash(session_hash, week))
            return sessions

        return Week(plan, num, type, spw, race, sessions_builder=builder)

    @property
    def hash(self):
        key = []
        for session in self.sessions:
            key.append(session.hash)
        return "[" + "_".join(key) + "]"

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
            "num": "",
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
        return Session(self, type, coef, cross=self.plan.cross)


def seconds_to_str(seconds):
    td = dt.timedelta(seconds=seconds)
    hours, minutes = td.seconds // 3600, (td.seconds // 60) % 60
    seconds = round(seconds - hours * 3600 - minutes * 60)
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
COOL_DOWN = (50, 65)


def _r(duration, base=5):
    return base * round(duration / base)


def _j(l, char="+"):
    return char.join([str(i) for i in l])


def _s(l, char="+"):
    return l.split(char)


class Bike:
    def __init__(self, duration):
        self.duration = duration
        # hardcoded for now
        self.speed = 22
        self.distance = self.speed * duration / 60.0

    def __str__(self):
        return duration_to_str(self.duration)

    @property
    def hash(self):
        return "B%d" % self.duration

    @classmethod
    def from_hash(cls, hash):
        duration = int(hash[1:])
        return cls(duration)


class Continuous:
    def __init__(self, vma, duration, intensity=ENDURANCE):
        self.duration = _r(duration)
        self.vma = vma
        self.intensity = intensity
        self.speed_low = vma_to_speed(vma, intensity[0])
        self.speed_high = vma_to_speed(vma, intensity[1])
        speed_avg = (self.speed_low + self.speed_high) / 2.0

        if intensity == ENDURANCE:
            # 10mn acceleration
            warmup_distance = distance_acceleration(9.0, speed_avg, 10.0 / 60.0)
            self.core_duration = self.duration - 10.0
            core_distance = self.core_duration / 60 * speed_avg
            self.distance = core_distance + warmup_distance
        else:
            self.distance = self.duration / 60 * speed_avg
            self.core_duration = None

    @property
    def hash(self):
        if self.intensity == ENDURANCE:
            code = 1
        else:
            code = 2
        if round(self.duration) == self.duration:
            duration = round(self.duration)
        else:
            duration = self.duration
        return "|".join([str(duration), str(code)])

    @classmethod
    def from_hash(cls, hash, session):
        hash = hash.split("|")
        if int(hash[1]) == 1:
            intensity = ENDURANCE
        else:
            intensity = WARMUP
        duration = float(hash[0])
        return cls(session.vma, duration, intensity)

    @classmethod
    def for_race(cls, vma, race):
        intensity = race.intensity()
        distance = race.distance()
        speed_low = vma_to_speed(vma, intensity[0])
        speed_high = vma_to_speed(vma, intensity[1])
        speed_avg = (speed_low + speed_high) / 2.0
        duration = distance / speed_avg * 60
        return cls(vma, duration, intensity)

    @property
    def title(self):
        if self.intensity == ENDURANCE:
            return "Endurance de %s" % duration_to_str(self.duration)
        if self.intensity == WARMUP:
            return "Echauffement de %s" % duration_to_str(self.duration)
        return "Retour au calme de %s" % duration_to_str(self.duration)

    def __str__(self):
        if self.intensity == ENDURANCE:
            info = "10mn de 9 à %skm/h<br/>%s entre %s et %skm/h" % (
                speed_to_str(self.speed_low),
                duration_to_str(self.core_duration),
                speed_to_str(self.speed_low),
                speed_to_str(self.speed_high),
            )

        else:
            info = "Vitesse entre %s et %s km/h" % (
                speed_to_str(self.speed_low),
                speed_to_str(self.speed_high),
            )

        return """%s <i class="question circle icon" data-variation="mini inverted" data-html="%s"></i>
           """ % (
            self.title,
            info,
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
    def __init__(self, session, type):
        self.vma = session.vma
        self.session = session
        self.repetitions = type.repetitions
        self.type = type
        # split in two
        if self.repetitions > 8:
            repetitions, remainder = divmod(self.repetitions, 2)
            self.repetitions = [repetitions + remainder] * 2
            self.between_duration = 2.0
        else:
            self.between_duration = 0.0
            self.repetitions = (self.repetitions,)

        self.duration = _r(
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
        return "I" + _j([self.type.hash], ";")

    @classmethod
    def from_hash(cls, hash, session):
        hash = hash[1:]
        hash = _s(hash, ";")
        type = repetition_from_hash(hash[0], session)
        return cls(session, type)

    def __str__(self):
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


class Session:
    def __init__(self, week, type, coef=1.0, session_builder=None, cross=False):
        self.type = type
        self.race = week.race
        self.week = week
        self.num = 0
        self.vma = week.plan.vma
        self.level = week.plan.level
        self.coef = coef
        self.cross = cross

        if session_builder is not None:
            self.warmup, self.core, self.cool_down = session_builder(self)

        # endurance or long run
        if type in (SessionType.ENDURANCE, SessionType.LONG_RUN):
            if self.race in (SessionType.FIVE, SessionType.TEN):
                self.base_time = 40
            elif self.race == SessionType.HALF:
                self.base_time = 50
            else:
                self.base_time = 60
            if type == SessionType.LONG_RUN:
                self.base_time *= 1.6

            if self.level == EASY:
                self.base_time -= 10
            elif self.level == HARD:
                self.base_time += 10

            week_pair = week.num % 2 == 1
            self.base_time *= coef
            if session_builder is None:
                duration = self.base_time + ((week.num - 1) * self.base_time * 0.1)
                if self.cross and type == SessionType.ENDURANCE and week_pair:
                    self.core = Bike(duration * 1.25)
                elif self.cross and type == SessionType.LONG_RUN and not week_pair:
                    self.core = Bike(duration * 1.5)
                else:
                    self.core = Continuous(self.vma, duration)
                self.warmup = None
                self.cool_down = None
        # interval or race
        else:
            self.base_time = 0
            if session_builder is None:
                if self.race in (SessionType.FIVE, SessionType.TEN):
                    warmup_time = 15
                elif self.race == SessionType.HALF:
                    warmup_time = 20
                else:
                    warmup_time = 25

                self.warmup = Continuous(self.vma, warmup_time, WARMUP)

                if self.week.race_week and type == self.race:
                    self.cool_down = None
                    self.core = Continuous.for_race(self.vma, self.race)
                else:
                    self.cool_down = Continuous(self.vma, 15, COOL_DOWN)
                    self.core = self._build_interval(coef)

        self.duration = self.core.duration
        self.distance = self.core.distance
        if self.warmup:
            self.duration += self.warmup.duration
            self.distance += self.warmup.distance
        if self.cool_down:
            self.duration += self.cool_down.duration
            self.distance += self.cool_down.distance

        self.distance = round(self.distance * 2) / 2
        self.week = week

    @classmethod
    def from_hash(cls, hash, week):
        elmts = hash.split(":")

        def builder(session):
            def _get_cont(elmt):
                if elmt == "x":
                    return None
                return Continuous.from_hash(elmt, session)

            warmup = _get_cont(elmts[2])
            if elmts[3].startswith("I"):
                core = Interval.from_hash(elmts[3], session)
            elif elmts[3].startswith("B"):
                core = Bike.from_hash(elmts[3])
            else:
                core = Continuous.from_hash(elmts[3], session)
            cd = _get_cont(elmts[4])
            return warmup, core, cd

        return cls(week, elmts[0], elmts[1], session_builder=builder)

    @property
    def hash(self):
        if round(self.coef) == self.coef:
            coef = str(int(self.coef))
        else:
            coef = str(self.coef)
        key = [str(int(self.type)), str(coef)]
        if self.warmup:
            key.append(self.warmup.hash)
        else:
            key.append("x")
        key.append(self.core.hash)
        if self.cool_down:
            key.append(self.cool_down.hash)
        else:
            key.append("x")
        return ":".join(key)

    def _graduation(self, base):
        # XXX inclue tapering at the end
        return base + ((self.week.num - 1) * base * 0.1)

    def _build_interval(self, coef):
        type = pick_repetition(
            self.type,
            self.race,
            self.week.num,
            self.vma,
            self.week.type,
            self.week.plan.total_weeks,
            self.level,
        )
        return Interval(self, type)

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
            if not isinstance(self.core, Bike):
                res["description"] = str(self.core)
            else:
                res["description"] = "Sortie vélo de " + str(self.core)
            return res
        res["warmup"] = self.warmup.json()
        res["cool_down"] = self.cool_down is not None and self.cool_down.json() or {}
        res["core"] = self.core.json()
        if self.cool_down is not None:
            res["description"] = self._to_html(self.warmup, self.core, self.cool_down)
        elif self.week.race_week and self.type == self.race:

            res["description"] = self._to_html(self.warmup, "Course!!! %s" % self.core)
        else:
            res["description"] = self._to_html(self.warmup, "%s" % self.core)
        return res


class TrainingPlan:
    def __init__(self, race, vma, level, cross):
        self.race = race
        self.vma = vma
        self.level = level
        self.spw = None
        self.gen_weeks = None
        self.spe_weeks = None
        self.weeks = []
        self.total_weeks = None
        self.cross = cross

    @classmethod
    def from_small_hash(cls, hash):
        uncompressed = zlib.decompress(base64.b64decode(hash)).decode("utf8")
        return cls.from_hash(uncompressed)

    @classmethod
    def from_hash(cls, hash):
        elements = _s(hash)
        race = int(elements[0])
        vma = float(elements[1])
        level = float(elements[2])
        cross = elements[3] == 1
        plan = cls(race, vma, level, cross)
        plan.spw = elements[3]
        # ugly
        weeks = [w.strip("[]") for w in _j(elements[4:]).split("]+[")]
        for num, week_hash in enumerate(weeks):
            plan.weeks.append(
                Week.from_hash("[" + week_hash + "]", plan, num, type, plan.spw, race)
            )
        return plan

    @property
    def hash(self):
        key = [
            int(self.race),
            self.vma,
            self.level,
            self.spw,
            self.cross and "1" or "0",
        ]
        for week in self.weeks:
            key.append(week.hash)
        return _j(key)

    @property
    def small_hash(self):
        return base64.b64encode(zlib.compress(self.hash.encode("utf8"), 9))

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
        res["hash"] = self.small_hash.decode("utf8")
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


def plan(race=SessionType.TEN, vma=18.5, weeks=8, spw=5, level=NORMAL, cross=False):
    training = TrainingPlan(race, vma, level, cross=cross)
    training.build(weeks, spw)
    return training


def plan_from_hash(hash):
    return TrainingPlan.from_small_hash(hash)


if __name__ == "__main__":
    p = plan(cross=True)
    hash = p.small_hash

    print(p.hash)
    print(len(p.small_hash))
    p2 = TrainingPlan.from_small_hash(hash)
    # data = zlib.decompress(base64.b64decode(p.small_hash))
    # print(data)
    # print(len(data))
    # print(plan().json())

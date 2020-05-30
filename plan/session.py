# encoding: utf8
from plan.bike import Bike
from plan.utils import duration_to_str, speed_to_str
from plan.continuous import Continuous
from plan.interval import Interval, pick_repetition, EASY, HARD
from plan.sessiontype import SessionType
from plan.constants import WARMUP, COOL_DOWN


class Session:
    def __init__(self, week, type, coef=1.0, session_builder=None, cross=False):
        self.type = type
        self.race = week.race
        self.week = week
        self.runner = week.runner
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
                    self.core = Continuous(self.runner, self.vma, duration)
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

                self.warmup = Continuous(self.runner, self.vma, warmup_time, WARMUP)

                if self.week.race_week and type == self.race:
                    self.cool_down = None
                    self.core = Continuous.for_race(self.runner, self.vma, self.race)
                else:
                    self.cool_down = Continuous(self.runner, self.vma, 15, COOL_DOWN)
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

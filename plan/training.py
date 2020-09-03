import zlib
import base64

from plan.week import Week, WeekType
from plan.utils import split, join
from plan.runner import Runner


def hash_encode(hash):
    hash = zlib.compress(hash.encode("utf8"), 9)
    return base64.urlsafe_b64encode(hash).rstrip(b"=")


def hash_decode(hash):
    padding = 4 - (len(hash) % 4)
    hash = hash + "=" * padding
    hash = base64.urlsafe_b64decode(hash)
    return zlib.decompress(hash).decode("utf8")


class TrainingPlan:
    def __init__(self, race, runner, level, cross):
        self.race = race
        self.runner = runner
        self.level = level
        self.spw = None
        self.gen_weeks = None
        self.spe_weeks = None
        self.weeks = []
        self.total_weeks = None
        self.cross = cross

    @classmethod
    def from_small_hash(cls, hash):
        return cls.from_hash(hash_decode(hash))

    @classmethod
    def from_hash(cls, hash):
        elements = split(hash)
        race = int(elements[0])
        runner = Runner.from_hash(elements[1])
        level = float(elements[2])
        cross = elements[3] == 1
        plan = cls(race, runner, level, cross)
        plan.spw = elements[4]
        # ugly
        weeks = [w.strip("[]") for w in join(elements[5:]).split("]+[")]

        plan.total_weeks = len(weeks)
        plan.gen_weeks, rest = divmod(plan.total_weeks, 2)
        plan.spe_weeks = plan.total_weeks - plan.gen_weeks + rest

        for num, week_hash in enumerate(weeks):
            if num < plan.gen_weeks:
                type = WeekType.GENERAL
            else:
                type = WeekType.SPECIFIC
            plan.weeks.append(
                Week.from_hash(
                    "[" + week_hash + "]", plan, num + 1, type, plan.spw, race
                )
            )

        return plan

    @property
    def hash(self):
        key = [
            int(self.race),
            self.runner.hash,
            self.level,
            self.spw,
            self.cross and "1" or "0",
        ]
        for week in self.weeks:
            key.append(week.hash)
        return join(key)

    @property
    def small_hash(self):
        return hash_encode(self.hash)

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
        desc.append(
            "Les vitesses sont données à titre indicatif pour des"
            " parcours plats et des conditions optimales (piste)."
        )
        desc.append(
            "Il faut adapter sa vitesse en cas de dénivellé, de "
            "terrain accidenté ou de surface lente type pelouse."
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

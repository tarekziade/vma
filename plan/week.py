from enum import Enum

from plan.utils import duration_to_str, speed_to_str
from plan.sessiontype import SessionType


class WeekType(Enum):
    GENERAL = 1
    SPECIFIC = 2

    def __str__(self):
        if self == WeekType.GENERAL:
            return "Préparation générale"
        return "Préparation spécifique"


class Week:
    def __init__(self, plan, num, type, spw, race, sessions_builder=None):
        self.type = type
        self.spw = spw
        self.race = race
        self.runner = plan.runner
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
        from plan.session import Session

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
        from plan.session import Session

        return Session(self, type, coef, cross=self.plan.cross)

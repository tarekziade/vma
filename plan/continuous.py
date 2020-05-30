from plan.utils import (
    speed_to_str,
    duration_to_str,
    round_duration,
    vma_to_speed,
    distance_acceleration,
)
from plan.constants import ENDURANCE, WARMUP


class Continuous:
    def __init__(self, runner, vma, duration, intensity=ENDURANCE):
        self.duration = round_duration(duration)
        # XXX should grab from runner
        self.vma = vma
        self.runner = runner
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

        self.max_fc = self.runner.get_max_fc(intensity[1])

    @property
    def hash(self):
        if self.intensity == ENDURANCE:
            code = 1
        else:
            code = 2
        if round_duration(self.duration) == self.duration:
            duration = round_duration(self.duration)
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
        return cls(session.runner, session.vma, duration, intensity)

    @classmethod
    def for_race(cls, runner, vma, race):
        intensity = race.intensity()
        distance = race.distance()
        speed_low = vma_to_speed(vma, intensity[0])
        speed_high = vma_to_speed(vma, intensity[1])
        speed_avg = (speed_low + speed_high) / 2.0
        duration = distance / speed_avg * 60
        return cls(runner, vma, duration, intensity)

    @property
    def title(self):
        if self.intensity == ENDURANCE:
            return "Endurance de %s" % duration_to_str(self.duration)
        if self.intensity == WARMUP:
            return "Echauffement de %s" % duration_to_str(self.duration)
        return "Retour au calme de %s" % duration_to_str(self.duration)

    def __str__(self):
        if self.intensity == ENDURANCE:
            lines = ["10mn de 9 à %skm/h", "%s entre %s et %skm/h", "FC Max %dbpm"]

            info = "<br/>".join(lines) % (
                speed_to_str(self.speed_low),
                duration_to_str(self.core_duration),
                speed_to_str(self.speed_low),
                speed_to_str(self.speed_high),
                self.max_fc,
            )
        else:
            lines = ["Vitesse entre %s et %s km/h", "FC Max %dbpm"]

            info = "<br/>".join(lines) % (
                speed_to_str(self.speed_low),
                speed_to_str(self.speed_high),
                self.max_fc,
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

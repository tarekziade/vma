from plan.utils import duration_to_str


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

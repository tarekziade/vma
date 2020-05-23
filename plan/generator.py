# encoding: utf8
from plan.session import SessionType
from plan.training import TrainingPlan
from plan.interval import NORMAL


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

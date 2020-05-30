# encoding: utf8
from plan.session import SessionType
from plan.training import TrainingPlan
from plan.interval import NORMAL
from plan.runner import Runner


def plan(
    race=SessionType.TEN,
    vma=18.5,
    weeks=8,
    spw=5,
    level=NORMAL,
    cross=False,
    age=43,
    max_hr=192,
):
    runner = Runner(age, vma, max_hr)
    training = TrainingPlan(race, runner, level, cross=cross)
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

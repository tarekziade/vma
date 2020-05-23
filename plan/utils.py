# encoding: utf8
import datetime as dt


def distance_acceleration(initial_speed, final_speed, duration):
    average_speed = (initial_speed + final_speed) / 2.0
    return duration * average_speed


def vma_percent(vma, percent=100):
    return percent / 100 * vma


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


def round_duration(duration, base=5):
    return base * round(duration / base)


def join(l, char="+"):
    return char.join([str(i) for i in l])


def split(l, char="+"):
    return l.split(char)

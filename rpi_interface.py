

def read_temp(channel):
    # mock
    import time
    import math
    t = time.time()
    th = t / 20.0
    return math.sin(th)


def set_pwm(channel, duty_ratio):
    pass


def read_temp(channel):
    # mock
    import time
    import math
    t = time.time()
    th = t
    return 3.0 * math.sin(th)


def set_pwm(channel, duty_ratio):
    pass
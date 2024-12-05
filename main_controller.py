import threading
from PID import PIDController
import rpi_interface
import time
from consts import STABLE_KP, Control_Interval_s

g_workers = []

MODE_IDLE = -1
MODE_DESCEND = 0
MODE_STABLE = 1

MIN_OUTPUT = 0
MAX_OUTPUT = 100

DIRECTION_UNDETERMINED = 0
DIRECTION_DESCEND = 1
DIRECTION_ASCEND = 2


class _RepeatTimer(threading.Timer):
    def run(self):
        while not self.finished.is_set():
            self.finished.wait(self.interval)
            self.function(*self.args, **self.kwargs)


class Worker(object):
    def __init__(self, channel):
        self.pid = PIDController()
        self.stable_pid = PIDController(STABLE_KP)
        self.timer = None
        self.mode = MODE_IDLE
        self.channel = channel

        # status
        self.last_T = 0

        # params
        self.target_dT = 0
        self.initial_T = 0
        self.target_T = 0
        self.target_direction = DIRECTION_UNDETERMINED

        # outputs
        self.T_data = []
        self.output_data = []

    def start_decend(self):
        self.target_direction = DIRECTION_UNDETERMINED
        self.mode = MODE_DESCEND

    def start_stable(self):
        self.mode = MODE_STABLE

    def stop(self):
        self.mode = MODE_IDLE

    def set_pid_params(self, kp, ki, kd):
        self.pid.k_p = kp
        self.pid.k_i = ki
        self.pid.k_d = kd

    def start(self):
        self.timer = _RepeatTimer(Control_Interval_s, self.run)
        self.timer.start()

    def stop(self):
        if self.timer:
            self.timer.cancel()

    def run(self):
        # 1. read
        t = time.time()
        current_T = rpi_interface.read_temp(self.channel)
        if current_T is None:
            # channel not valid
            return
        self.T_data.append((t, current_T))

        # 2. control
        if self.mode == MODE_DESCEND:
            output = self.run_descend_mode(current_T)
        elif self.mode == MODE_STABLE:
            output = self.run_descend_mode(current_T)
        else:
            return

        # 3. output
        self.output_data.append((t, output))

    def clamp(self, output):
        if output > MAX_OUTPUT:
            output = MAX_OUTPUT
        if output < MIN_OUTPUT:
            output = MIN_OUTPUT
        return output

    def run_stable_mode(self, current_T):
        # 1. calc error
        error_T = current_T - self.initial_T

        # 2. PID
        output = self.stable_pid.PID_Update(error_T)

        # 3. clamp
        output = self.clamp(output)

        return output

    def run_descend_mode(self, current_T):
        # 0. init direction
        if self.target_direction == DIRECTION_UNDETERMINED:
            if current_T > self.target_T:
                self.target_direction = DIRECTION_DESCEND
            else:
                self.target_direction = DIRECTION_ASCEND
        # 1. if finished, change to stable mode
        if self.target_direction == DIRECTION_DESCEND and current_T <= self.target_T \
                or self.target_direction == DIRECTION_ASCEND and current_T >= self.target_T:
            self.mode = MODE_STABLE
            self.initial_T = self.target_T

        # 2. update status and calc error
        dT = current_T - self.last_T
        error_dT = dT - self.target_dT
        self.last_T = current_T

        # 3. PID
        output = self.pid.PID_Update(error_dT)

        # 4. clamp
        output = self.clamp(output)

        return output


def Init_workers(channel_count=4):
    for i in range(channel_count):
        worker = Worker(i)
        g_workers.append(worker)
        worker.start()

def Stop_workers():
    for worker in g_workers:
        worker.stop()
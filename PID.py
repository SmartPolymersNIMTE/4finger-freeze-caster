

class PIDController(object):
    def __init__(self, kp=1, ki=0, kd=0):
        self.k_p = kp
        self.k_i = ki
        self.k_d = kd

        self.sum_error = 0
        self.last_error = 0

    def reset(self):
        self.sum_error = 0
        self.last_error = 0
    def PID_Update(self, cur_error):
        # update params
        self.sum_error += cur_error
        d_err = cur_error - self.last_error
        self.last_error = cur_error

        # pid formula
        output = self.k_p + self.k_i * self.sum_error + self.k_d * d_err

        return output
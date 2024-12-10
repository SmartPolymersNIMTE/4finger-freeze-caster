import RPi.GPIO as GPIO
from daqhats import hat_list, HatIDs, TcTypes, mcc134
from consts import MOSFET_FREQ, MAX_DUTY

hat = None
mosfet_pins = [12, 0, 0, 0]
mosfet_ctrls = []


def init():
    global hat
    ######################################### Temperature reader ######################################### 
    # Get hat list of MCC daqhat boards
    board_list = hat_list(filter_by_id = HatIDs.ANY)
    if not board_list:
        print("No boards sound")
        sys.exit()
    #Set Channel and reading frecuency
    channel0 = 0
    channel1 = 1
    channel2 = 2
    channel3 = 3
    delay_between_reads = 1 #seconds
    #Set thermocouple type and enable Channel
    tc_type = TcTypes.TYPE_T
    for entry in board_list:
        if entry.id==HatIDs.MCC_134:
            print("Board{}: MCC 134", format(entry.address))
            hat = mcc134(entry.address)
    hat.tc_type_write(channel0, tc_type)
    hat.tc_type_write(channel1, tc_type)
    hat.tc_type_write(channel2, tc_type)
    hat.tc_type_write(channel3, tc_type)
    
    ############################### Set up GPIO pins for MOSFET control ##################################
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BOARD) #for pin numbering use BOARD; for GPIO numbering use BCM
    for mosfet_pin in mosfet_pins:
        if mosfet_pin != 0:
            GPIO.setup(mosfet_pin, GPIO.OUT)
            pwm_mosfet = GPIO.PWM(mosfet_pin, MOSFET_FREQ)
            pwm_mosfet.start(0)
            mosfet_ctrls.append(pwm_mosfet)


def read_temp(channel):
    if not hat:
        return 0
    t = hat.t_in_read(channel)
    return t


def set_pwm(channel, duty_ratio):
    if channel >= len(mosfet_ctrls):
        return
    pwm_mosfet = mosfet_ctrls[channel]
    
    if duty_ratio < 0:
        duty_ratio = 0
    if duty_ratio > MAX_DUTY:
        duty_ratio = MAX_DUTY
    pwm_mosfet.ChangeDutyCycle(duty_ratio)


if __name__ == '__main__':
    init()
    import time
    while True:
        t = read_temp(0)
        print(t)
        time.sleep(0.1)

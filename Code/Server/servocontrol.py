import evdev
import threading
import time
import pprint

import ADC
import Buzzer
import gamepad
import Led
import Motor
import servo

disableMotor = False

class ServoControl:
    
    def __init__(self, debug = False):
        # data for horizontal (0) servo
        self.hor_cur = 90
        self._hor_min = 50
        self._hor_max = 130

        # data for vertical (1) servo
        self.ver_cur = 90
        self._ver_min = 80
        self._ver_max = 120

        # handle for servor driver
        self._pwm = servo.Servo()

        self.debug = debug

    def _addSat(self, a: int, b: int, min: int, max: int) -> int:
        ''' add a to b with saturation to [min, max] '''
        newval = a + b
        if newval < min:
            newval = min
        elif newval > max:
            newval = max
        return newval
    
    def rotate_horizontally(self, increment: int):
        '''positive increment means clock-wise rotation, center is 90, range is from 50..110'''
        self.hor_cur = self._addSat(self.hor_cur, increment, self._hor_min, self._hor_max)
        self._pwm.setServoPwm('0',self.hor_cur)
        if (self.debug):
            print('New horizontal angle: %d' % (self.hor_cur))


    def rotate_vertically(self, increment: int):
        '''positive increment means upward rotation, center is 90, range is from 80..150'''
        self.ver_cur = self._addSat(self.ver_cur, increment, self._ver_min, self._ver_max)
        self._pwm.setServoPwm('1',self.ver_cur)
        if (self.debug):
            print('New vertical angle: %d' % (self.ver_cur))

    def center(self):
        self.hor_cur = 90
        self._pwm.setServoPwm('0',90)
        self.ver_cur = 90
        self._pwm.setServoPwm('1',90)


def check_battery_low(adc, umin = 7, debug = False) -> bool:
    supply_voltage = adc.recvADCAvrg(2) * 3
    if (debug):
        print(str(supply_voltage))
    return (supply_voltage < umin)


def process_stick1(hor: float, ver: float, m: Motor):  

    lon = int(-ver)
    lat = int(hor / 2 )
    m.setMotorModel(lon + lat, lon + lat, lon - lat, lon - lat)


def process_stick2(hor: float, ver: float, serc: ServoControl):
    if hor < -0.95:
        serc.rotate_horizontally(-2)
    elif hor < -0.5:
        serc.rotate_horizontally(-1)
    elif hor > 0.95:
        serc.rotate_horizontally(2)
    elif hor > 0.5:
        serc.rotate_horizontally(1)

    if ver < -0.95:
        serc.rotate_vertically(2)
    elif ver < -0.5:
        serc.rotate_vertically(1)
    elif ver > 0.95:
        serc.rotate_vertically(-2)
    elif ver > 0.5:
        serc.rotate_vertically(-1)

def monitorBattery(myAdc, myBuzzer):
    """Runnable for monitor thread"""
    # TODO: use LEDs to indicate avrg. battery voltage / charge
    global disableMotor

    # read supply voltage
    if check_battery_low(myAdc):
        print("WARNING: Battery voltage is low ( < 7.0V)! Stop Motors!")
        disableMotor = True
        myBuzzer.run('1')   # signal error

    time.sleep(0.05)


if __name__ == '__main__':
    print('Initialize gamepad control...')
    myPad = gamepad.Gamepad()
    myPad.set_scale(.05, 800, .95, 4095)

    print('Initialize motor control...')
    myEngine = Motor.Motor()
    
    print('Initialize servo control ... ')
    myServo = ServoControl(debug = True)

    print('Initialize Buzzer Driver...')
    myBuzzer = Buzzer.Buzzer()

    print('Initialize ADC Driver...')
    myAdc = ADC.Adc()
    Thread_Monitor = threading.Thread(target = monitorBattery, args=[myAdc, myBuzzer])
    Thread_Monitor.start()

    print('Initialize LED Driver...')
    myLed = Led.Led()

    try:
        print('Center camera head...')
        myServo.center()
        time.sleep(2)

        print('Enter 50ms control loop...')
        disableMotor = False
        while True:
            # 1st stick controls the wheel motors
            stick1_hor = myPad.get_axis_scaled(0)
            stick1_ver = myPad.get_axis_scaled(1)
            if not disableMotor:
                process_stick1(stick1_hor, stick1_ver, myEngine)
            else:
                myEngine.stop()
            
            
            # 2nd stick control the camera head
            stick2_hor = myPad.get_axis(2)
            stick2_ver = myPad.get_axis(5)
            process_stick2(stick2_hor, stick2_ver, myServo)


            # TODO: use Gamepad buttons to shutdown rpi
            # TODO: use ultrasonic to implement "follow" mode

            time.sleep(0.05)
    finally:
        myEngine.stop()
        myLed.switchOff()
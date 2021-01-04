import evdev
import pprint
import time

class GamepadNotFound(Exception):
    pass

class GamepadWrongAxis(Exception):
    pass

class GamepadScaleError(Exception):
    pass

class Gamepad:
    def __init__(self):
        devicepaths = evdev.list_devices()
        if len(devicepaths) == 0:
            raise GamepadNotFound

        if len(devicepaths) == 1:
            self.gamepad = evdev.InputDevice(devicepaths[0])
        else:
            while True:
                selection = input('Which input device shall be used (0..' + len(devicepaths) + '?')
                if int(selection) >= 0 and int(selection) < len(devicepaths):
                    break
            self.gamepad = evdev.InputDevice(devicepaths[int(selection)])
            
        self.name = self.gamepad.name
        
        # capabilities[3] contains axes and include a array of tuples: 
        # [(axis number, "AxisInfo"), (axis number, "AxisInfo")
        self.capabilities = self.gamepad.capabilities()
        REL_ABS = 3
        self.capabilities_axes = self.capabilities[REL_ABS]  

        # get the properties of the joystick
        self.num_axis = len(self.capabilities_axes)
        if self.num_axis == 0:
            raise GamepadNotFound
        
        self.axis = [a[0] for a in self.capabilities_axes]
        self.axisinfo = [a[1] for a in self.capabilities_axes]

        # calculate axis info for later normalization and add them to AbsInfo objects
        # TODO: create own AbsNormInfo class which uses AbsInfo as parameter for initialization
        for x in range(self.num_axis):
            ai = self.axisinfo[x]
            ai.width = float(ai.max - ai.min) / 2
            ai.mid = ai.min + ai.width
            ai.incr = 1.0 /ai.width

    def get_axis(self, num: int) -> float:
        ''' returns normalized float (-1 .. 1) position of gamepad axis num
            -1 if left or up
            0 is centered
            +1 is right or down
        '''
        if not num in self.axis:
            raise GamepadWrongAxis
        axis_index = self.axis.index(num)

        pos_raw = self.get_axis_raw(num)
        axisinfo = self.axisinfo[axis_index]

        pos = (pos_raw - axisinfo.mid ) / axisinfo.width

        return pos

    def get_axis_raw(self, num: int) -> int:
        ''' returns raw absolute position of gamepad axis num
            0 is normally left or up,
            128 is normally center, 
            255 is right or down
        '''

        if not num in self.axis:
            raise GamepadWrongAxis
        
        return self.gamepad.absinfo(num).value

    # TODO: store scale axis specific, check if evdev supports something like that
    def set_scale(self, dead_in: float, dead_out: float, max_in: float, max_out: float):
        self.isScaleInit = True

        if dead_in < 0 or dead_in > 1 or max_in < 0 or max_in > 1:
            raise GamepadScaleError
        
        self.scale_dead_in = dead_in
        self.scale_dead_out = dead_out
        self.scale_max_in = max_in
        self.scale_max_out = max_out
        self.scale_width_in = max_in - dead_in
        self.scale_width_out = max_out - dead_out

    def get_axis_scaled(self, num: int) -> float:
        if not self.isScaleInit:
            raise GamepadScaleError

        pos = self.get_axis(num)

        if pos < -self.scale_max_in:
            return -self.scale_max_out
        elif pos < -self.scale_dead_in:
            return -self.scale_dead_out + (pos + self.scale_dead_in) / self.scale_width_in * self.scale_width_out
        elif pos > self.scale_max_in:
            return self.scale_max_out
        elif pos > self.scale_dead_in:
            return self.scale_dead_out + (pos - self.scale_dead_in) / self.scale_width_in * self.scale_width_out
        else:
            return 0

    def __str__(self) -> str:
        return self.gamepad.name

if __name__ == '__main__':
    myPad = Gamepad()
    print(myPad)
    myPad.set_scale(0.05, 800, 0.95, 4095)
    while True:
        for a in myPad.axis:
            print('Axis %d raw value = %d, normalized = %f, scaled = %f' % 
                     (a, myPad.get_axis_raw(a), myPad.get_axis(a), myPad.get_axis_scaled(a)))
        time.sleep(1)
    
    
import time
from PCA9685 import PCA9685
class Motor:
    def __init__(self):
        self.pwm = PCA9685(0x40, debug=True)
        self.pwm.setPWMFreq(50)

    def duty_range(self,duty1,duty2,duty3,duty4):
        if duty1>4095:
            duty1=4095
        elif duty1<-4095:
            duty1=-4095        
        
        if duty2>4095:
            duty2=4095
        elif duty2<-4095:
            duty2=-4095
            
        if duty3>4095:
            duty3=4095
        elif duty3<-4095:
            duty3=-4095
            
        if duty4>4095:
            duty4=4095
        elif duty4<-4095:
            duty4=-4095
        return duty1,duty2,duty3,duty4
        
    def left_Upper_Wheel(self,duty):
        if duty>0:
            self.pwm.setMotorPwm(0,0)
            self.pwm.setMotorPwm(1,duty)
        elif duty<0:
            self.pwm.setMotorPwm(1,0)
            self.pwm.setMotorPwm(0,abs(duty))
        else:
            self.pwm.setMotorPwm(0,4095)
            self.pwm.setMotorPwm(1,4095)
    def left_Lower_Wheel(self,duty):
        if duty>0:
            self.pwm.setMotorPwm(3,0)
            self.pwm.setMotorPwm(2,duty)
        elif duty<0:
            self.pwm.setMotorPwm(2,0)
            self.pwm.setMotorPwm(3,abs(duty))
        else:
            self.pwm.setMotorPwm(2,4095)
            self.pwm.setMotorPwm(3,4095)
    def right_Upper_Wheel(self,duty):
        if duty>0:
            self.pwm.setMotorPwm(6,0)
            self.pwm.setMotorPwm(7,duty)
        elif duty<0:
            self.pwm.setMotorPwm(7,0)
            self.pwm.setMotorPwm(6,abs(duty))
        else:
            self.pwm.setMotorPwm(6,4095)
            self.pwm.setMotorPwm(7,4095)
    def right_Lower_Wheel(self,duty):
        if duty>0:
            self.pwm.setMotorPwm(4,0)
            self.pwm.setMotorPwm(5,duty)
        elif duty<0:
            self.pwm.setMotorPwm(5,0)
            self.pwm.setMotorPwm(4,abs(duty))
        else:
            self.pwm.setMotorPwm(4,4095)
            self.pwm.setMotorPwm(5,4095)
            
 
    def setMotorModel(self,frontLeft,rearLeft,frontRight,rearRight):
        ''' engine speeds range from -4095 .. 4095 '''
        frontLeft,rearLeft,frontRight,rearRight=self.duty_range(frontLeft,rearLeft,frontRight,rearRight)
        self.left_Upper_Wheel(-frontLeft)
        self.left_Lower_Wheel(-rearLeft)
        self.right_Upper_Wheel(-frontRight)
        self.right_Lower_Wheel(-rearRight)

    def stop(self):
        ''' stop all 4 electric motors'''
        self.left_Upper_Wheel(0)
        self.left_Lower_Wheel(0)
        self.right_Upper_Wheel(0)
        self.right_Lower_Wheel(0)
            
            
PWM=Motor()          
def loop(): 
    print('Move forward with 50% speed for 3 sec')
    PWM.setMotorModel(2000,2000,2000,2000)       #Forward
    time.sleep(3)
    print('Move backward with 50% speed for 3 sec')
    PWM.setMotorModel(-2000,-2000,-2000,-2000)   #Back
    time.sleep(3)
    print('Spin left with 50% speed for 3 sec')
    PWM.setMotorModel(-500,-500,2000,2000)       #Left 
    time.sleep(3)
    print('Spin right with 50% speed for 3 sec')
    PWM.setMotorModel(2000,2000,-500,-500)       #Right    
    time.sleep(3)
    print('Stop motors')
    PWM.setMotorModel(0,0,0,0)                   #Stop

def loop_single():
    start = 250
    stop = 1000
    step = 1
    display = 25
    inbetweentime = 0
    
    print('Slowly increase speed on front left wheel...')
    for x in range(start, stop, step):
        PWM.setMotorModel(x,0,0,0)
        time.sleep(0.01)
        if (x % display) == 0:
            print(str(x))
    time.sleep(inbetweentime)

    print('Slowly increase speed on rear left wheel...')
    for x in range(start, stop, step):
        PWM.setMotorModel(0,x,0,0)
        time.sleep(0.01)
        if (x % display) == 0:
            print(str(x))
    time.sleep(inbetweentime)

    print('Slowly increase speed on front right wheel...')
    for x in range(start, stop, step):
        PWM.setMotorModel(0,0,x,0)
        time.sleep(0.01)
        if (x % display) == 0:
            print(str(x))
    time.sleep(inbetweentime)

    print('Slowly increase speed on rear right wheel...')
    for x in range(start, stop, step):
        PWM.setMotorModel(0,0,0,x)
        time.sleep(0.01)
        if (x % display) == 0:
            print(str(x))
    time.sleep(inbetweentime)
    
    PWM.stop()


def destroy():
    PWM.stop()

if __name__=='__main__':
    input('Please lift the car before starting this test as the car will move for 3 seconds in different directions!')

    try:
        loop_single()
        loop()
    except KeyboardInterrupt:  # When 'Ctrl+C' is pressed, the child program destroy() will be  executed.
        destroy()

# -*-coding: utf-8 -*-
import time
from rpi_ws281x import *
# LED strip configuration:
LED_COUNT      = 8      # Number of LED pixels.
LED_PIN        = 18      # GPIO pin connected to the pixels (18 uses PWM!).
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 10      # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 255     # Set to 0 for darkest and 255 for brightest
LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL    = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53

class LedUnknownName(Exception):
    pass

# Define functions which animate LEDs in various ways.
class Led:
    def __init__(self, initial_brightness = 50):
        #Control the sending order of color data
        self.ORDER = "RGB"  
        # Create NeoPixel object with appropriate configuration.
        self.strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
        # Intialize the library (must be called once before other functions).
        self.strip.begin()
        self.strip.setBrightness(initial_brightness)

    @staticmethod
    def LED_TYPR(order,R_G_B):
        B=R_G_B & 255
        G=R_G_B >> 8 & 255
        R=R_G_B >> 16 & 255 
        Led_type=["GRB","GBR","RGB", "RBG","BRG","BGR"]
        color = [Color(G,R,B),Color(G,B,R),Color(R,G,B),Color(R,B,G),Color(B,R,G),Color(B,G,R)]
        if order in Led_type:
            return color[Led_type.index(order)]

    smartcar_pos = {'D12': 0, 'D13': 1, 'D14': 2, 'D15': 3,
                    'D16': 4, 'D17': 5, 'D18': 6, 'D19': 7}    
    smartcar_idx = {'D12': 1, 'D13': 2, 'D14': 4, 'D15': 8,
                    'D16': 0x10, 'D17': 0x20, 'D18': 0x40, 'D19': 0x80}    
    @staticmethod
    def getLedPosition(ledname) -> int:
        """Convert a LED name to it's position in the strip driver"""
        if ledname in Led.smartcar_pos:
            return Led.smartcar_pos[ledname]
        else:
            raise LedUnknownName

    @staticmethod
    def getLedIndex(ledname) -> int:
        """Convert a LED name to it's index in the strip driver"""
        if ledname in Led.smartcar_pos:
            return Led.smartcar_idx[ledname]
        else:
            raise LedUnknownName

    def colorWipe(self,strip, color, wait_ms=50):
        """Wipe color across display a pixel at a time."""
        color=self.LED_TYPR(self.ORDER,color)
        for i in range(self.strip.numPixels()):
            self.strip.setPixelColor(i, color)
            self.strip.show()
            time.sleep(wait_ms/1000.0)

    def theaterChase(self,strip, color, wait_ms=50, iterations=10):
        """Movie theater light style chaser animation."""
        color=self.LED_TYPR(self.ORDER,color)
        for j in range(iterations):
            for q in range(3):
                for i in range(0,self.strip.numPixels(), 3):
                    self.strip.setPixelColor(i+q, color)
                self.strip.show()
                time.sleep(wait_ms/1000.0)
                for i in range(0, self.strip.numPixels(), 3):
                    self.strip.setPixelColor(i+q, 0)

    def wheel(self,pos):
        """Generate rainbow colors across 0-255 positions."""
        if pos<0 or pos >255:
            r=g=b=0
        elif pos < 85:
            r=pos * 3
            g=255 - pos * 3
            b=0
        elif pos < 170:
            pos -= 85
            r=255 - pos * 3
            g=0
            b=pos * 3
        else:
            pos -= 170
            r=0
            g=pos * 3
            b=255 - pos * 3
        return self.LED_TYPR(self.ORDER,Color(r,g,b))

    def rainbow(self,strip, wait_ms=20, iterations=1):
        """Draw rainbow that fades across all pixels at once."""
        for j in range(256*iterations):
            for i in range(self.strip.numPixels()):
                 self.strip.setPixelColor(i, self.wheel((i+j) & 255))
            self.strip.show()
            time.sleep(wait_ms/1000.0)

    def rainbowCycle(self,strip, wait_ms=20, iterations=5):
        """Draw rainbow that uniformly distributes itself across all pixels."""
        for j in range(256*iterations):
            for i in range(self.strip.numPixels()):
                self.strip.setPixelColor(i, self.wheel((int(i * 256 / self.strip.numPixels()) + j) & 255))
            self.strip.show()
            time.sleep(wait_ms/1000.0)

    def theaterChaseRainbow(self,strip, wait_ms=50):
        """Rainbow movie theater light style chaser animation."""
        for j in range(256):
            for q in range(3):
                for i in range(0, self.strip.numPixels(), 3):
                    self.strip.setPixelColor(i+q, self.wheel((i+j) % 255))
                self.strip.show()
                time.sleep(wait_ms/1000.0)
                for i in range(0, strip.numPixels(), 3):
                    strip.setPixelColor(i+q, 0)

    def ledIndex(self,index,R,G,B):
        """Sets multiple LEDs at once to a new color, each bit in index represents one LED"""
        color=self.LED_TYPR(self.ORDER,Color(R,G,B))
        for i in range(8):
            if index & 0x01 == 1:
                self.strip.setPixelColor(i,color)
                self.strip.show()
            index=index >> 1

    def ledMode(self,n):
        self.mode=n
        while True:
            if self.mode=='1':
                self.colorWipe(self.strip, Color(255, 0, 0))  # Red wipe
                self.colorWipe(self.strip, Color(0, 255, 0))  # Green wipe
                self.colorWipe(self.strip, Color(0, 0, 255))  # Blue wipe
                self.colorWipe(self.strip, Color(0,0,0),10)
            elif self.mode=='2':
                self.theaterChaseRainbow(self.strip)
                self.colorWipe(self.strip, Color(0,0,0),10)
            elif self.mode=='3':
                self.rainbow(self.strip)
                self.colorWipe(self.strip, Color(0,0,0),10)
            elif self.mode=='4':
                self.rainbowCycle(self.strip)
                self.colorWipe(self.strip, Color(0,0,0),10)
            else:
                self.colorWipe(self.strip, Color(0,0,0),10)
                break

    def switchOff(self):
        self.ledIndex(0xFF, 0, 0, 0)

    def __del__(self):
        ''' Make sure the LEDs switch off once the program terminates'''
        #FIXME: E/A Access violation occurs, probably because order of object destruction is random
        #self.switchOff()
        pass

if __name__ == '__main__':
    print ('Program is starting ... ')
    try:
        led=Led() 

        led.ledIndex(0xFF,255,255,255)
        print('Current brightness is (0..255): %d' % led.strip.getBrightness())
        try: 
            led.strip.setBrightness(int(input('Set new brightness or press Enter to keep value: ')))
            time.sleep(1)
        except:
            pass
        while True:
            print ("Chaser animation")
            led.colorWipe(led.strip, Color(255,0, 0), wait_ms = 1000)  # Red wipe
            time.sleep(1)
            led.colorWipe(led.strip, Color(0, 255, 0))  # Green wipe
            time.sleep(1)
            led.colorWipe(led.strip, Color(0, 0, 255))  # Blue wipe
            time.sleep(1)
            led.theaterChaseRainbow(led.strip)
            print ("Rainbow animation")
            led.rainbow(led.strip)
            led.rainbowCycle(led.strip)
            led.colorWipe(led.strip, Color(0,0,0),10)
    except KeyboardInterrupt:  # When 'Ctrl+C' is pressed, the child program destroy() will be  executed.
        led.switchOff()

        
            
        
                    




   

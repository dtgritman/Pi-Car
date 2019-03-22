#import evdev
from evdev import InputDevice, ecodes
#import ps4 controller codes
from ps4controllercodes import *
#import rccar to control car
import nitrorccar as rccar
#import other libraries
import time
import os

#control rc car with ps4 controller
def ps4RcCar(car):
    controllerFile = "/dev/input/event2"
    
    while not os.path.exists(controllerFile):
        print("{} - Controller Not Found!".format(time.strftime("%H:%M:%S")))
        for i in range(30):
            if not os.path.exists(controllerFile):
                time.sleep(1)
        time.sleep(1)
    
    #creates object 'controller' to store the data
    controller = InputDevice(controllerFile)
    #prints out device info at start
    print(controller)
    
    #setup variables to track controller
    curL2Trig = 0
    curR2Trig = 0
    curLJs = { "x": 127, "y": 127 }
    
    paused = False
    try:
        #evdev takes care of polling the controller in a loop
        for event in controller.read_loop():
            if event.type == ecodes.EV_KEY:
                if event.code == BTN.option:
                    if event.value == 1:
                        paused = not paused
            
            elif event.type == ecodes.EV_ABS:
                #Range is 0 to 255, Center values are about 127 (up/left: below 127, down/right: above 127)
                if event.code == JS.left_x:
                    curLJs["x"] = event.value
                elif event.code == JS.left_y:
                    curLJs["y"] = event.value
                
                #Range is 0 to 255
                elif event.code == TRIG.hold_l2:
                    curL2Trig = event.value
                elif event.code == TRIG.hold_r2:
                    curR2Trig = event.value
            
            steerPerc = 50
            if curLJs.get("x") < 124 or curLJs.get("x") > 131:
                steerPerc = int((curLJs.get("x") / 255) * 100)
            
            speedPerc = 50
            if curR2Trig > 0:
                speedPerc = speedPerc + ((curR2Trig / 255 / 2) * 100)
            if curL2Trig > 0:
                speedPerc = speedPerc - ((curL2Trig / 255 / 2) * 100)
            
            if paused:
                car.stop()
            else:
                car.setSteering(steerPerc)
                car.setSpeed(speedPerc)
            print("CallSteering: {}, CallSpeed: {}".format(steerPerc, speedPerc))
        
    except OSError:
        print("{} - Controller Disconnected!".format(time.strftime("%H:%M:%S")))
        return False
    
    except KeyboardInterrupt:
        print("\nConnection Closed!")
        return True


#------------ MAIN ------------
car = rccar.RcCar(12, 13, 1000, 2000, 1000, 2000)
if not car.connected:
    print('Failed to connect to car!')

try:
    #create rc car object and setup gun
    while not ps4RcCar(car):
        car.stop()
        time.sleep(5)

except KeyboardInterrupt:
    print("\nConnection Closed!")
        
finally:
    #clean up and stop car
    car.cleanup()
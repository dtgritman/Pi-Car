#import evdev
from evdev import InputDevice, ecodes
#import ps4 controller codes
from ps4controllercodes import *
#import rccar to control car
import rccar
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
    curR1Trig = 0
    curL2Trig = 0
    curR2Trig = 0
    curLJs = { "x": 127, "y": 127 }
    
    paused = False
    try:
        #evdev takes care of polling the controller in a loop
        for event in controller.read_loop():
            if paused:
                if event.type == ecodes.EV_KEY and event.code == BTN.option and event.value == 1:
                    paused = False
                continue
            
            if event.type == ecodes.EV_KEY:
                if event.code == BTN.option:
                    if event.value == 1:
                        car.stop()
                        paused = True
                        print("Input Paused!")
                        continue
                
                elif event.code == TRIG.r1:
                    curR1Trig = event.value
            
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
            
            steerPerc = 50 #curLJs.get("x")
            if curLJs.get("x") < 121 or curLJs.get("x") > 131:
               # steerPerc = curLJs.get("x")
                steerPerc = int((curLJs.get("x") / 255) * 100)
            
            speedPerc = 50
            if curR2Trig > 0:
                speedPerc = speedPerc + ((curR2Trig / 255 / 2) * 100)
            if curL2Trig > 0:
                speedPerc = speedPerc - ((curL2Trig / 255 / 2) * 100)
            
            
            car.setSteering(steerPerc)
            car.setSpeed(speedPerc)
            car.setGun(curR1Trig)
            print("CallGun: {}, CallSteering: {}, CallSpeed: {}".format(curR1Trig, steerPerc, speedPerc))
        
    except OSError:
        print("{} - Controller Disconnected!".format(time.strftime("%H:%M:%S")))
        return False
    
    except KeyboardInterrupt:
        print("\nConnection Closed!")
        return True


#------------ MAIN ------------
car = rccar.RcCar(12, 13, 1000, 2000, 820, 1480)
if not car.connected:
    print('Failed to connect to car!')
car.initializeGun(26, 'HIGH')
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
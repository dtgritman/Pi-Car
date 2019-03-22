#import evdev
from evdev import InputDevice, ecodes
#import pigpio for gpio controls
import pigpio
#import other libraries
import time
import os


#button code variables
xBtn = 304
oBtn = 305
trBtn = 307
sqBtn = 308

up_down = 17
left_right = 16

share = 314
option = 315
ps = 316

l1Trig = 310
l2Trig = 312
l2TrigHold = 2
r1Trig = 311
r2Trig = 313
r2TrigHold = 5

lJsPress = 317
lJsX = 0
lJsY = 1
rJsPress = 318
rJsX = 3
rJsY = 4


#initialize pi for pigpio and check if connected
pi = pigpio.pi()
if not pi.connected:
     print("Pi not connected to pigpio.")
     exit()

#GPIO pin locations
servoPin = 13
motorPin = 12
gunPin = 26

pi.set_mode(gunPin, pigpio.OUTPUT)

#set steering servo min and max pulsewidth
steeringMin = 820
steeringMax = 1480

#set motor min and max pulsewidth
motorMin = 1000
motorMax = 2000


#set steering to the percent given
def setSteering(pwPerC):
    range = steeringMax - steeringMin
    
    #turn off servo if percent is below 0
    if pwPerC < 0:
        pw = 0
    elif pwPerC > 100:
        pwPerC = 100
    else:
        pw = steeringMin + (range * pwPerC / 100)
    
    pi.set_servo_pulsewidth(servoPin, pw)

#set motor speed to the percent given
def setSpeed(pwPerC):
    range = (motorMax - motorMin) / 2
    
    #turn off motor if percent is below 0
    if pwPerC < 0:
        pw = 0
    elif pwPerC > 100:
        pwPerC = 100
    elif pwPerC > 50:
        pw = motorMin + range + (range * .84 * (pwPerC - 50) / 100) + (range * .16)
    elif pwPerC < 50:
        pw = motorMin + range - (range * .84 * (50 - pwPerC) / 100) - (range * .16)
    else:
        pw = motorMin + range
    
    pi.set_servo_pulsewidth(motorPin, pw)

#shoots the gun based on status of 0(off) or 1(on)
def setGun(status):
    if status == 1:
        status = 0
    else:
        status = 1
    pi.write(gunPin, status)
    
def ps4RcCar():
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
    curR1TrigCh = False
    curL2Trig = 0
    curR2Trig = 0
    curLJs = { "x": 127, "y": 127 }
    curRJs = { "x": 127, "y": 127 }
    
    paused = False
    
    try:
        #evdev takes care of polling the controller in a loop
        for event in controller.read_loop():
            curR1TrigCh = False
        
            if event.type == ecodes.EV_KEY:
                if event.code == option:
                    if event.value == 1:
                        paused = not paused
                
                elif event.code == r1Trig:
                    if event.value != curR1Trig:
                        curR1TrigCh = True
                        curR1Trig = event.value
            
            elif event.type == ecodes.EV_ABS:
                #Range is 0 to 255, Center values are about 127 (up/left: below 127, down/right: above 127)
                if event.code == lJsX:
                    curLJs["x"] = event.value
                elif event.code == lJsY:
                    curLJs["y"] = event.value
                
                #Range is 0 to 255
                elif event.code == l2TrigHold:
                    curL2Trig = event.value
                elif event.code == r2TrigHold:
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
                steerPerc = -1
                speedPerc = -1
                curR1Trig = 0
            
            setSteering(steerPerc)
            setSpeed(speedPerc)
            setGun(curR1Trig)
            print("CallGun: {}, CallSteering: {}, CallSpeed: {}".format(curR1Trig, steerPerc, speedPerc))
        
    except OSError:
        print("{} - Controller Disconnected!".format(time.strftime("%H:%M:%S")))
        return False
    except KeyboardInterrupt:
        print("\nConnection Closed!")
        return True


#------------ MAIN ------------
try:
    while not ps4RcCar():
        setSteering(-1)
        setSpeed(-1)
        setGun(0)
        time.sleep(5)

except KeyboardInterrupt:
    print("\nConnection Closed!")
    
finally:
    #Clean up and turn servo/motor off
    setSteering(-1)
    setSpeed(-1)
    setGun(0)
    pi.stop()
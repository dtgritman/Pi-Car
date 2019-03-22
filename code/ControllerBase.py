#import evdev
from evdev import InputDevice, categorize, ecodes

#creates object 'gamepad' to store the data
#you can call it whatever you like
gamepad = InputDevice('/dev/input/event3')

#button code variables (change to suit your device)
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

#prints out device info at start
print(gamepad)

#evdev takes care of polling the controller in a loop
try:
    for event in gamepad.read_loop():
        if event.type == ecodes.EV_KEY:
            if event.value == 1:
                if event.code == xBtn:
                    print("X")
                elif event.code == sqBtn:
                    print("Square")
                elif event.code == trBtn:
                    print("Triangle")
                elif event.code == oBtn:
                    print("O")
                
                elif event.code == share:
                    print("Share")
                elif event.code == option:
                    print("Option")
                elif event.code == ps:
                    print("PS")
                
                elif event.code == l1Trig:
                    print("L1 Trigger")
                #elif event.code == l2Trig:
                #    print("L2 Trigger Press")
                elif event.code == r1Trig:
                    print("R1 Trigger")
                #elif event.code == r2Trig:
                #    print("R2 Trigger Press")
                
                elif event.code == lJsPress:
                    print("Left Joystick Press")
                elif event.code == rJsPress:
                    print("Right Joystick Press")
        elif event.type == ecodes.EV_ABS:
            if event.code == up_down:
                if event.value == -1:
                    print("Up")
                elif event.value == 1:
                    print("Down")
            elif event.code == left_right:
                if event.value == -1:
                    print("Left")
                elif event.value == 1:
                    print("Right")
            
            #Range is 0 to 255, Center values are about 127 (up/left: below 127, down/right: above 127)
            elif event.code == lJsX:
                print("Left Joystick X-Axis : " + str(event.value))
            elif event.code == lJsY:
                print("Left Joystick Y-Axis : " + str(event.value))
            elif event.code == rJsX:
                print("Right Joystick X-Axis : " + str(event.value))
            elif event.code == rJsY:
                print("Right Joystick Y-Axis : " + str(event.value))
            
            #Range is 0 to 255
            elif event.code == l2TrigHold:
                print("L2 Trigger : " + str(event.value))
            elif event.code == r2TrigHold:
                print("R2 Trigger : " + str(event.value))

except OSError:
    print("Controller Disconnected")
except KeyboardInterrupt:
    print("Gud Bye")
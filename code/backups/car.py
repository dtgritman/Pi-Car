#import libraries
import pigpio
import time

#initialize pi for pigpio and check if connected
pi = pigpio.pi()
if not pi.connected:
     print("Pi not connected to pigpio.")
     exit()

#GPIO pin locations
servoPin = 13
motorPin = 12

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

#make the car do a figure eight
def figureEight(t, count):
     setSteering(100)
     setSpeed(80)
     time.sleep(t)
     setSteering(0)
     time.sleep(t)
     if count > 1:
          figureEight(t, count - 1)
     else:
          setSpeed(50)
          setSteering(0)

#activate motor with 50% power to setup esc
setSpeed(50)

try:
     while True:
          command = input("Enter (Controller) (PulseWidthPercent):")
          command = command.split(" ")
          if len(command) == 1 and command[0] == "":
               setSpeed(50)
               continue
          elif len(command) < 2:
               print("Command not recognized. Controller: 0 = Servo, 1 = Motor")
               continue

          try:
               pwPercent = float(command[1])
               if len(command) > 2:
                    input2 = int(command[2])
          except ValueError:
               print("Invalid input for PulseWidthPercent")
               continue

          if command[0] == "0":
               setSteering(pwPercent)
          elif command[0] == "f8":
               figureEight(pwPercent, input2)
          else:
               setSpeed(pwPercent)


except KeyboardInterrupt:
     pass

#Clean up and turn servo/motor off
setSteering(-1)
setSpeed(-1)
pi.stop()

print("\nConnection Closed.")

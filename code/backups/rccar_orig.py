import RPi.GPIO as GPIO
import time as time

GPIO.setmode(GPIO.BCM)
GPIO.setup(12, GPIO.OUT)
GPIO.setup(18, GPIO.OUT)

servo = GPIO.PWM(12, 50)
motor = GPIO.PWM(18, 300)
servo.start(0)
motor.start(0)

try:
     while True:
          command = input("Enter (Controller) (Duty Cycle):")
          command = command.split(" ")
          if len(command) < 2:
               print("Command not recognized. Controller: 0 = Servo, 1 = Motor")
               continue

          try:
               dc = float(command[1])
          except ValueError:
               print("Invalid float input for Duty Cycle")
               continue

          if command[0] == "0":
               servo.ChangeDutyCycle(dc)
          else:
               motor.ChangeDutyCycle(dc)


except KeyboardInterrupt:
     pass

servo.stop()
motor.stop()
GPIO.cleanup()

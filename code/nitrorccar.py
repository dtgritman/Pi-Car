#import pigpio to control servo/motor
import pigpio

class RcCar:
    def __init__(self, motorPin, steeringPin, motorMinPulseWidth, motorMaxPulseWidth, steeringMinPulseWidth, steeringMaxPulseWidth):
        #initialize pi for pigpio and check if connected
        self.pi = pigpio.pi()
        if not self.pi.connected:
            print("Pi not connected to pigpio.")
            self.connected = False
            return
        self.connected = True
        
        #GPIO pin locations
        self.motorPin = motorPin
        self.steeringPin = steeringPin
        
        #set motor min and max pulsewidth
        self.motorMin = motorMinPulseWidth
        self.motorMax = motorMaxPulseWidth
        
        #set steering servo min and max pulsewidth
        self.steeringMin = steeringMinPulseWidth
        self.steeringMax = steeringMaxPulseWidth
        
        #initialize motor with 50% power to initialize Electronic Speed Controller(ESC)
        self.setSpeed(50)
    
    #setup relay controlled gun
    def initializeGun(self, gunPin, relayActiveState='LOW'):
        self.gunPin = gunPin
        self.pi.set_mode(26, pigpio.OUTPUT)
        if relayActiveState.upper() == 'HIGH':
            self.gunStates = [1, 0]
        else:
            self.gunStates = [0, 1]
    
    #set motor speed to the percent given
    def setSpeed(self, percent):
        range = self.motorMax - self.motorMin
        
        #turn off motor if percent is below 0
        if percent < 0:
            pulseWidth = 0
        elif percent > 100:
            percent = 100
        else:
            pulseWidth = self.motorMin + (range * percent / 100)
        
        self.pi.set_servo_pulsewidth(self.motorPin, pulseWidth)
    
    #set steering to the percent given
    def setSteering(self, percent):
        range = self.steeringMax - self.steeringMin
        
        #turn off servo if percent is below 0
        if percent < 0:
            pulseWidth = 0
        elif percent > 100:
            percent = 100
        else:
            pulseWidth = self.steeringMin + (range * percent / 100)
    
        self.pi.set_servo_pulsewidth(self.steeringPin, pulseWidth)
    
    #set gun state (0 = off, 1 = on)
    def setGun(self, state):
        if not hasattr(self, 'gunPin'):
            return
        self.pi.write(self.gunPin, self.gunStates[state])
    
    #stop everything
    def stop(self):
        #turn servo/motor off
        self.setSteering(-1)
        self.setSpeed(-1)
        #turn gun off
        self.setGun(0)
    
    #clean up and stop everything
    def cleanup(self):
        self.stop()
        self.pi.stop()
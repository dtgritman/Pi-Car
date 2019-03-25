#include <unistd.h>
#include <sys/types.h>
#include <fcntl.h>
#include <signal.h>
#include <stdlib.h>
#include <stdbool.h>
#include <stdio.h>
#include <time.h>

#include <pigpiod_if2.h>

//Motor ESC Values
#define MOTOR_ESC 12
#define MOTOR_ESC_MIN 1000
#define MOTOR_ESC_MAX 2000
#define MOTOR_DEADZONE 12

//Steering Servo Values
#define SERVO_STEERING 13
#define SERVO_STEERING_MIN 820
#define SERVO_STEERING_MAX 1480

//Controller Code Types
#define EV_KEY 1
#define EV_ABS 3

//Controller Key Codes
#define EV_KEY_SH 314   // Share
#define EV_KEY_OPT 315  // Option
#define EV_KEY_H 316    // Home

#define EV_KEY_X 304
#define EV_KEY_O 305
#define EV_KEY_T 307    // Triangle
#define EV_KEY_S 308    // Square

    
#define EV_KEY_L1 310
#define EV_KEY_L2 312
#define EV_KEY_R1 311
#define EV_KEY_R2 313

#define EV_KEY_LJS 317  // Left Joystick
#define EV_KEY_RJS 318  // Right Joystick

//Controller ABS Codes
#define EV_ABS_L2 2
#define EV_ABS_R2 5

#define EV_ABS_LJS_X 0  // Left Joystick X
#define EV_ABS_LJS_Y 1  // Left Joystick Y
#define EV_ABS_RJS_X 3  // Right Joystick X
#define EV_ABS_RJS_Y 4  // Right Joystick Y


struct input_event {
    struct timeval time;
    unsigned short type;
    unsigned short code;
    unsigned int value;
};

struct controller_status {
    bool opt;
    bool r1;
    unsigned short l2_pos;
    unsigned short r2_pos;
    unsigned short js_x;
};

static bool keepRunning = true;
void intHandler(int sig) {
    keepRunning = false;
}

static int motorCenter = (MOTOR_ESC_MAX + MOTOR_ESC_MIN) / 2;
static int motorRange = (MOTOR_ESC_MAX - MOTOR_ESC_MIN) / 2;
static int motorDeadZone = (MOTOR_DEADZONE / 100.0) * (MOTOR_ESC_MAX - MOTOR_ESC_MIN) / 2;
//Set motor speed
void setSpeed(int pi, short motorPerc) {
    int pulseWidth = motorCenter;

    if (motorPerc > 100)
        motorPerc = 100;
    
    if (motorPerc < 0)
        pulseWidth = 0;
    else if (motorPerc > 50)
        pulseWidth += motorDeadZone + (motorRange - motorDeadZone) * (motorPerc - 50) / 50.0;
    else if (motorPerc < 50)
        pulseWidth -= motorDeadZone + (motorRange - motorDeadZone) * (50 - motorPerc) / 50.0;
    
    set_servo_pulsewidth(pi, MOTOR_ESC, pulseWidth);
}

//Set steering angle
void setSteering(int pi, short steeringPerc) {
    int pulseWidth = 0;
    
    if (steeringPerc > 100)
        steeringPerc = 100;
    if (steeringPerc >= 0)
        pulseWidth = SERVO_STEERING_MIN + ((SERVO_STEERING_MAX - SERVO_STEERING_MIN) * steeringPerc / 100);
    
    set_servo_pulsewidth(pi, SERVO_STEERING, pulseWidth);
}

void stopCar(int pi) {
    setSpeed(pi, -1);
    setSteering(pi, -1);
}

int main() {
    struct sigaction sig;
    sig.sa_handler = intHandler;
    sigaction(SIGINT, &sig, NULL);
    
    struct input_event event;
    int pi, fd, speedPerc, steeringPerc;
    clock_t startTime;
    struct controller_status controllerStat = {0,0,0,0,0};
    
    pi = pigpio_start(NULL, NULL);
    fd = open("/dev/input/event2", O_RDONLY);
    
    bool paused = false;
    while (keepRunning) {
        if (fd == -1) {
            printf("Controller Not Found!\n");
            startTime = time(NULL);
            while (keepRunning && fd == -1 && time(NULL) - startTime < 20) {
                fd = open("/dev/input/event2", O_RDONLY);
                sleep(1);
            }
            continue;
        }
        if (read(fd, &event, sizeof(struct input_event)) != sizeof(struct input_event)) {
            printf("Controller Disconnected!\n");
            close(fd);
            fd = open("/dev/input/event2", O_RDONLY);
            continue;
        }
        
        if (event.type == EV_KEY) {
            if (event.code == EV_KEY_OPT)
                controllerStat.opt = event.value;
            else if (event.code == EV_KEY_R1)
                controllerStat.r1 = event.value;
        }
        else if (event.type == EV_ABS) {
            if (event.code == EV_ABS_L2)
                controllerStat.l2_pos = event.value;
            else if (event.code == EV_ABS_R2)
                controllerStat.r2_pos = event.value;
            else if (event.code == EV_ABS_RJS_X)
                controllerStat.js_x = event.value;
        }
        
        if (controllerStat.opt == 1) {
            //Reset option status to 0 to prevent multiple calls if held
            controllerStat.opt = 0;
            paused = !paused;
            if (paused) {
                stopCar(pi);
                printf("Paused!\n");
            }
            continue;
        }
        
        if (paused)
            continue;
        
        steeringPerc = 50;
        if (controllerStat.js_x < 121 || controllerStat.js_x > 131)
            steeringPerc = (controllerStat.js_x / 255.0) * 100;
        setSteering(pi, steeringPerc);
        
        speedPerc = 50;
        if (controllerStat.r2_pos > 0)
            speedPerc += (controllerStat.r2_pos / 255.0) * 50;
        if (controllerStat.l2_pos > 0)
            speedPerc -= (controllerStat.l2_pos / 255.0) * 50;
        setSpeed(pi, speedPerc);
        
        if (event.code == EV_KEY_OPT || event.code == EV_KEY_R1 || event.code == EV_ABS_L2 || event.code == EV_ABS_R2 || event.code == EV_ABS_RJS_X)
            printf("shoot: %u | setSpeed: %u | setSteering: %u\n", controllerStat.r1, speedPerc, steeringPerc);
    }
    
    printf("\nExiting!\n");
    stopCar(pi);
    pigpio_stop(pi);
    close(fd);
    
    return 0;
}
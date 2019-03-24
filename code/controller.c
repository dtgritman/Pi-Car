#include <stdio.h>
#include <unistd.h>
#include <sys/types.h>
#include <fcntl.h>
#include <stdbool.h>

#include <pigpiod_if2.h>


#define MOTOR_ESC 12
#define SERVO_STEERING 13

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



int main() {
    struct input_event event;
    int pi, fd;
    
    pi = pigpio_start(NULL, NULL);
    
    /*
    set_PWM_frequency(pi, SERVO_STEERING, 300);
    set_servo_pulsewidth(pi,SERVO_STEERING, 1300);
    sleep(3);
    set_servo_pulsewidth(pi,SERVO_STEERING, 1100);
    sleep(3);
    
    set_servo_pulsewidth(pi,SERVO_STEERING, 0);
    */
    pigpio_stop(pi);
    
    
    fd = open("/dev/input/event2", O_RDONLY);
    if (fd == -1) {
        printf("Error opening file\n");
        return -1;
    }
    
    struct controller_status statController = {0,0,0,0,0,0};
    
    bool paused = false;
    while (!paused) {
        read(fd, &event, sizeof(struct input_event));
        if (event.type == EV_KEY) {
            if (event.code == EV_KEY_OPT) {
                if (event.value == 1) {
                    paused = true;
                    printf("PAUSE TOGGLE\n");
                }
            }
            else if (event.code == EV_KEY_R1) {
                if (event.value == 1)
                    printf("SHOOT\n");
            }
        }
        else if (event.type == EV_ABS) {
            if (event.code == EV_ABS_L2)
                printf("L2: %u\n", event.value);
            else if (event.code == EV_ABS_R2)
                printf("R2: %u\n", event.value);
            
            else if (event.code == EV_ABS_RJS_X)
                printf("RJS_X: %u\n", event.value);
        }
    }
    
    close(fd);
    
    return 0;
}
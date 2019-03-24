# Pi-Car
Raspberry Pi controlled rc car

### Setup:
###### Dependencies:
 pigpio - `sudo apt-get install pigpio python-pigpio python3-pigpio gcc` (run on startup use `sudo systemctl enable pigpiod` otherwise use `sudo pigpiod` before use)

###### Add User to these groups to run without sudo:
 add user to the input group with `sudo usermod -a -G input <username>` to read evdev
 add user to the bluetooth group with `sudo usermod -a -G bluetooth <username>`
 then relog
 
###### Connecting Bluetooth controller (ps4 controller in this case):
 set bluetooth to start on boot with `sudo systemctl enable bluetooth`
 then reboot
 then use `bluetoothctl`
 then use `agent on`
 then use `default-agent`
 then use `scan on`
 find the controller address and use `pair <XX:XX:XX:XX:XX:XX>`
 then use `trust <XX:XX:XX:XX:XX:XX>

#### C Specific Setup:
 Compile using `gcc -Wall -pthread -o controller controller.c -lpigpiod_if2 -lrt`

#### Python Specific Setup:
###### Dependencies:
 evdev - `sudo apt-get install python-dev python-pip python3-pip` next use -> `sudo pip install evdev` next use -> `sudo pip3 install ev-dev`

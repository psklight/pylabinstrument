from pyoptics.thorlabs.motion import KCubeDCServo as kdc
from time import sleep

motor = kdc.Motor(27002550)
motor.verbose = True
motor.open()

# perform homing
motor.home()

sleep(60) # wait for 60 seconds for homing to finish. more time might be nedded.

motor.moveToPosition(2) # move to 2-mm position

sleep(10)

pos = motor.getPosition()
print('Position: {}'.format(pos))
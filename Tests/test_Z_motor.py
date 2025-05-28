from ControlMotors import ControlStage
import time

# Connect to the Arduino
port_arduino = 'COM10'
stage = ControlStage(port_arduino, [1, 100, 1])

# Enable the stage movement
stage.handle_enable(1)

# Set and perform homing
stage.handle_set_homing()  # Y first, then X, skip Z
stage.handle_homing()

time.sleep(60) #TODO: wait for homing to complete

# Move the stage to a specific position
stage.handle_moveto(2000, 0, 0, 10) #dt, x, y, z

# Move the stage with relative displacement
stage.handle_move(2000, 0, 0, 10) #dt,dx,dy,dz

# Reset the stage controller after execution
stage.close()


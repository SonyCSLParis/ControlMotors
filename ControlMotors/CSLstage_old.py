"""
  Motorised Stage

  Copyright (C) 2021 Sony Computer Science Laboratories
  Author(s) Ali Ruyer-Thompson, Aliénor Lahlou, Peter Hanappe

  Motorised Stage allows to control the position of a microscope stage.

  Motorised Stage is free software: you can redistribute it and/or modify
  it under the terms of the GNU Public License as published by
  the Free Software Foundation, either version 3 of the License, or
  (at your option) any later version.

  This program is distributed in the hope that it will be useful, but
  WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
  General Public License for more details.

  You should have received a copy of the GNU General Public License
  along with this program.  If not, see
  <http://www.gnu.org/licenses/>.

"""


from CSLserial import ControlSerial

import time
import json
import traceback
import numpy as np

        
class ControlStage:
    def __init__(self, arduino_port, gears):
        
        self.x = 0
        self.y = 0
        self.z = 0
        self.gears = gears
        self.arduino_port = arduino_port

        self.link = ControlSerial(self.arduino_port)

        self.backlash_pos = 1#300
        self.backlash_neg = -1#-300




    def handle_enable(self, enable):
        # Enable or diable to allow automatic or manual command
        # respectively
        self.link.send_command("E[%d]"%int(enable))



    def handle_moveto(self, t, x, y, z=0):
        """move the motor to absolute position"""
        self.link.send_command("m[%d,%d,%d,%d]" % (t, x, y, z))


    def handle_move(self, dt, dx, dy, dz=0):
        """move the motor by relative displacement"""
        self.link.send_command("M[%d,%d,%d,%d]" % (dt, dx, dy, dz))


    def handle_pause(self):
        """pause after the ongoing moving task"""
        self.link.send_command("p")


    def handle_continue(self):
        """restart after pause"""
        self.link.send_command("c")


    def send_idle(self):
        """assert the connection is correctly established"""
        reply = self.link.send_command("I")
        return reply[1]

    def handle_set_homing(self, a=2, b=-1, c=-1):
        """configure the homing order. x:0, y:1, z:2, skip:-1. 
        Example: set y, then x: handle_set_homing(link, 1, 0, -1)"""
        self.link.send_command("h[%d,%d,%d]" % (a,b,c))


    def handle_homing(self):
        """perform homing in the order set by "handle_set_homing"""
        self.link.send_command("H")

    def close(self):
        self.link.driver.close()


    # X displacement
    def move_dx(self, dx, dt=-1) :

        if dt == -1:
            # Adjust displacement speed according to the displacement
            # length dx
            dt = dx // self.gears[0]
            if np.abs(dt) < 10: dt = 10
        # Send commmand to the Arduino
        self.handle_move(np.abs(dt), dx, 0, 0) 
        self.x += dx / self.gears[0]


        
    # Y displacement
    def move_dy(self, dy, dt = -1) :

        if dt == -1:
            # Adjust displacement speed according to the displacement
            # length dy (considering the gearbox with ration x100)
            dt = dy // self.gears[1]
            if np.abs(dt) < 10: dt = 10
        # Send commmand to the Arduino
        self.handle_move(np.abs(dt), 0, dy, 0) 
        self.y += dy // self.gears[1]
        # Allows to display the global y displacement

        
    # Z displacement
    def move_dz(self, dz, dt=-1) :

        if dt == -1:
            # Adjust displacement speed according to the displacement
            # length dx
            dt = dz // self.gears[2]
            if np.abs(dt) < 10: dt = 10
        # Send command to the Arduino
        self.handle_move(np.abs(dt), 0, 0, dz) 
        self.z += dz // self.gears[2]
        # Allows to display the global x displacement

    def reset(self):
        self.link.close()


if __name__ == "__main__":

    port_arduino = 'COM6'
    stage = CSLstage(port_arduino, [1, 100, 1])

    stage.link.reset_arduino()
    #handle_moveto(link_arduino, 2000, 1600, 0, 0)



    stage.handle_enable(1)
    stage.handle_set_homing()
    stage.handle_homing()
    """
    stage.handle_move(6000, 1600, 1600, 1600) 

    stage.handle_pause() #ici mettre la fonction pause

    time.sleep(5.0)

    stage.handle_continue() 

    stage.handle_move(6000, -1600, -1600, -1600)
    #check si on est 
    stage.handle_enable(1)

    status = stage.send_idle()
    print(status)

    """
    stage.reset() 

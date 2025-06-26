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
import numpy as np
import tkinter as tk
import argparse
from ControlMotors import ControlStage
import sys



def interface_motors(stage):

    """--------Params-----------"""

    root = tk.Tk()
    root.title('Command interface')
    frame = tk.Frame(root, bg="white")
    frame.pack()


    column_x = 0
    column_y = 2
    column_z = 4

    row_100 = 4
    row_50 = 5
    row_10 = 6

    bg_x = "#de007f"
    bg_y = "#0098e1"
    bg_z = "#292a80"

    fg_x = "white"
    fg_y = "white"
    fg_z = "white"

    var_x = tk.StringVar()
    var_y = tk.StringVar()
    var_z = tk.StringVar()

    var_x.set("x = " + str(stage.x)) 
    var_y.set("y = " + str(stage.y)) 
    var_z.set("z = " + str(stage.z)) 




    def move_dx(dx, dt=-1, var_x = var_x):
        stage.move_dz(dx, dt)
        # Allows to display the global x displacement
        var_x.set("x = " + str(stage.x)) 

    def move_dy(dy, dt=-1, var_y = var_y):
        stage.move_dy(dy, dt)
        # Allows to display the global y displacement
        var_y.set("y = " + str(stage.y))     
        
    def move_dz(dz, dt=-1, var_z = var_z):
        stage.move_dz(dz, dt)
        # Allows to display the global z displacement
        var_z.set("z = " + str(stage.z)) 

    def move_x_entry(): #move using user input value
        dx = int(entry_x.get())
        move_dx(dx, dt=-1)


    def move_y_entry(): #move using user input value
        dy = int(entry_y.get())
        move_dy(dy, dt = -1)


    def move_z_entry(): #move using user input value
        dz = int(entry_z.get())
        stage.move_dz(dz, dt = -1)


        
    def toggle(): #Enable or disable motor control
        if enable_button.config('text')[-1] == 'Enable':
            stage.handle_enable(1)
            enable_button.config(text='Disable')
        else:
            stage.handle_enable(0)
            enable_button.config(text='Enable')

    """--------Buttons-----------"""


    # Leave the app

    quit_button = tk.Button(frame, text="Quit", fg="black", bg="white", command=sys.exit)
    quit_button.grid(column=0, row=2, ipadx=5, pady=5)

    # Enable or disable motors

    enable_button = tk.Button(frame, text="Enable", bg="white", fg="black", command=toggle)
    enable_button.grid(column= 1, row=2, ipadx=5, pady=5)

    # Get global displacement values x and y

    label_x = tk.Label(frame, textvariable = var_x, bg="white") #shows as text in the window
    label_x.grid(column=3, row=0, ipadx=5, pady=5)


    label_y = tk.Label(frame, textvariable = var_y, bg="white") #shows as text in the window
    label_y.grid(column=3, row=1, ipadx=5, pady=5)

    label_z = tk.Label(frame, textvariable = var_z, bg="white") #shows as text in the window
    label_z.grid(column=3, row=2, ipadx=5, pady=5)

    # User inputs valus and clicks to move

    entry_x = tk.Entry(frame, width=6)
    entry_x.grid(column=4, row=0, ipadx=5, pady=5 )    
    user_x = tk.Button(frame, text = 'move x', command = move_x_entry, bg="white")
    user_x.grid(column=5, row=0, ipadx=5, pady=5 )

    entry_y = tk.Entry(frame, width=6)
    entry_y.grid(column=4, row=1, ipadx=5, pady=5 )    
    user_y = tk.Button(frame, text = 'move y', command = move_y_entry, bg="white")
    user_y.grid(column=5, row=1, ipadx=5, pady=5 )

    entry_z = tk.Entry(frame, width=6)
    entry_z.grid(column=4, row=2, ipadx=5, pady=5 )    
    user_z = tk.Button(frame, text = 'move z', command = move_z_entry, bg="white")
    user_z.grid(column=5, row=2, ipadx=5, pady=5 )

    # Predefined movements x and y (+/- 100, 50 or 10)

    button2 = tk.Button(frame,
                    text="x - 100", fg=fg_x, bg=bg_x,
                    command = lambda : move_dx(-100, -1))
    button2.grid(column=column_x, row=row_100, ipadx=5, pady=5)

    button3 = tk.Button(frame,
                    text="x - 50", fg=fg_x, bg=bg_x,
                    command = lambda : move_dx( -50, -1))
    button3.grid(column=column_x, row=row_50, ipadx=5, pady=5)

    button4 = tk.Button(frame,
                    text="x - 10", fg=fg_x, bg=bg_x,
                    command = lambda :  move_dx( -10, -1))
    button4.grid(column=column_x, row=row_10, ipadx=5, pady=5)

    button5 = tk.Button(frame,
                    text="x + 10", fg=fg_x, bg=bg_x,
                    command = lambda :  move_dx( 10, -1))
    button5.grid(column=column_x+1, row=row_10, ipadx=5, pady=5)

    button6 = tk.Button(frame,
                    text="x + 50", fg=fg_x, bg=bg_x,
                    command = lambda :  move_dx( 50, -1))
    button6.grid(column=column_x+1, row=row_50, ipadx=5, pady=5)

    button7 = tk.Button(frame,
                    text="x + 100", fg=fg_x, bg=bg_x,
                    command = lambda :  move_dx( 100, -1))
    button7.grid(column=column_x+1, row=row_100, ipadx=5, pady=5)

    #

    button8 = tk.Button(frame,
                    text="y - 100", fg=fg_y, bg=bg_y,
                    command = lambda :  move_dy( -100, -1))
    button8.grid(column=column_y, row=row_100, ipadx=5, pady=5)

    button9 = tk.Button(frame,
                    text="y - 50", fg=fg_y, bg=bg_y,
                    command = lambda :  move_dy( -50, -1))
    button9.grid(column=column_y, row=row_50, ipadx=5, pady=5)

    button10 = tk.Button(frame,
                    text="y - 10", fg=fg_y, bg=bg_y,
                    command = lambda :  move_dy( -10, -1))
    button10.grid(column=column_y, row=row_10, ipadx=5, pady=5)

    button11 = tk.Button(frame,
                    text="y + 10", fg=fg_y, bg=bg_y,
                    command = lambda :  move_dy( 10, -1))
    button11.grid(column=column_y+1, row=row_10, ipadx=5, pady=5)

    button12 = tk.Button(frame,
                    text="y + 50", fg=fg_y, bg=bg_y,
                    command = lambda :  move_dy( 50, -1))
    button12.grid(column=column_y+1, row=row_50, ipadx=5, pady=5)

    button13 = tk.Button(frame,
                    text="y + 100", fg=fg_y, bg=bg_y,
                    command = lambda :  move_dy( 100, -1))
    button13.grid(column=column_y+1, row=row_100, ipadx=5, pady=5)

    #

    button14 = tk.Button(frame,
                    text="z - 100", fg=fg_z, bg=bg_z,
                    command = lambda :  move_dz( -100, -1))
    button14.grid(column=column_z, row=row_100, ipadx=5, pady=5)

    button15 = tk.Button(frame,
                    text="z - 50", fg=fg_z, bg=bg_z,
                    command = lambda :  move_dz( -50, -1))
    button15.grid(column=column_z, row=row_50, ipadx=5, pady=5)

    button16 = tk.Button(frame,
                    text="z - 10", fg=fg_z, bg=bg_z,
                    command = lambda :  move_dz( -10, -1))
    button16.grid(column=column_z, row=row_10, ipadx=5, pady=5)

    button17 = tk.Button(frame,
                    text="z + 10", fg=fg_z, bg=bg_z,
                    command = lambda :  move_dz( 10, -1))
    button17.grid(column=column_z+1, row=row_10, ipadx=5, pady=5)

    button18 = tk.Button(frame,
                    text="z + 50", fg=fg_z, bg=bg_z,
                    command = lambda :  move_dz( 50, -1))
    button18.grid(column=column_z+1, row=row_50, ipadx=5, pady=5)

    button19 = tk.Button(frame,
                    text="z + 100", fg=fg_z, bg=bg_z,
                    command = lambda :  move_dz( 100, -1))
    button19.grid(column=column_z+1, row=row_100, ipadx=5, pady=5)



    root.mainloop()



if __name__ == "__main__":
    

    parser = argparse.ArgumentParser(prog = 'Motorized Stage')
    parser.add_argument('--port', default='COM6')
    args = parser.parse_args()


    x = 0
    y = 0
    z = 0
    gears = [1, 100, 1]

    arduino_port = args.port
    stage = ControlStage(arduino_port, gears)

    interface_motors(stage)

    """
    from ControlStage import ControlStage
    from ControlStage.interface_motors import interface_motors

    x = 0
    y = 0
    z = 0
    gears = [1, 100, 1]

    arduino_port = "COM6"
    stage = ControlStage(arduino_port, gears)

    interface_motors(stage)
    """
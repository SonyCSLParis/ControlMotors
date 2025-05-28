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
from serial import *
from python_serial import *
import numpy as np
import tkinter as tk
import argparse


parser = argparse.ArgumentParser(prog = 'Motorized Stage')
parser.add_argument('--port', default='COM5')
args = parser.parse_args()


x = 0
y = 0
z = 0
gears = [1, 1, 1]

link = Serial(args.port, 115200)
time.sleep(2.0)
handle_enable(link, 0)

"""--------Useful functions-------------"""
        
# X displacement
def move_dx(link, dx, dt=-1) :
    global x
    global var_x
    if dt == -1:
        # Adjust displacement speed according to the displacement
        # length dx
        dt = dx * 10 // gears[0]
        if np.abs(dt) < 10: dt = 10
    # Send commmand to the Arduino
    handle_move(link, np.abs(dt), dx, 0, 0) 
    x += dx / gears[0]
    # Allows to display the global x displacement
    var_x.set("x = " + str(x)) 

    
# Y displacement
def move_dy(link, dy, dt = -1) :
    global y
    global var_y
    if dt == -1:
        # Adjust displacement speed according to the displacement
        # length dy (considering the gearbox with ration x100)
        dt = dy * 10 // gears[1]
        if np.abs(dt) < 10: dt = 10
    # Send commmand to the Arduino
    handle_move(link, np.abs(dt), 0, dy, 0) 
    y += dy // gears[1]
    # Allows to display the global y displacement
    var_y.set("y = " + str(y)) 

    
# Z displacement
def move_dz(link, dz, dt=-1) :
    global z
    global var_z
    if dt == -1:
        # Adjust displacement speed according to the displacement
        # length dx
        dt = dz * 10 // gears[2]
        if np.abs(dt) < 10: dt = 10
    # Send commmand to the Arduino
    handle_move(link, np.abs(dt), 0, 0, dz) 
    z += dz // gears[2]
    # Allows to display the global x displacement
    var_z.set("z = " + str(z)) 

    
def move_x_entry(): #move using user input value
    dx = np.int(entry_x.get())
    move_dx(link, dx, dt=-1)


def move_y_entry(): #move using user input value
    dy = np.int(entry_y.get())
    move_dy(link, dy, dt = -1)


def move_z_entry(): #move using user input value
    dz = np.int(entry_z.get())
    move_dz(link, dz, dt = -1)


    
def toggle(): #Enable or disable motor control
    if enable_button.config('text')[-1] == 'Enable':
        handle_enable(link, 1)
        enable_button.config(text='Disable')
    else:
        handle_enable(link, 0)
        enable_button.config(text='Enable')


"""--------Buttons-----------"""

root = tk.Tk()
root.title('Command interface')
frame = tk.Frame(root, bg="white")
frame.pack()


column_x = 0;
column_y = 2;
column_z = 4;

row_100 = 4;
row_50 = 5;
row_10 = 6;

bg_x = "#de007f"
bg_y = "#0098e1"
bg_z = "#292a80"

fg_x = "white"
fg_y = "white"
fg_z = "white"


# Leave the app

quit_button = tk.Button(frame, text="Quit", fg="black", bg="white", command=quit)
quit_button.grid(column=0, row=2, ipadx=5, pady=5)

# Enable or disable motors

enable_button = tk.Button(frame, text="Enable", bg="white", fg="black", command=toggle)
enable_button.grid(column= 1, row=2, ipadx=5, pady=5)

# Get global displacement values x and y

var_x = tk.StringVar()
label_x = tk.Label(frame, textvariable = var_x, bg="white") #shows as text in the window
label_x.grid(column=3, row=0, ipadx=5, pady=5)

var_y = tk.StringVar()
label_y = tk.Label(frame, textvariable = var_y, bg="white") #shows as text in the window
label_y.grid(column=3, row=1, ipadx=5, pady=5)

var_z = tk.StringVar()
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
                   command = lambda :move_dx(link, -100, -1))
button2.grid(column=column_x, row=row_100, ipadx=5, pady=5)

button3 = tk.Button(frame,
                   text="x - 50", fg=fg_x, bg=bg_x,
                   command = lambda :move_dx(link, -50, -1))
button3.grid(column=column_x, row=row_50, ipadx=5, pady=5)

button4 = tk.Button(frame,
                   text="x - 10", fg=fg_x, bg=bg_x,
                   command = lambda : move_dx(link, -10, -1))
button4.grid(column=column_x, row=row_10, ipadx=5, pady=5)

button5 = tk.Button(frame,
                   text="x + 10", fg=fg_x, bg=bg_x,
                   command = lambda : move_dx(link, 10, -1))
button5.grid(column=column_x+1, row=row_10, ipadx=5, pady=5)

button6 = tk.Button(frame,
                   text="x + 50", fg=fg_x, bg=bg_x,
                   command = lambda : move_dx(link, 50, -1))
button6.grid(column=column_x+1, row=row_50, ipadx=5, pady=5)

button7 = tk.Button(frame,
                   text="x + 100", fg=fg_x, bg=bg_x,
                   command = lambda : move_dx(link, 100, -1))
button7.grid(column=column_x+1, row=row_100, ipadx=5, pady=5)

#

button8 = tk.Button(frame,
                   text="y - 100", fg=fg_y, bg=bg_y,
                   command = lambda : move_dy(link, -100, -1))
button8.grid(column=column_y, row=row_100, ipadx=5, pady=5)

button9 = tk.Button(frame,
                   text="y - 50", fg=fg_y, bg=bg_y,
                   command = lambda : move_dy(link, -50, -1))
button9.grid(column=column_y, row=row_50, ipadx=5, pady=5)

button10 = tk.Button(frame,
                   text="y - 10", fg=fg_y, bg=bg_y,
                   command = lambda : move_dy(link, -10, -1))
button10.grid(column=column_y, row=row_10, ipadx=5, pady=5)

button11 = tk.Button(frame,
                   text="y + 10", fg=fg_y, bg=bg_y,
                   command = lambda : move_dy(link, 10, -1))
button11.grid(column=column_y+1, row=row_10, ipadx=5, pady=5)

button12 = tk.Button(frame,
                   text="y + 50", fg=fg_y, bg=bg_y,
                   command = lambda : move_dy(link, 50, -1))
button12.grid(column=column_y+1, row=row_50, ipadx=5, pady=5)

button13 = tk.Button(frame,
                   text="y + 100", fg=fg_y, bg=bg_y,
                   command = lambda : move_dy(link, 100, -1))
button13.grid(column=column_y+1, row=row_100, ipadx=5, pady=5)

#

button14 = tk.Button(frame,
                   text="z - 100", fg=fg_z, bg=bg_z,
                   command = lambda : move_dz(link, -100, -1))
button14.grid(column=column_z, row=row_100, ipadx=5, pady=5)

button15 = tk.Button(frame,
                   text="z - 50", fg=fg_z, bg=bg_z,
                   command = lambda : move_dz(link, -50, -1))
button15.grid(column=column_z, row=row_50, ipadx=5, pady=5)

button16 = tk.Button(frame,
                   text="z - 10", fg=fg_z, bg=bg_z,
                   command = lambda : move_dz(link, -10, -1))
button16.grid(column=column_z, row=row_10, ipadx=5, pady=5)

button17 = tk.Button(frame,
                   text="z + 10", fg=fg_z, bg=bg_z,
                   command = lambda : move_dz(link, 10, -1))
button17.grid(column=column_z+1, row=row_10, ipadx=5, pady=5)

button18 = tk.Button(frame,
                   text="z + 50", fg=fg_z, bg=bg_z,
                   command = lambda : move_dz(link, 50, -1))
button18.grid(column=column_z+1, row=row_50, ipadx=5, pady=5)

button19 = tk.Button(frame,
                   text="z + 100", fg=fg_z, bg=bg_z,
                   command = lambda : move_dz(link, 100, -1))
button19.grid(column=column_z+1, row=row_100, ipadx=5, pady=5)


var_x.set("x = " + str(x)) 
var_y.set("y = " + str(y)) 
var_z.set("z = " + str(z)) 


root.mainloop()

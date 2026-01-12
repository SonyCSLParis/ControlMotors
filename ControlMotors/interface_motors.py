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
from tkinter import ttk, messagebox
import argparse
from ControlMotors import ControlStage
import sys
from serial.tools import list_ports
import threading



def interface_motors(stage=None):

    """--------Params-----------"""

    root = tk.Tk()
    root.title('Command interface')
    # Medium-sized window
    root.geometry("450x340")
    frame = tk.Frame(root, bg="white")
    frame.pack(padx=10, pady=10, fill="both", expand=True)


    column_x = 0
    column_y = 2
    column_z = 4

    # Rows for the large movement buttons (leave extra space for header/controls)
    row_100 = 5
    row_50 = 6
    row_10 = 7

    bg_x = "#de007f"
    bg_y = "#0098e1"
    bg_z = "#292a80"

    fg_x = "white"
    fg_y = "white"
    fg_z = "white"

    var_x = tk.StringVar()
    var_y = tk.StringVar()
    var_z = tk.StringVar()

    # Gear ratio variables (motor-steps per stage-step)
    gear_x_var = tk.StringVar(value="1")
    gear_y_var = tk.StringVar(value="100")
    gear_z_var = tk.StringVar(value="1")

    # Simple connection status text
    status_var = tk.StringVar(value="Not connected")

    # Initial values before connection
    if stage is not None:
        var_x.set("x = " + str(stage.x)) 
        var_y.set("y = " + str(stage.y)) 
        var_z.set("z = " + str(stage.z)) 
        # If a stage is provided, initialise gear boxes from its gears
        if hasattr(stage, "gears") and len(stage.gears) >= 3:
            try:
                gear_x_var.set(str(stage.gears[0]))
                gear_y_var.set(str(stage.gears[1]))
                gear_z_var.set(str(stage.gears[2]))
            except Exception:
                # Fall back to defaults if anything goes wrong
                pass
    else:
        var_x.set("x = ?")
        var_y.set("y = ?")
        var_z.set("z = ?")


    # ---- Serial port selector inside the interface ----

    selected_port = tk.StringVar()
    # Prevent concurrent scans
    busy = False

    def refresh_ports():
        ports = list_ports.comports()
        devices = [p.device for p in ports]
        combo_ports["values"] = devices
        if devices:
            selected_port.set(devices[0])
        else:
            selected_port.set("")

    def _scan_ports_worker(gears):
        nonlocal stage, busy
        print("[Oquam] Starting port scan...")
        ports = list_ports.comports()
        if not ports:
            print("[Oquam] No serial ports found.")
            def no_ports():
                nonlocal busy
                busy = False
                status_var.set("No serial ports found")
                btn_connect.configure(state=tk.NORMAL)
                messagebox.showwarning("No ports", "No serial ports found. Connect the Arduino and refresh.")
            root.after(0, no_ports)
            return

        # Prefer ports that look like Arduino/Oquam devices, but fall back to all
        def is_arduino_like(p):
            desc = (p.description or "").lower()
            hwid = (p.hwid or "").lower()
            # Common Arduino/USB-serial identifiers
            keys = ["arduino", "wchusbserial", "usb-serial", "usb serial", "ch340", "ftdi"]
            return any(k in desc or k in hwid for k in keys)

        arduino_like = [p for p in ports if is_arduino_like(p)]
        candidates = arduino_like or ports

        selected = selected_port.get().strip()
        def sort_key(p):
            return 0 if selected and p.device == selected else 1
        candidates = sorted(candidates, key=sort_key)

        last_error = None
        for p in candidates:
            port_name = p.device
            desc = p.description or ""
            print(f"[Oquam] Trying port {port_name} ({desc})...")

            # Skip obvious Bluetooth / non-serial virtual ports that tend to block
            if "bluetooth" in desc.lower():
                print(f"[Oquam] Skipping {port_name} because it looks like a Bluetooth port.")
                continue
            try:
                new_stage = ControlStage(port_name, list(gears))
            except Exception as e:
                print(f"[Oquam] Failed to open {port_name}: {e}")
                last_error = e
                continue

            try:
                driver = new_stage.link.get_driver()
                encoder = new_stage.link.encoder

                old_timeout = getattr(driver, "timeout", None)
                driver.timeout = 1.0

                try:
                    command = encoder.convert('?',)
                    driver.write(command.encode('ascii'))
                    raw = driver.readline()
                finally:
                    driver.timeout = old_timeout

                reply = raw.decode('ascii', errors='ignore').strip()
                print(f"[Oquam] Reply on {port_name}: {reply!r}")
                if not reply.startswith('#?[0,"Oquam'):
                    raise RuntimeError(f"Unexpected identification frame on {port_name}: {reply}")

                def on_success():
                    nonlocal stage, busy
                    stage = new_stage
                    selected_port.set(port_name)
                    var_x.set("x = " + str(stage.x))
                    var_y.set("y = " + str(stage.y))
                    var_z.set("z = " + str(stage.z))
                    for w in motion_widgets:
                        w.configure(state=tk.NORMAL)
                    status_var.set(f"Connected to {port_name}")
                    btn_connect.configure(state=tk.NORMAL)
                    busy = False
                    messagebox.showinfo("Connected", f"Connected to Oquam stage on {port_name}.")

                root.after(0, on_success)
                print(f"[Oquam] Successfully connected on {port_name}.")
                return
            except Exception as e:
                print(f"[Oquam] Handshake failed on {port_name}: {e}")
                last_error = e
                try:
                    new_stage.close()
                except Exception:
                    pass
                continue

        def on_failure():
            nonlocal busy
            busy = False
            status_var.set("No Oquam device found")
            btn_connect.configure(state=tk.NORMAL)
            msg = "No Oquam-compatible device found on any serial port."
            if last_error is not None:
                msg += f"\nLast error: {last_error}"
            messagebox.showerror("Connection error", msg)

        root.after(0, on_failure)

    def connect_stage():
        nonlocal busy
        if busy:
            return

        # Read and validate gear ratios from the UI
        try:
            gx = int(gear_x_var.get() or "1")
            gy = int(gear_y_var.get() or "1")
            gz = int(gear_z_var.get() or "1")
        except ValueError:
            messagebox.showerror("Invalid gear values", "Gear ratios must be integers for X, Y, and Z.")
            return

        gears = (gx, gy, gz)

        busy = True
        status_var.set("Scanning ports for Oquam stage...")
        btn_connect.configure(state=tk.DISABLED)
        threading.Thread(target=_scan_ports_worker, args=(gears,), daemon=True).start()

    selector_frame = tk.Frame(frame, bg="white")
    selector_frame.grid(column=0, row=0, columnspan=6, pady=5, sticky="w")

    tk.Label(selector_frame, text="Serial port:", bg="white").grid(column=0, row=0, padx=(0, 5))
    combo_ports = ttk.Combobox(selector_frame, textvariable=selected_port, state="readonly", width=10)
    combo_ports.grid(column=1, row=0, padx=5)

    btn_refresh = tk.Button(selector_frame, text="Refresh", command=refresh_ports, bg="white")
    btn_refresh.grid(column=2, row=0, padx=5)

    btn_connect = tk.Button(selector_frame, text="Connect", command=connect_stage, bg="white")
    btn_connect.grid(column=3, row=0, padx=5)

    # Connection status label
    tk.Label(selector_frame, textvariable=status_var, bg="white").grid(column=4, row=0, padx=5, sticky="w")

    # Gear ratio inputs: bottom line of the interface, aligned with X/Y/Z
    tk.Label(frame, text="Gear:", bg="white").grid(column=column_x, row=8, padx=5, pady=(6, 2), sticky="e")
    entry_gear_x = tk.Entry(frame, width=6, textvariable=gear_x_var)
    entry_gear_x.grid(column=column_x+1, row=8, ipadx=2, pady=(6, 2))

    tk.Label(frame, text="Gear:", bg="white").grid(column=column_y, row=8, padx=5, pady=(6, 2), sticky="e")
    entry_gear_y = tk.Entry(frame, width=6, textvariable=gear_y_var)
    entry_gear_y.grid(column=column_y+1, row=8, ipadx=2, pady=(6, 2))

    tk.Label(frame, text="Gear:", bg="white").grid(column=column_z, row=8, padx=5, pady=(6, 2), sticky="e")
    entry_gear_z = tk.Entry(frame, width=6, textvariable=gear_z_var)
    entry_gear_z.grid(column=column_z+1, row=8, ipadx=2, pady=(6, 2))

    # Populate initial port list
    refresh_ports()




    def move_dx(dx, dt=-1, var_x=var_x):
        if stage is None:
            return
        stage.move_dx(dx, dt)
        # Allows to display the global x displacement
        var_x.set("x = " + str(stage.x)) 

    def move_dy(dy, dt=-1, var_y=var_y):
        if stage is None:
            return
        stage.move_dy(dy, dt)
        # Allows to display the global y displacement
        var_y.set("y = " + str(stage.y))     
        
    def move_dz(dz, dt=-1, var_z=var_z):
        if stage is None:
            return
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
        if stage is None:
            return
        if enable_button.config('text')[-1] == 'Enable':
            stage.handle_enable(1)
            enable_button.config(text='Disable')
        else:
            stage.handle_enable(0)
            enable_button.config(text='Enable')

    def home_x():
        """Home X axis only (if connected)."""
        if stage is None:
            return
        stage.handle_set_homing(0, -1, -1)
        stage.handle_homing()

    def home_y():
        """Home Y axis only (if connected)."""
        if stage is None:
            return
        stage.handle_set_homing(1, -1, -1)
        stage.handle_homing()

    def home_z():
        """Home Z axis only (if connected)."""
        if stage is None:
            return
        stage.handle_set_homing(2, -1, -1)
        stage.handle_homing()

    """--------Buttons-----------"""


    motion_widgets = []

    # Leave the app

    quit_button = tk.Button(frame, text="Quit", fg="black", bg="white", command=root.destroy)
    quit_button.grid(column=0, row=3, ipadx=5, pady=8)

    # Enable or disable motors

    enable_button = tk.Button(frame, text="Enable", bg="white", fg="black", command=toggle)
    enable_button.grid(column= 1, row=3, ipadx=5, pady=8)

    # Homing buttons per axis
    home_x_button = tk.Button(frame, text="Home X", fg=fg_x, bg=bg_x, command=home_x)
    home_x_button.grid(column=column_x, row=4, ipadx=5, pady=5)

    home_y_button = tk.Button(frame, text="Home Y", fg=fg_y, bg=bg_y, command=home_y)
    home_y_button.grid(column=column_y, row=4, ipadx=5, pady=5)

    home_z_button = tk.Button(frame, text="Home Z", fg=fg_z, bg=bg_z, command=home_z)
    home_z_button.grid(column=column_z, row=4, ipadx=5, pady=5)

    # Get global displacement values x and y

    label_x = tk.Label(frame, textvariable = var_x, bg="white") #shows as text in the window
    label_x.grid(column=3, row=1, ipadx=5, pady=5)


    label_y = tk.Label(frame, textvariable = var_y, bg="white") #shows as text in the window
    label_y.grid(column=3, row=2, ipadx=5, pady=5)

    label_z = tk.Label(frame, textvariable = var_z, bg="white") #shows as text in the window
    label_z.grid(column=3, row=3, ipadx=5, pady=5)

    # User inputs valus and clicks to move

    entry_x = tk.Entry(frame, width=6)
    entry_x.grid(column=4, row=1, ipadx=5, pady=5 )    
    user_x = tk.Button(frame, text = 'move x', command = move_x_entry, bg="white")
    user_x.grid(column=5, row=1, ipadx=5, pady=5 )

    entry_y = tk.Entry(frame, width=6)
    entry_y.grid(column=4, row=2, ipadx=5, pady=5 )    
    user_y = tk.Button(frame, text = 'move y', command = move_y_entry, bg="white")
    user_y.grid(column=5, row=2, ipadx=5, pady=5 )

    entry_z = tk.Entry(frame, width=6)
    entry_z.grid(column=4, row=3, ipadx=5, pady=5 )    
    user_z = tk.Button(frame, text = 'move z', command = move_z_entry, bg="white")
    user_z.grid(column=5, row=3, ipadx=5, pady=5 )

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

    # Collect all widgets that should be disabled until a stage is connected
    motion_widgets.extend([
        enable_button,
        home_x_button, home_y_button, home_z_button,
        entry_x, user_x,
        entry_y, user_y,
        entry_z, user_z,
        button2, button3, button4, button5, button6, button7,
        button8, button9, button10, button11, button12, button13,
        button14, button15, button16, button17, button18, button19,
    ])

    if stage is None:
        for w in motion_widgets:
            w.configure(state=tk.DISABLED)



    root.mainloop()



if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog='Motorized Stage')
    parser.add_argument('--port', default=None, help='Serial port of the Arduino (e.g. COM6). If provided, the interface starts connected; otherwise, select inside the GUI.')
    args = parser.parse_args()

    stage = None
    if args.port:
        stage = ControlStage(args.port, [1, 100, 1])

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
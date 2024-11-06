#
#--ALL IMPORTS--#
#

import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
from pprint import pformat

#
#--ALL VARIABLES--#
#

waves = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
wave = 1
unit_pressed = False
current_unit = None
placed_units = []
shared_unit_data = {}

#
#--SETUP FUNCTIONS--#
#

def wup():
    global wave
    if 1 <= wave < 15:
        wave += 1
        update_wave_label()
        update_oval_colors()
    else:
        log("Max wave reached!")

def wdown():
    global wave
    if 1 < wave <= 15:
        wave -= 1
        update_wave_label()
        update_oval_colors()
    else:
        log("Min wave reached!")

def log(f):
    log_text.insert(tk.END, f + "\n")
    log_text.see(tk.END)

def update_wave_label():
    wave_label.config(text=f"Current Wave: {wave}")

def update_oval_colors():
    for unit in placed_units:
        oval_id = unit['oval_id']
        text_id = unit['text_id']
        unit_wave = unit['wave']
        
        if wave >= unit_wave:  # Only show units from current wave or earlier waves
            map_canvas.itemconfig(oval_id, state='normal')
            map_canvas.itemconfig(text_id, state='normal')
            if wave == unit_wave:
                map_canvas.itemconfig(oval_id, fill='green', outline='green')
            else:
                map_canvas.itemconfig(oval_id, fill='red', outline='red')
            update_unit_display(unit)
        else:  # Hide units from future waves
            map_canvas.itemconfig(oval_id, state='hidden')
            map_canvas.itemconfig(text_id, state='hidden')

def unit_button_click(unit_num):
    global unit_pressed, current_unit
    unit_pressed = True
    current_unit = unit_num
    log(f"Click on the map to select unit {unit_num} placement.")

def on_map_click(event):
    global unit_pressed, current_unit
    if unit_pressed:
        x, y = event.x, event.y
        oval_size = 15
        oval_id = map_canvas.create_oval(x-oval_size, y-oval_size, x+oval_size, y+oval_size, 
                                       fill='red', outline='red')
        text_id = map_canvas.create_text(x, y, text=str(current_unit), 
                                       fill='white', font=("Arial", 12, "bold"))
        
        upgrades = [0] * 15
        
        placed_units.append({
            'oval_id': oval_id,
            'text_id': text_id,
            'unit_num': current_unit,
            'wave': wave,
            'x': x,
            'y': y,
            'upgrades': upgrades
        })
        
        unit_pressed = False
        log(f"Unit {current_unit} placed at ({x}, {y}) for wave {wave}")
        current_unit = None
        
        update_oval_colors()

def upgrade_unit(event):
    x, y = event.x, event.y
    for unit in placed_units:
        unit_x, unit_y = unit['x'], unit['y']
        if ((x - unit_x)**2 + (y - unit_y)**2) <= 225:
            unit['upgrades'][wave-1] += 1
            update_unit_display(unit)
            log(f"Upgraded unit {unit['unit_num']} at wave {wave}")
            break

def downgrade_unit(event):
    x, y = event.x, event.y
    for i, unit in enumerate(placed_units):
        unit_x, unit_y = unit['x'], unit['y']
        if ((x - unit_x)**2 + (y - unit_y)**2) <= 225:
            if unit['upgrades'][wave-1] > 0:
                # If unit has upgrades at current wave, remove one upgrade
                unit['upgrades'][wave-1] -= 1
                update_unit_display(unit)
                log(f"Downgraded unit {unit['unit_num']} at wave {wave}")
            elif wave == unit['wave'] and sum(unit['upgrades']) == 0:
                # Only allow deletion if we're on the wave it was placed and it has no upgrades
                map_canvas.delete(unit['oval_id'])
                map_canvas.delete(unit['text_id'])
                placed_units.pop(i)
                log(f"Removed unit {unit['unit_num']}")
            else:
                # If trying to delete on wrong wave or unit has upgrades in other waves
                log(f"Unit {unit['unit_num']} can only be deleted/downgraded on wave {unit['wave']}")
            break


def create_preview_window():
    preview_window = tk.Toplevel()
    preview_window.title("Macro Preview")
    
    # Create title label
    title_label = ttk.Label(preview_window, text="Macro Preview", font=("Arial", 24, "bold"))
    title_label.pack(pady=20)
    
    # Create canvas for preview
    preview_canvas = tk.Canvas(preview_window, width=resized_image.width, height=resized_image.height)
    preview_canvas.pack()
    preview_canvas.create_image(0, 0, anchor=tk.NW, image=map_image)
    
    # Create wave label
    preview_wave_label = ttk.Label(preview_window, text="Wave: 1", font=("Arial", 16))
    preview_wave_label.pack(pady=10)
    
    # Add the message at the bottom
    message_label = ttk.Label(preview_window, 
                             text="If this is not right, you can go back and make changes.", 
                             font=("Arial", 10, "italic"))
    message_label.pack(pady=10)
    
    # Copy all placed units to preview canvas
    preview_units = []
    for unit in placed_units:
        oval_id = preview_canvas.create_oval(
            unit['x']-15, unit['y']-15, 
            unit['x']+15, unit['y']+15, 
            fill='red', outline='red', state='hidden'
        )
        text_id = preview_canvas.create_text(
            unit['x'], unit['y'], 
            text=str(unit['unit_num']), 
            fill='white', font=("Arial", 12, "bold"), 
            state='hidden'
        )
        preview_units.append({
            'oval_id': oval_id,
            'text_id': text_id,
            'wave': unit['wave'],
            'upgrades': unit['upgrades'],
            'unit_num': unit['unit_num']
        })
    
    def update_preview(current_wave):
        preview_wave_label.config(text=f"Wave: {current_wave}")
        
        for unit in preview_units:
            if current_wave >= unit['wave']:
                preview_canvas.itemconfig(unit['oval_id'], state='normal')
                preview_canvas.itemconfig(unit['text_id'], state='normal')
                
                if current_wave == unit['wave']:
                    preview_canvas.itemconfig(unit['oval_id'], fill='green', outline='green')
                else:
                    preview_canvas.itemconfig(unit['oval_id'], fill='red', outline='red')
                
                # Update upgrade display
                total_upgrades = sum(unit['upgrades'][:current_wave])
                if total_upgrades > 0:
                    preview_canvas.itemconfig(unit['text_id'], 
                                           text=f"{unit['unit_num']}[+{total_upgrades}]")
                else:
                    preview_canvas.itemconfig(unit['text_id'], 
                                           text=str(unit['unit_num']))
            else:
                preview_canvas.itemconfig(unit['oval_id'], state='hidden')
                preview_canvas.itemconfig(unit['text_id'], state='hidden')
        
        if current_wave < 15:
            preview_window.after(1000, update_preview, current_wave + 1)
        else:
            # After reaching wave 15, restart from wave 1
            preview_window.after(1000, update_preview, 1)
    
    # Start the animation
    preview_window.after(1000, update_preview, 1)


def update_unit_display(unit):
    total_upgrades = sum(unit['upgrades'][:wave])
    
    if total_upgrades > 0:
        map_canvas.itemconfig(unit['text_id'], 
                            text=f"{unit['unit_num']}[+{total_upgrades}]")
    else:
        map_canvas.itemconfig(unit['text_id'], 
                            text=str(unit['unit_num']))

def print_lists():
    global shared_unit_data  # Declare the use of the global variable
    confirmation = messagebox.askyesno("Confirm", "Are you sure you want to complete the setup?")
    if confirmation:
        # Save the unit data to the shared variable with the new format
        shared_unit_data = {
            'units': [
                {
                    'wave': unit['wave'],
                    'unit_num': unit['unit_num'],
                    'posx': unit['x'],
                    'posy': unit['y'],
                    'upgrades': unit['upgrades']
                } for unit in placed_units
            ]
        }
        
        # Log the shared unit data
        log("Saved Unit Data:")
        log(str(shared_unit_data))  # Log the entire shared_unit_data variable
        
        messagebox.showinfo("Setup Complete", "The setup has been completed and data has been logged.")
        create_preview_window()
    else:
        log("Setup completion cancelled.")

#
#--SETUP GUI AND MAINLOOP
#

root = tk.Tk()
root.title("Setup")

original_image = Image.open("map.png")
resized_image = original_image.resize((original_image.width // 3, original_image.height // 3))
map_image = ImageTk.PhotoImage(resized_image)

# Create main frame to contain left and right frames
main_frame = ttk.Frame(root)
main_frame.pack(side="top", fill="both", expand=True)

# Create and pack left frame inside main frame
left_frame = ttk.Frame(main_frame)
left_frame.pack(side="left", fill="y", padx=10, pady=10)

# Create and pack right frame inside main frame
right_frame = ttk.Frame(main_frame)
right_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

map_canvas = tk.Canvas(left_frame, width=resized_image.width, height=resized_image.height)
map_canvas.pack()
map_canvas.create_image(0, 0, anchor=tk.NW, image=map_image)
map_canvas.bind("<Button-1>", on_map_click)
map_canvas.bind("<Button-3>", downgrade_unit)
map_canvas.bind("<Button-2>", upgrade_unit)

wave_label = ttk.Label(right_frame, text=f"Current Wave: {wave}", font=("Arial", 20, "bold"))
wave_label.pack(pady=10)

up_button = ttk.Button(right_frame, text="Wave Up", command=wup)
up_button.pack(pady=5)

down_button = ttk.Button(right_frame, text="Wave Down", command=wdown)
down_button.pack(pady=5)

log_text = tk.Text(right_frame, height=10, width=40)
log_text.pack(pady=10)

button_frame = ttk.Frame(right_frame)
button_frame.pack(pady=10, fill='both')

complete_button = ttk.Button(right_frame, text="Finish setup", command=print_lists)
complete_button.pack(pady=10)

for i in range(6):
    button_frame.columnconfigure(i, weight=1)

u1_button = ttk.Button(button_frame, text="1", width=3, command=lambda: unit_button_click(1))
u1_button.grid(row=0, column=0, padx=2, sticky='ew')
u2_button = ttk.Button(button_frame, text="2", width=3, command=lambda: unit_button_click(2))
u2_button.grid(row=0, column=1, padx=2, sticky='ew')
u3_button = ttk.Button(button_frame, text="3", width=3, command=lambda: unit_button_click(3))
u3_button.grid(row=0, column=2, padx=2, sticky='ew')
u4_button = ttk.Button(button_frame, text="4", width=3, command=lambda: unit_button_click(4))
u4_button.grid(row=0, column=3, padx=2, sticky='ew')
u5_button = ttk.Button(button_frame, text="5", width=3, command=lambda: unit_button_click(5))
u5_button.grid(row=0, column=4, padx=2, sticky='ew')
u6_button = ttk.Button(button_frame, text="6", width=3, command=lambda: unit_button_click(6))
u6_button.grid(row=0, column=5, padx=2, sticky='ew')

# Create bottom frame and pack it below the main frame
bottom_frame = ttk.Frame(root)
bottom_frame.pack(side="bottom", fill="x", padx=10, pady=10)

# Add labels to the bottom frame
keybind_label = ttk.Label(bottom_frame, text="Keybinds:", font=("Arial", 12, "bold"))
keybind_label.pack(side="left", padx=(0, 10))

place_label = ttk.Label(bottom_frame, text="Place: Left Click", font=("Arial", 10))
place_label.pack(side="left", padx=10)

upgrade_label = ttk.Label(bottom_frame, text="Upgrade: Middle Click", font=("Arial", 10))
upgrade_label.pack(side="left", padx=10)

downgrade_label = ttk.Label(bottom_frame, text="Remove Upgrade or Remove unit: Right Click", font=("Arial", 10))
downgrade_label.pack(side="left", padx=10)

disclaimer_label = ttk.Label(bottom_frame, text="Disclaimer: Deleting units and using abilities have not been added yet.", font=("Arial", 10, "italic"), foreground="red")
disclaimer_label.pack(side="bottom", pady=(10, 0))

instruction_frame = ttk.Frame(root)
instruction_frame.pack(side="bottom", fill="x", padx=10, pady=10)

instruction_label = ttk.Label(instruction_frame, 
                              text="To start macro, close this window after finalizing setup.", 
                              font=("Arial", 12, "bold"), 
                              foreground="blue")
instruction_label.pack(side="bottom", pady=(10, 0))

root.mainloop()

#                     #
#                     #
#                     #
#--MAIN SCRIPT START--#
#                     #
#                     #
#                     #

def update_shared_data_label():
    formatted_data = pformat(shared_unit_data, width=40)
    shared_data_label.config(text=f"Shared Unit Data:\n{formatted_data}")

mainroot = tk.Tk()
mainroot.title("Main")

# Create a label to display shared_unit_data
shared_data_label = ttk.Label(mainroot, text="", font=("Courier", 10), justify=tk.LEFT)
shared_data_label.pack(padx=10, pady=10)

# Update the label with the current shared_unit_data
update_shared_data_label()

mainroot.mainloop()
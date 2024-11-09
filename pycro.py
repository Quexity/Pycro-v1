#
#--ALL IMPORTS--#
#

import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
from pprint import pformat
import win32gui
import win32com.client
import win32con
import cv2
from matplotlib import pyplot as plt
import pyautogui
import numpy as np
import time

#
#--ALL VARIABLES--#
#

waves = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
wave = 1
unit_pressed = False
current_unit = None
placed_units = []
shared_unit_data = {}
setup_complete = False

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
    preview_canvas = tk.Canvas(preview_window, width=960, height=540)
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
    
    # Add Close button
    close_button = ttk.Button(preview_window, text="Close Preview", command=preview_window.destroy)
    close_button.pack(pady=10)
    
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
    
    # Start the display
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
    global shared_unit_data
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
        setup_complete = True
        
        # Add the continue button
        continue_button = ttk.Button(right_frame, text="Continue to macro", command=root.destroy)
        continue_button.pack(pady=10)

        # Log the shared unit data
        log("Saved Unit Data:")
        log(str(shared_unit_data)) 
        
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
resized_image = original_image.resize((960, 540), Image.LANCZOS)
map_image = ImageTk.PhotoImage(resized_image)

main_frame = ttk.Frame(root)
main_frame.pack(side="top", fill="both", expand=True)

left_frame = ttk.Frame(main_frame)
left_frame.pack(side="left", fill="y", padx=10, pady=10)

right_frame = ttk.Frame(main_frame)
right_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

map_canvas = tk.Canvas(left_frame, width=960, height=540)
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

for i in range(5):
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

bottom_frame = ttk.Frame(root)
bottom_frame.pack(side="bottom", fill="x", padx=10, pady=10)

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

# Split shared_unit_data into separate lists
waves = []
unit_nums = []
positions_x = []
positions_y = []
upgrade_lists = []
playbutton = cv2.imread("Lobbydetections\\playbutton.png")
playbutton_gray = cv2.cvtColor(playbutton, cv2.COLOR_BGR2GRAY)
playbutton_rgb = cv2.cvtColor(playbutton, cv2.COLOR_BGR2RGB)

# Extract data from shared_unit_data
for unit in shared_unit_data.get('units', []):
    waves.append(unit['wave'])
    unit_nums.append(unit['unit_num'])
    positions_x.append(unit['posx'])
    positions_y.append(unit['posy'])
    upgrade_lists.append(unit['upgrades'])

#
#
#
#
# TEMPORARY, DELETE LATER.
def update_shared_data_label():
    formatted_data = "Split Unit Data:\n"
    formatted_data += f"Waves: {waves}\n"
    formatted_data += f"Unit Numbers: {unit_nums}\n"
    formatted_data += f"X Positions: {positions_x}\n"
    formatted_data += f"Y Positions: {positions_y}\n"
    formatted_data += f"Upgrade Lists: {upgrade_lists}\n"
    shared_data_label.config(text=formatted_data)
#
#
#
#

def find_roblox_window():
    browser_names = [
        "microsoft edge", 
        "chrome", 
        "firefox", 
        "safari", 
        "opera", 
        "brave", 
        "vivaldi", 
        "browser"
    ]

    def enum_windows_callback(hwnd, windows):
        # Check if the window is visible and has a title
        if win32gui.IsWindowVisible(hwnd) and win32gui.GetWindowText(hwnd):
            # Get the window title and class name
            title = win32gui.GetWindowText(hwnd)
            class_name = win32gui.GetClassName(hwnd)
            
            # Check if the title contains any browser names
            is_browser = any(browser_name in title.lower() for browser_name in browser_names)
            
            # Print out window details for debugging, remove later
            print(f"Window Title: {title}, Class Name: {class_name}")
            
            # Check for Roblox-like window titles or class names, excluding browsers
            if not is_browser and ("roblox" in title.lower() or "roblox" in class_name.lower()):
                windows.append(hwnd)
        return True

    # List to store found Roblox windows
    roblox_windows = []
    
    # Run through all windows
    win32gui.EnumWindows(enum_windows_callback, roblox_windows)
    
    # If windows found, return the first one, remove later.
    if roblox_windows:
        print(f"Found Roblox window: {win32gui.GetWindowText(roblox_windows[0])}")
        return roblox_windows[0]
    
    return None

def find_and_click_play_button():
    # Find the Roblox window using our custom function
    hwnd = find_roblox_window()
    
    if hwnd:
        try:
            # Bring the window to the foreground
            shell = win32com.client.Dispatch("WScript.Shell")
            shell.SendKeys('%')  # Alt key to bring window to foreground
            win32gui.SetForegroundWindow(hwnd)
            
            # Restore the window if minimized
            if win32gui.IsIconic(hwnd):
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
            
            # Give a small delay incase focus takes longer
            time.sleep(1)
        except Exception as e:
            print(f"Could not bring Roblox window to foreground: {e}")
        
        # Screenshot the screen
        screenshot = pyautogui.screenshot()
        screenshot_np = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        screenshot_gray = cv2.cvtColor(screenshot_np, cv2.COLOR_BGR2GRAY)
        
        # Template matching
        result = cv2.matchTemplate(screenshot_gray, playbutton_gray, cv2.TM_CCOEFF_NORMED)
        
        # Find the location of the best match
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        
        # Set the threshold for matching
        threshold = 0.8
        if max_val >= threshold:
            # Get the center of the matched region
            w, h = playbutton_gray.shape[::-1]
            top_left = max_loc
            center_x = top_left[0] + w // 2
            center_y = top_left[1] + h // 2
            
            # Click the center of the play button
            pyautogui.click(center_x, center_y)
            print("Play button found and clicked!")
            return True
        else:
            print("Play button not found.")
            return False
    else:
        print("Roblox window not found")
        return False

def embed_roblox():
    # Find the Roblox window
    hwnd = find_roblox_window()

    if hwnd:
        # Set fixed dimensions for the Roblox window
        fixed_width = 960
        fixed_height = 540
        
        # Get the window handle of the frame where roblox is going to be embedded
        frame_hwnd = roblox_frame.winfo_id()
        
        # Set the parent of the Roblox window to our frame
        win32gui.SetParent(hwnd, frame_hwnd)
        
        # Move and resize the Roblox window to fill the frame with fixed dimensions
        win32gui.MoveWindow(hwnd, 0, 0, fixed_width, fixed_height, True)
        
        # Remove the window style that allows resizing and moving
        style = win32gui.GetWindowLong(hwnd, win32con.GWL_STYLE)
        style = style & ~win32con.WS_THICKFRAME & ~win32con.WS_CAPTION
        win32gui.SetWindowLong(hwnd, win32con.GWL_STYLE, style)
        
        # Force window to redraw
        win32gui.SetWindowPos(hwnd, None, 0, 0, fixed_width, fixed_height, 
                              win32con.SWP_FRAMECHANGED | win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
        
        # Wait a moment for the window to settle
        time.sleep(1)
        
        # Print the actual window title after embedding, remove later.
        actual_title = win32gui.GetWindowText(hwnd)
        print(f"Embedded Roblox window with actual title: {actual_title}")
        
        # Start searching for play button
        find_and_click_play_button()
    else:
        print("Roblox window not found. Please ensure Roblox is open.")

mainroot = tk.Tk()
mainroot.title("Main")
mainroot.geometry("1280x720")
mainroot.resizable(True, True) 

main_frame = ttk.Frame(mainroot)
main_frame.pack(fill=tk.BOTH, expand=True)

roblox_frame = ttk.Frame(main_frame, relief="solid", borderwidth=1, width=960, height=540)
roblox_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=False)  # Set expand to False to keep the f

right_frame = ttk.Frame(main_frame)
right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True) 

embed_button = ttk.Button(main_frame, text="Embed Roblox", command=embed_roblox)
embed_button.pack()

data_frame = ttk.Frame(main_frame)
data_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

shared_data_label = ttk.Label(data_frame, text="", font=("Courier", 10), justify=tk.LEFT)
shared_data_label.pack(padx=10, pady=10)

update_shared_data_label()

mainroot.mainloop()
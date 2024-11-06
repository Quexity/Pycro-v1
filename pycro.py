import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

waves = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
wave = 1
unit_pressed = False
current_unit = None
placed_units = [] 

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
        unit_wave = unit['wave']
        if wave == unit_wave:
            map_canvas.itemconfig(oval_id, fill='green', outline='green')
        else:
            map_canvas.itemconfig(oval_id, fill='red', outline='red')

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
        
        placed_units.append({
            'oval_id': oval_id,
            'text_id': text_id,
            'unit_num': current_unit,
            'wave': wave,
            'x': x,
            'y': y
        })
        
        unit_pressed = False
        log(f"Unit {current_unit} placed at ({x}, {y}) for wave {wave}")
        current_unit = None
        
        update_oval_colors()

def print_lists():
    x_coordinates = [unit['x'] for unit in placed_units]
    y_coordinates = [unit['y'] for unit in placed_units]
    unit_numbers = [unit['unit_num'] for unit in placed_units]
    wave_numbers = [unit['wave'] for unit in placed_units]
    
    log(f"X coordinates: {x_coordinates}")
    log(f"Y coordinates: {y_coordinates}")
    log(f"Unit numbers: {unit_numbers}")
    log(f"Wave numbers: {wave_numbers}")

root = tk.Tk()
root.title("Setup")

original_image = Image.open("map.png")
resized_image = original_image.resize((original_image.width // 3, original_image.height // 3))
map_image = ImageTk.PhotoImage(resized_image)

left_frame = ttk.Frame(root)
left_frame.pack(side="left", fill="y", padx=10, pady=10)

right_frame = ttk.Frame(root)
right_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

map_canvas = tk.Canvas(left_frame, width=resized_image.width, height=resized_image.height)
map_canvas.pack()
map_canvas.create_image(0, 0, anchor=tk.NW, image=map_image)
map_canvas.bind("<Button-1>", on_map_click)

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

confirm_button = ttk.Button(right_frame, text="Confirm", command=print_lists)
confirm_button.pack(pady=10)

root.mainloop()
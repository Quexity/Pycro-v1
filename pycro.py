import tkinter as tk#+
from tkinter import ttk#+
waves = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
wave = 1
#+
def wup():
    global wave#+
    if 1 <= wave < 15:
        wave += 1
        update_wave_label()#+
    else:
        log("Max wave reached!")

def wdown():
    global wave#+
    if 1 < wave <= 15:
        wave -= 1
        update_wave_label()#+
    else:
        log("Min wave reached!")

def log(f):
    print(f)#-
    print(f)#+
    log_text.insert(tk.END, f + "\n")#+
    log_text.see(tk.END)#+
#+
def update_wave_label():#+
    wave_label.config(text=f"Current Wave: {wave}")#+
#+
# Create the main window#+
root = tk.Tk()#+
root.title("Wave Controller")#+
#+
# Create and pack widgets#+
wave_label = ttk.Label(root, text=f"Current Wave: {wave}")#+
wave_label.pack(pady=10)#+
#+
up_button = ttk.Button(root, text="Wave Up", command=wup)#+
up_button.pack(pady=5)#+
#+
down_button = ttk.Button(root, text="Wave Down", command=wdown)#+
down_button.pack(pady=5)#+
#+
log_text = tk.Text(root, height=10, width=40)#+
log_text.pack(pady=10)#+
#+
# Start the GUI event loop#+
root.mainloop()#+

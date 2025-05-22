import os
import tkinter as tk
from tkinter import ttk
from obswebsocket import obsws, requests

# OBS WebSocket connection info
HOST = "localhost"
PORT = 4455
PASSWORD = "123456"  # Replace with your OBS WebSocket password

# Source names in OBS
p1_sources = ["P1_Active", "P1_Bench1", "P1_Bench2", "P1_Bench3", "P1_Bench4", "P1_Bench5"]
p2_sources = ["P2_Active", "P2_Bench1", "P2_Bench2", "P2_Bench3", "P2_Bench4", "P2_Bench5"]

# Image folder
IMAGE_FOLDER = r"C:\Users\esquelo\Desktop\livemgs\imagens"
iconeapp = r"C:\Users\esquelo\Desktop\livemgs\manafix.ico"

# Get image files
def get_image_files(folder):
    return [f for f in os.listdir(folder) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]

# OBS Connection
def connect_obs():
    ws = obsws(HOST, PORT, PASSWORD)
    ws.connect()
    return ws

# GUI App
class OBSSwitcherApp:
    def __init__(self, master):
        self.master = master
        master.title("Programa foda do Hage pra stream da Manafix")

        self.ws = connect_obs()
        self.image_files = get_image_files(IMAGE_FOLDER)

        self.dropdowns = {}

        # Headers
        ttk.Label(master, text="Player 1", font=("Segoe UI", 10, "bold")).grid(row=0, column=0, columnspan=2, pady=(10, 0))
        ttk.Label(master, text="Player 2", font=("Segoe UI", 10, "bold")).grid(row=0, column=2, columnspan=2, pady=(10, 0))

        # Layout player 1 and player 2 side by side
        for i, (p1_source, p2_source) in enumerate(zip(p1_sources, p2_sources), start=1):
            # Player 1
            ttk.Label(master, text=p1_source).grid(row=i, column=0, padx=5, pady=3, sticky="e")
            p1_var = tk.StringVar()
            p1_combo = ttk.Combobox(master, textvariable=p1_var, values=self.image_files, width=25)
            p1_combo.grid(row=i, column=1, padx=5, pady=3)
            self.dropdowns[p1_source] = p1_combo

            # Player 2
            ttk.Label(master, text=p2_source).grid(row=i, column=2, padx=20, pady=3, sticky="e")
            p2_var = tk.StringVar()
            p2_combo = ttk.Combobox(master, textvariable=p2_var, values=self.image_files, width=25)
            p2_combo.grid(row=i, column=3, padx=5, pady=3)
            self.dropdowns[p2_source] = p2_combo

        ttk.Button(master, text="Update All", command=self.update_all).grid(row=7, column=0, columnspan=4, pady=10)

    def update_all(self):
        for source, dropdown in self.dropdowns.items():
            filename = dropdown.get()
            if filename:
                image_path = os.path.abspath(os.path.join(IMAGE_FOLDER, filename))
                try:
                    self.ws.call(requests.SetSourceSettings(
                        sourceName=source,
                        sourceSettings={"file": image_path}
                    ))
                except Exception as e:
                    print(f"Error updating {source}: {e}")

    def __del__(self):
        try:
            self.ws.disconnect()
        except:
            pass

# Run the app
if __name__ == "__main__":
    root = tk.Tk()
    app = OBSSwitcherApp(root)
    root.iconbitmap(iconeapp)
    root.mainloop()
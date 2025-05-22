import os
import tkinter as tk
from tkinter import ttk
from obswebsocket import obsws, requests

# coisas do websocket
HOST = "localhost"
PORT = 4455
PASSWORD = "123456"  # coloca sua senha

# nome das fontes no obs
p1_sources = ["p1_ativo", "p1_banco1", "p1_banco2", "p1_banco3", "p1_banco4", "p1_banco5"]
p2_sources = ["p2_ativo", "p2_banco1", "p2_banco2", "p2_banco3", "p2_banco4", "p2_banco5"]

# pasta de imagens e ícone
IMAGE_FOLDER = r"C:\Users\esquelo\Desktop\livemgs\imagens"
iconeapp = r"C:\Users\esquelo\Desktop\livemgs\manafix.ico"

# pega as imagens
def get_image_files(folder):
    return [f for f in os.listdir(folder) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]

# liga no obs
def connect_obs():
    ws = obsws(HOST, PORT, PASSWORD)
    ws.connect()
    return ws

# aplicativo
class OBSSwitcherApp:
    def __init__(self, master):
        self.master = master
        master.title("Programa foda do Hage pra stream da Manafix")

        self.ws = connect_obs()
        self.image_files = get_image_files(IMAGE_FOLDER)
        self.dropdowns = {}

        # dark mode
        self.dark_mode = tk.BooleanVar(value=True)
        self.set_theme()

        # botão pra alternar tema
        toggle_btn = ttk.Checkbutton(master, text="Modo Escuro", variable=self.dark_mode, command=self.set_theme)
        toggle_btn.grid(row=0, column=4, padx=10, pady=10, sticky="e")

        # nomes dos jogadores
        ttk.Label(master, text="Jogador 1", font=("Segoe UI", 10, "bold")).grid(row=0, column=0, columnspan=2, pady=(10, 0))
        ttk.Label(master, text="Jogador 2", font=("Segoe UI", 10, "bold")).grid(row=0, column=2, columnspan=2, pady=(10, 0))

        # layout do aplicativo
        for i, (p1_source, p2_source) in enumerate(zip(p1_sources, p2_sources), start=1):
            # jogador 1
            ttk.Label(master, text=p1_source).grid(row=i, column=0, padx=5, pady=3, sticky="e")
            p1_var = tk.StringVar()
            p1_combo = ttk.Combobox(master, textvariable=p1_var, values=self.image_files, width=25)
            p1_combo.grid(row=i, column=1, padx=5, pady=3)
            self.dropdowns[p1_source] = p1_combo

            # jogador 2
            ttk.Label(master, text=p2_source).grid(row=i, column=2, padx=20, pady=3, sticky="e")
            p2_var = tk.StringVar()
            p2_combo = ttk.Combobox(master, textvariable=p2_var, values=self.image_files, width=25)
            p2_combo.grid(row=i, column=3, padx=5, pady=3)
            self.dropdowns[p2_source] = p2_combo

        ttk.Button(master, text="Atualizar Tudo", command=self.update_all).grid(row=7, column=0, columnspan=4, pady=10)

    def set_theme(self):
        style = ttk.Style()
        if self.dark_mode.get():
            self.master.configure(bg="#2e2e2e")
            style.theme_use("clam")
            style.configure("TLabel", background="#2e2e2e", foreground="white")
            style.configure("TButton", background="#3e3e3e", foreground="white")
            style.configure("TCombobox", fieldbackground="#3e3e3e", background="#2e2e2e", foreground="white")
            style.configure("TCheckbutton", background="#2e2e2e", foreground="white")
        else:
            self.master.configure(bg="SystemButtonFace")
            style.theme_use("default")
            style.configure("TLabel", background="SystemButtonFace", foreground="black")
            style.configure("TButton", background="SystemButtonFace", foreground="black")
            style.configure("TCombobox", fieldbackground="white", background="white", foreground="black")
            style.configure("TCheckbutton", background="SystemButtonFace", foreground="black")

    def update_all(self):
        for source, dropdown in self.dropdowns.items():
            filename = dropdown.get()
            if filename:
                image_path = os.path.abspath(os.path.join(IMAGE_FOLDER, filename))
                try:
                    self.ws.call(requests.SetInputSettings(
                        inputName=source,
                        inputSettings={"file": image_path},
                        overlay=True
                    ))
                except Exception as e:
                    print(f"Erro ao atualizar {source}: {e}")

    def __del__(self):
        try:
            self.ws.disconnect()
        except:
            pass

# roda o aplicativo
if __name__ == "__main__":
    root = tk.Tk()
    app = OBSSwitcherApp(root)
    root.iconbitmap(iconeapp)
    root.mainloop()

import os
import tkinter as tk
from tkinter import ttk
import asyncio
from obsws_python import OBSWS

# Config OBS WebSocket
HOST = "localhost"
PORT = 4455
PASSWORD = "kv48BtG8cAy1uIX8"

# Fontes no OBS
p1_sources = ["p1_ativo", "p1_banco1", "p1_banco2", "p1_banco3", "p1_banco4", "p1_banco5"]
p2_sources = ["p2_ativo", "p2_banco1", "p2_banco2", "p2_banco3", "p2_banco4", "p2_banco5"]

# Caminho das imagens
IMAGE_FOLDER = r"C:\Users\esquelo\Desktop\livemgs\imagens"
iconeapp = r"C:\Users\esquelo\Desktop\livemgs\manafix.ico"

# Busca imagens na pasta
def get_image_files(folder):
    return [f for f in os.listdir(folder) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]

class OBSSwitcherApp:
    def __init__(self, master):
        self.master = master
        master.title("Programa foda do Hage pra stream da Manafix")

        self.image_files = get_image_files(IMAGE_FOLDER)
        self.dropdowns = {}

        # Layout
        ttk.Label(master, text="Jogador 1", font=("Segoe UI", 10, "bold")).grid(row=0, column=0, columnspan=2, pady=(10, 0))
        ttk.Label(master, text="Jogador 2", font=("Segoe UI", 10, "bold")).grid(row=0, column=2, columnspan=2, pady=(10, 0))

        for i, (p1_source, p2_source) in enumerate(zip(p1_sources, p2_sources), start=1):
            ttk.Label(master, text=p1_source).grid(row=i, column=0, padx=5, pady=3, sticky="e")
            p1_var = tk.StringVar()
            p1_combo = ttk.Combobox(master, textvariable=p1_var, values=self.image_files, width=25)
            p1_combo.grid(row=i, column=1, padx=5, pady=3)
            self.dropdowns[p1_source] = p1_combo

            ttk.Label(master, text=p2_source).grid(row=i, column=2, padx=20, pady=3, sticky="e")
            p2_var = tk.StringVar()
            p2_combo = ttk.Combobox(master, textvariable=p2_var, values=self.image_files, width=25)
            p2_combo.grid(row=i, column=3, padx=5, pady=3)
            self.dropdowns[p2_source] = p2_combo

        ttk.Button(master, text="Atualizar", command=lambda: asyncio.run(self.update_all())).grid(row=7, column=0, columnspan=4, pady=10)

    async def update_all(self):
        try:
            async with OBSWS(HOST, PORT, PASSWORD) as ws:
                for source, dropdown in self.dropdowns.items():
                    filename = dropdown.get()
                    if filename:
                        image_path = os.path.abspath(os.path.join(IMAGE_FOLDER, filename))
                        try:
                            await ws.set_input_settings(
                                inputName=source,
                                inputSettings={"file": image_path},
                                overlay=True
                            )
                            print(f"[OK] Atualizado '{source}' para '{filename}'")
                        except Exception as e:
                            print(f"[Erro] Falha ao atualizar '{source}': {e}")
        except Exception as e:
            print(f"[Erro de conexão] {e}")

# Executar
if __name__ == "__main__":
    root = tk.Tk()
    root.iconbitmap(iconeapp)
    app = OBSSwitcherApp(root)
    root.mainloop()

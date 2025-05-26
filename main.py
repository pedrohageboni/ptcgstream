import os
import tkinter as tk
from tkinter import ttk, filedialog
from obswebsocket import obsws, requests, exceptions as obsexceptions
import json
import sys
import pickle

OBS_HOST = "localhost"
OBS_PORT = 4455
OBS_PASSWORD = "123456"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MAIN_IMAGE_DIR_NAME = "imagens"
ICON_FILE_NAME = "icon.ico"

SUBFOLDER_POKEMON = "pokemon"
SUBFOLDER_ESTADIO = "estadios"
SUBFOLDER_PRIZES = "prizes"

PLAYER1_SOURCES = [
    "p1_ativo",
    "p1_banco1",
    "p1_banco2",
    "p1_banco3",
    "p1_banco4",
    "p1_banco5",
    "p1_banco6",
    "p1_banco7",
    "p1_banco8",
    "prize1"
]

PLAYER2_SOURCES = [
    "p2_ativo",
    "p2_banco1",
    "p2_banco2",
    "p2_banco3",
    "p2_banco4",
    "p2_banco5",
    "p2_banco6",
    "p2_banco7",
    "p2_banco8",
    "prize2"
]

SHARED_SOURCES = ["estadio"]

DEFAULT_DARK_MODE = True

MAIN_IMAGE_DIR = os.path.join(BASE_DIR, MAIN_IMAGE_DIR_NAME)
ICONE_APP_PATH = os.path.join(BASE_DIR, ICON_FILE_NAME)

FOLDERS = {
    "pokemon": os.path.join(MAIN_IMAGE_DIR, SUBFOLDER_POKEMON),
    "estadio": os.path.join(MAIN_IMAGE_DIR, SUBFOLDER_ESTADIO),
    "prizes": os.path.join(MAIN_IMAGE_DIR, SUBFOLDER_PRIZES)
}

SOURCES = {
    "player1": PLAYER1_SOURCES,
    "player2": PLAYER2_SOURCES,
    "shared": SHARED_SOURCES
}

DECK_PATHS_FILE = os.path.join(BASE_DIR, "deck_paths.pkl")

def load_deck_paths():
    try:
        with open(DECK_PATHS_FILE, 'rb') as f:
            return pickle.load(f)
    except:
        return {
            "player1": "",
            "player2": ""
        }

def save_deck_paths(player1_path, player2_path):
    deck_paths = {
        "player1": player1_path,
        "player2": player2_path
    }
    try:
        with open(DECK_PATHS_FILE, 'wb') as f:
            pickle.dump(deck_paths, f)
    except Exception as e:
        print(f"ERRO ao salvar caminhos dos decks: {e}")

DECK_PATHS = load_deck_paths()

def get_image_files(folder_path):
    if not folder_path or not os.path.isdir(folder_path):
        return []
    
    try:
        return sorted([f for f in os.listdir(folder_path) 
                      if f.lower().endswith(('.png', '.jpg', '.jpeg'))])
    except Exception as e:
        print(f"ERRO ao ler a pasta: {folder_path} - {e}")
        return []

def connect_obs():
    ws = obsws(OBS_HOST, OBS_PORT, OBS_PASSWORD)
    try:
        ws.connect()
        print("Conectado ao OBS.")
        return ws
    except Exception as e:
        print(f"ERRO ao conectar ao OBS: {e}")
        return None

class OBSController:
    def __init__(self, master):
        self.master = master
        master.title("programa foda do hage pra manafix")
        
        self.ws = connect_obs()
        
        self.images = {
            "pokemon": get_image_files(FOLDERS["pokemon"]),
            "estadio": get_image_files(FOLDERS["estadio"]),
            "prizes": get_image_files(FOLDERS["prizes"]),
            "player1_deck": get_image_files(DECK_PATHS["player1"]),
            "player2_deck": get_image_files(DECK_PATHS["player2"])
        }
        
        self.dropdowns = {}
        self.deck_paths = {
            "player1": tk.StringVar(value=DECK_PATHS["player1"]),
            "player2": tk.StringVar(value=DECK_PATHS["player2"])
        }
        self.dark_mode = tk.BooleanVar(value=DEFAULT_DARK_MODE)
        self.setup_ui()
        
        if self.ws:
            self.master.after(200, self.load_obs_settings)
    
    def setup_ui(self):
        self.apply_theme()
        
        ttk.Checkbutton(
            self.master, 
            text="Modo Escuro", 
            variable=self.dark_mode, 
            command=self.apply_theme
        ).grid(row=0, column=3, padx=10, pady=10, sticky="e")
        
        current_row = 1
        ttk.Label(
            self.master, 
            text="Estádio", 
            font=("Segoe UI", 10, "bold")
        ).grid(row=current_row, column=0, columnspan=4, pady=(10,5), sticky="w")
        
        current_row += 1
        for source in SOURCES["shared"]:
            ttk.Label(
                self.master, 
                text=source
            ).grid(row=current_row, column=0, padx=5, pady=3, sticky="e")
            
            image_list = self.get_images_for_source(source)
            combo_var = tk.StringVar()
            combo = ttk.Combobox(
                self.master, 
                textvariable=combo_var, 
                values=image_list, 
                width=35
            )
            combo.grid(row=current_row, column=1, columnspan=3, padx=5, pady=3, sticky="ew")
            self.dropdowns[source] = combo
            current_row += 1
        
        ttk.Label(
            self.master, 
            text="Jogador 1", 
            font=("Segoe UI", 10, "bold")
        ).grid(row=current_row, column=0, columnspan=2, pady=(15, 0))
        
        ttk.Label(
            self.master, 
            text="Jogador 2", 
            font=("Segoe UI", 10, "bold")
        ).grid(row=current_row, column=2, columnspan=2, pady=(15, 0))
        
        current_row += 1
        
        ttk.Label(
            self.master, 
            text="Deck:"
        ).grid(row=current_row, column=0, padx=5, pady=3, sticky="e")
        
        ttk.Entry(
            self.master,
            textvariable=self.deck_paths["player1"],
            width=25
        ).grid(row=current_row, column=1, padx=5, pady=3, sticky="ew")

        ttk.Label(
            self.master, 
            text="Deck:"
        ).grid(row=current_row, column=2, padx=5, pady=3, sticky="e")
        
        ttk.Entry(
            self.master,
            textvariable=self.deck_paths["player2"],
            width=25
        ).grid(row=current_row, column=3, padx=5, pady=3, sticky="ew")
        
        current_row += 1
        
        ttk.Button(
            self.master,
            text="Selecionar",
            command=lambda: self.select_deck_folder("player1")
        ).grid(row=current_row, column=0, columnspan=2, padx=5, pady=3)
        
        ttk.Button(
            self.master,
            text="Selecionar",
            command=lambda: self.select_deck_folder("player2")
        ).grid(row=current_row, column=2, columnspan=2, padx=5, pady=3)
        
        current_row += 1
        
        max_sources = max(len(SOURCES["player1"]), len(SOURCES["player2"]))
        for i in range(max_sources):
            if i < len(SOURCES["player1"]):
                self.create_dropdown(SOURCES["player1"][i], current_row+i, 0, 1)
            if i < len(SOURCES["player2"]):
                self.create_dropdown(SOURCES["player2"][i], current_row+i, 2, 3)
        
        row = current_row + max_sources
        ttk.Button(
            self.master, 
            text="Atualizar Tudo no OBS", 
            command=self.update_obs
        ).grid(row=row, column=0, columnspan=2, pady=10, padx=5, sticky="ew")
        
        ttk.Button(
            self.master, 
            text="Recarregar do OBS", 
            command=self.load_obs_settings
        ).grid(row=row, column=2, columnspan=2, pady=10, padx=5, sticky="ew")
        
        ttk.Button(
            self.master, 
            text="Atualizar Listas de Imagens", 
            command=self.refresh_images
        ).grid(row=row+1, column=0, columnspan=4, pady=10, padx=5, sticky="ew")
        
        self.master.grid_columnconfigure(1, weight=1)
        self.master.grid_columnconfigure(3, weight=1)
    
    def select_deck_folder(self, player):
        folder = filedialog.askdirectory(
            title=f"Selecionar pasta do deck do {player.replace('player', 'Jogador ')}",
            initialdir=self.deck_paths[player].get() or FOLDERS["pokemon"]
        )
        
        if folder:
            self.deck_paths[player].set(folder)
            self.images[f"{player}_deck"] = get_image_files(folder)
            self.update_player_dropdowns(player)
            save_deck_paths(
                self.deck_paths["player1"].get(),
                self.deck_paths["player2"].get()
            )
    
    def update_player_dropdowns(self, player):
        for source in SOURCES[player]:
            dropdown = self.dropdowns.get(source)
            if dropdown and "prize" not in source.lower():
                current = dropdown.get()
                image_list = self.get_images_for_source(source)
                dropdown['values'] = image_list
                if current in image_list:
                    dropdown.set(current)
                else:
                    dropdown.set('')
    
    def create_dropdown(self, source, row, label_col, dropdown_col):
        ttk.Label(
            self.master, 
            text=source
        ).grid(row=row, column=label_col, padx=5, pady=3, sticky="e")
        
        image_list = self.get_images_for_source(source)
        combo_var = tk.StringVar()
        combo = ttk.Combobox(
            self.master, 
            textvariable=combo_var, 
            values=image_list, 
            width=25
        )
        combo.grid(row=row, column=dropdown_col, padx=5, pady=3, sticky="ew")
        self.dropdowns[source] = combo
    
    def get_images_for_source(self, source):
        if "prize" in source.lower():
            return self.images["prizes"]
        elif source.lower() == "estadio":
            return self.images["estadio"]
        elif source in SOURCES["player1"]:
            if self.deck_paths["player1"].get() and self.images["player1_deck"]:
                return self.images["player1_deck"]
            return self.images["pokemon"]
        elif source in SOURCES["player2"]:
            if self.deck_paths["player2"].get() and self.images["player2_deck"]:
                return self.images["player2_deck"]
            return self.images["pokemon"]
        else:
            return self.images["pokemon"]
    
    def get_folder_for_source(self, source):
        if "prize" in source.lower():
            return FOLDERS["prizes"]
        elif source.lower() == "estadio":
            return FOLDERS["estadio"]
        elif source in SOURCES["player1"]:
            if self.deck_paths["player1"].get() and os.path.isdir(self.deck_paths["player1"].get()):
                return self.deck_paths["player1"].get()
            return FOLDERS["pokemon"]
        elif source in SOURCES["player2"]:
            if self.deck_paths["player2"].get() and os.path.isdir(self.deck_paths["player2"].get()):
                return self.deck_paths["player2"].get()
            return FOLDERS["pokemon"]
        else:
            return FOLDERS["pokemon"]
    
    def apply_theme(self):
        style = ttk.Style()
        if self.dark_mode.get():
            self.master.configure(bg="#2e2e2e")
            style.theme_use("clam")
            style.configure(".", background="#2e2e2e", foreground="white")
            style.configure("TLabel", background="#2e2e2e", foreground="white")
            style.configure("TButton", background="#3e3e3e", foreground="white")
            style.configure("TCombobox", fieldbackground="#3e3e3e", foreground="white")
            style.configure("TCheckbutton", background="#2e2e2e", foreground="white")
            style.configure("TEntry", fieldbackground="#3e3e3e", foreground="white")
            
            self.master.option_add('*TCombobox*Listbox.background', '#3e3e3e')
            self.master.option_add('*TCombobox*Listbox.foreground', 'white')
        else:
            self.master.configure(bg="SystemButtonFace")
            style.theme_use("default")
    
    def refresh_images(self):
        self.images = {
            "pokemon": get_image_files(FOLDERS["pokemon"]),
            "estadio": get_image_files(FOLDERS["estadio"]),
            "prizes": get_image_files(FOLDERS["prizes"]),
            "player1_deck": get_image_files(self.deck_paths["player1"].get()),
            "player2_deck": get_image_files(self.deck_paths["player2"].get())
        }

        for source, dropdown in self.dropdowns.items():
            current = dropdown.get()
            image_list = self.get_images_for_source(source)
            dropdown['values'] = image_list
            if current in image_list:
                dropdown.set(current)
            else:
                dropdown.set('')
    
    def load_obs_settings(self):
        if not self.ws:
            print("Não conectado ao OBS.")
            return
        
        self.refresh_images()
        
        for source, dropdown in self.dropdowns.items():
            try:
                response = self.ws.call(requests.GetInputSettings(inputName=source))
                settings = response.datain.get('inputSettings', {})
                
                if 'file' in settings:
                    filename = os.path.basename(settings['file'])
                    image_list = self.get_images_for_source(source)
                    
                    if filename in image_list:
                        dropdown.set(filename)
                    else:
                        dropdown.set(filename)
                        print(f"AVISO: Imagem '{filename}' não encontrada localmente.")
                else:
                    dropdown.set('')
            except Exception as e:
                print(f"Erro ao obter configurações para {source}: {e}")
                dropdown.set('')
    
    def update_obs(self):
        if not self.ws:
            print("Não conectado ao OBS.")
            return
        
        for source, dropdown in self.dropdowns.items():
            filename = dropdown.get()
            if not filename:
                continue
                
            folder = self.get_folder_for_source(source)
            full_path = os.path.abspath(os.path.join(folder, filename))
            
            if not os.path.exists(full_path):
                print(f"ERRO: Arquivo não encontrado: {full_path}")
                continue
                
            try:
                self.ws.call(requests.SetInputSettings(
                    inputName=source,
                    inputSettings={"file": full_path},
                    overlay=True
                ))
            except Exception as e:
                print(f"Erro ao atualizar {source}: {e}")
    
    def __del__(self):
        if hasattr(self, 'ws') and self.ws:
            try:
                self.ws.disconnect()
            except:
                pass

if __name__ == "__main__":
    for folder_path in FOLDERS.values():
        if not os.path.exists(folder_path):
            try:
                os.makedirs(folder_path)
                print(f"Pasta criada: {folder_path}")
            except:
                print(f"ERRO: Não foi possível criar a pasta: {folder_path}")
    
    root = tk.Tk()
    
    if os.path.exists(ICONE_APP_PATH):
        try:
            root.iconbitmap(ICONE_APP_PATH)
        except:
            pass
    
    app = OBSController(root)
    
    root.protocol("WM_DELETE_WINDOW", lambda: (app.__del__(), root.destroy()))   
    root.mainloop()
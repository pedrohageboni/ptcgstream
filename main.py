import os
import tkinter as tk
from tkinter import ttk
from obswebsocket import obsws, requests, exceptions as obsexceptions
import json
import sys

CONFIG_FILE_NAME = "config.json"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def get_expected_config_structure_example():
    """Returns a string showing an example of the expected config.json structure."""
    return """
{
  "obs_websocket": {
    "host": "localhost",
    "port": 4455,
    "password": "YOUR_OBS_PASSWORD_HERE"
  },
  "paths": {
    "main_image_directory_name": "imagens",
    "icon_file_name": "manafix.ico",
    "subfolders": {
      "pokemon": "pokemon",
      "estadio": "estadios",
      "prizes": "prizes"
    }
  },
  "obs_sources": {
    "player1": ["p1_ativo", "p1_banco1", "p1_banco2", "p1_banco3", "p1_banco4", "p1_banco5", "prize1"],
    "player2": ["p2_ativo", "p2_banco1", "p2_banco2", "p2_banco3", "p2_banco4", "p2_banco5", "prize2"],
    "shared": ["estadio"]
  },
  "ui_settings": {
    "default_dark_mode": true
  }
}
"""

def load_config(filepath):
    """Loads configuration from a JSON file. Exits if not found or malformed."""
    essential_keys = ["obs_websocket", "paths", "obs_sources", "ui_settings"]
    essential_websocket_keys = ["host", "port", "password"]
    essential_paths_keys = ["main_image_directory_name", "icon_file_name", "subfolders"]
    essential_subfolders_keys = ["pokemon", "estadio", "prizes"]
    essential_obs_sources_keys = ["player1", "player2", "shared"]
    essential_ui_settings_keys = ["default_dark_mode"]


    try:
        with open(filepath, 'r') as f:
            loaded_config = json.load(f)
        print(f"Configuração carregada de: {filepath}")

        # Validate essential top-level keys
        for key in essential_keys:
            if key not in loaded_config:
                print(f"ERRO FATAL: Chave essencial '{key}' não encontrada em '{filepath}'.")
                print("Verifique se o seu config.json está completo.")
                print("\nEstrutura esperada (exemplo):\n" + get_expected_config_structure_example())
                sys.exit(1)
        
        # Validate essential sub-keys
        for key in essential_websocket_keys:
            if key not in loaded_config["obs_websocket"]:
                print(f"ERRO FATAL: Chave essencial 'obs_websocket.{key}' não encontrada.")
                sys.exit(1)
        for key in essential_paths_keys:
            if key not in loaded_config["paths"]:
                print(f"ERRO FATAL: Chave essencial 'paths.{key}' não encontrada.")
                sys.exit(1)
        for key in essential_subfolders_keys:
            if key not in loaded_config["paths"]["subfolders"]:
                print(f"ERRO FATAL: Chave essencial 'paths.subfolders.{key}' não encontrada.")
                sys.exit(1)
        for key in essential_obs_sources_keys:
            if key not in loaded_config["obs_sources"]:
                print(f"ERRO FATAL: Chave essencial 'obs_sources.{key}' não encontrada.")
                sys.exit(1)
        for key in essential_ui_settings_keys:
            if key not in loaded_config["ui_settings"]:
                print(f"ERRO FATAL: Chave essencial 'ui_settings.{key}' não encontrada.")
                sys.exit(1)

        return loaded_config
        
    except FileNotFoundError:
        print(f"ERRO FATAL: Arquivo de configuração '{filepath}' não encontrado.")
        print("Por favor, crie um arquivo 'config.json' neste diretório com as configurações necessárias.")
        print("\nExemplo da estrutura esperada para 'config.json':\n" + get_expected_config_structure_example())
        sys.exit(1) # Exit the application
    except json.JSONDecodeError as e:
        print(f"ERRO FATAL: Formato JSON inválido no arquivo de configuração '{filepath}': {e}")
        print("Por favor, verifique a sintaxe do seu 'config.json'.")
        sys.exit(1) # Exit the application
    except Exception as e: # Catch any other unexpected error during loading
        print(f"ERRO FATAL inesperado ao carregar a configuração '{filepath}': {e}")
        sys.exit(1)


# Load configuration at the start
CONFIG_PATH = os.path.join(BASE_DIR, CONFIG_FILE_NAME)
APP_CONFIG = load_config(CONFIG_PATH) # This will now exit if config is bad

# --- Use Loaded Configuration (This part remains the same) ---
# OBS WebSocket settings
HOST = APP_CONFIG["obs_websocket"]["host"]
PORT = APP_CONFIG["obs_websocket"]["port"]
PASSWORD = APP_CONFIG["obs_websocket"]["password"]

# Paths
MAIN_IMAGE_DIR_NAME = APP_CONFIG["paths"]["main_image_directory_name"]
ICONE_APP_NAME = APP_CONFIG["paths"]["icon_file_name"]
SUBFOLDER_POKEMON = APP_CONFIG["paths"]["subfolders"]["pokemon"]
SUBFOLDER_ESTADIO = APP_CONFIG["paths"]["subfolders"]["estadio"]
SUBFOLDER_PRIZES = APP_CONFIG["paths"]["subfolders"]["prizes"]

MAIN_IMAGE_DIR = os.path.join(BASE_DIR, MAIN_IMAGE_DIR_NAME)
POKEMON_FOLDER_PATH = os.path.join(MAIN_IMAGE_DIR, SUBFOLDER_POKEMON)
ESTADIO_FOLDER_PATH = os.path.join(MAIN_IMAGE_DIR, SUBFOLDER_ESTADIO)
PRIZES_FOLDER_PATH = os.path.join(MAIN_IMAGE_DIR, SUBFOLDER_PRIZES)
ICONE_APP_PATH = os.path.join(BASE_DIR, ICONE_APP_NAME)

# OBS Source names
P1_SOURCES = APP_CONFIG["obs_sources"]["player1"]
P2_SOURCES = APP_CONFIG["obs_sources"]["player2"]
SHARED_SOURCES = APP_CONFIG["obs_sources"]["shared"]
ALL_OBS_SOURCES = P1_SOURCES + P2_SOURCES + SHARED_SOURCES

# UI Settings
DEFAULT_DARK_MODE = APP_CONFIG["ui_settings"]["default_dark_mode"]


# --- Helper Functions (ensure_folder_exists, get_image_files_from_folder, connect_obs_websocket) ---
# (These functions remain the same as your previous version)
def ensure_folder_exists(folder_path):
    if not os.path.isdir(folder_path):
        try:
            os.makedirs(folder_path, exist_ok=True)
            print(f"Pasta '{folder_path}' criada.")
        except OSError as e:
            print(f"ERRO: Não foi possível criar a pasta: {folder_path} - {e}")
            return False
    return True

def get_image_files_from_folder(folder_path):
    if not ensure_folder_exists(folder_path):
        return []
    try:
        return sorted([f for f in os.listdir(folder_path) if f.lower().endswith(('.png', '.jpg', '.jpeg'))])
    except Exception as e:
        print(f"ERRO ao ler a pasta de imagens '{folder_path}': {e}")
        return []

def connect_obs_websocket():
    ws = obsws(HOST, PORT, PASSWORD)
    try:
        ws.connect()
        print("Conectado ao OBS.")
        return ws
    except obsexceptions.ConnectionFailure:
        print("ERRO: Não foi possível conectar ao OBS. Verifique se o OBS está aberto e o WebSocket server está habilitado com a senha correta (config.json).")
        if PASSWORD == "YOUR_OBS_PASSWORD_HERE": # Match example password
            print(">>>> Lembre-se de ATUALIZAR a senha do OBS WebSocket em config.json! <<<<")
        return None
    except Exception as e:
        print(f"ERRO inesperado ao conectar ao OBS: {e}")
        return None

class OBSSwitcherApp:
    # ... (The rest of your OBSSwitcherApp class remains the same) ...
    # __init__, get_image_config_for_source, set_theme,
    # refresh_all_image_lists_ui, load_current_obs_settings,
    # update_all_obs, __del__

    def __init__(self, master):
        self.master = master
        master.title("Manafix OBS Control (Config via JSON)") 

        self.ws = connect_obs_websocket()

        self.pokemon_image_files = get_image_files_from_folder(POKEMON_FOLDER_PATH)
        self.estadio_image_files = get_image_files_from_folder(ESTADIO_FOLDER_PATH)
        self.prize_image_files = get_image_files_from_folder(PRIZES_FOLDER_PATH)

        self.dropdowns = {}
        self.dark_mode = tk.BooleanVar(value=DEFAULT_DARK_MODE)
        self.master.configure(bg="#2e2e2e" if self.dark_mode.get() else "SystemButtonFace")
        self.set_theme()

        current_row = 0
        ttk.Checkbutton(master, text="Modo Escuro", variable=self.dark_mode, command=self.set_theme).grid(
            row=current_row, column=4, padx=10, pady=10, sticky="e")

        current_row += 1
        ttk.Label(master, text="Estádio", font=("Segoe UI", 10, "bold")).grid(
            row=current_row, column=0, columnspan=4, pady=(10,5), sticky="w")
        current_row += 1
        for source_name in SHARED_SOURCES: 
            ttk.Label(master, text=source_name).grid(row=current_row, column=0, padx=5, pady=3, sticky="e")
            _, image_list = self.get_image_config_for_source(source_name)
            combo_var = tk.StringVar()
            combo = ttk.Combobox(master, textvariable=combo_var, values=image_list, width=35)
            combo.grid(row=current_row, column=1, columnspan=3, padx=5, pady=3, sticky="ew")
            self.dropdowns[source_name] = combo
            current_row += 1

        ttk.Label(master, text="Jogador 1", font=("Segoe UI", 10, "bold")).grid(
            row=current_row, column=0, columnspan=2, pady=(15, 0))
        ttk.Label(master, text="Jogador 2", font=("Segoe UI", 10, "bold")).grid(
            row=current_row, column=2, columnspan=2, pady=(15, 0))
        current_row += 1

        max_player_sources = max(len(P1_SOURCES), len(P2_SOURCES)) 
        start_row_for_players = current_row

        for i in range(max_player_sources):
            if i < len(P1_SOURCES):
                p1_source = P1_SOURCES[i]
                ttk.Label(master, text=p1_source).grid(row=start_row_for_players + i, column=0, padx=5, pady=3, sticky="e")
                _, image_list = self.get_image_config_for_source(p1_source)
                p1_var = tk.StringVar()
                p1_combo = ttk.Combobox(master, textvariable=p1_var, values=image_list, width=25)
                p1_combo.grid(row=start_row_for_players + i, column=1, padx=5, pady=3)
                self.dropdowns[p1_source] = p1_combo
            
            if i < len(P2_SOURCES):
                p2_source = P2_SOURCES[i]
                ttk.Label(master, text=p2_source).grid(row=start_row_for_players + i, column=2, padx=20, pady=3, sticky="e")
                _, image_list = self.get_image_config_for_source(p2_source)
                p2_var = tk.StringVar()
                p2_combo = ttk.Combobox(master, textvariable=p2_var, values=image_list, width=25)
                p2_combo.grid(row=start_row_for_players + i, column=3, padx=5, pady=3)
                self.dropdowns[p2_source] = p2_combo
        
        current_row = start_row_for_players + max_player_sources

        ttk.Button(master, text="Atualizar Tudo no OBS", command=self.update_all_obs).grid(
            row=current_row, column=0, columnspan=2, pady=10, padx=5, sticky="ew")
        ttk.Button(master, text="Recarregar do OBS", command=self.load_current_obs_settings).grid(
            row=current_row, column=2, columnspan=2, pady=10, padx=5, sticky="ew")
        current_row +=1
        ttk.Button(master, text="Atualizar Listas de Imagens", command=self.refresh_all_image_lists_ui).grid(
            row=current_row, column=0, columnspan=4, pady=10, padx=5, sticky="ew")

        master.grid_columnconfigure(1, weight=1)
        master.grid_columnconfigure(3, weight=1)

        if self.ws:
            self.master.after(200, self.load_current_obs_settings)
        else:
            print("OBS não conectado, pulando carregamento inicial das configurações.")

    def get_image_config_for_source(self, source_name):
        # Use APP_CONFIG directly for subfolder names
        if source_name.lower() == APP_CONFIG["paths"]["subfolders"]["estadio"].lower():
            return ESTADIO_FOLDER_PATH, self.estadio_image_files
        elif "prize" in source_name.lower():
            return PRIZES_FOLDER_PATH, self.prize_image_files
        else: 
            return POKEMON_FOLDER_PATH, self.pokemon_image_files
    
    def set_theme(self):
        style = ttk.Style()
        if self.dark_mode.get():
            self.master.configure(bg="#2e2e2e")
            style.theme_use("clam")
            style.configure(".", background="#2e2e2e", foreground="white", borderwidth=0)
            style.configure("TLabel", background="#2e2e2e", foreground="white", padding=2)
            style.configure("TButton", background="#3e3e3e", foreground="white", padding=5, relief="flat")
            style.map("TButton", background=[('active', '#5e5e5e'), ('pressed', '#484848')])
            style.configure("TCombobox", fieldbackground="#3e3e3e", background="#3e3e3e", foreground="white", arrowcolor="white", padding=3)
            style.map('TCombobox', fieldbackground=[('readonly', '#3e3e3e'), ('focus', '#484848')])
            style.map('TCombobox', selectbackground=[('readonly', '#3e3e3e')]) 
            style.map('TCombobox', selectforeground=[('readonly', 'white')])
            style.configure("TCheckbutton", background="#2e2e2e", foreground="white", indicatorcolor="#5e5e5e", padding=5)
            style.map("TCheckbutton", indicatorcolor=[('selected', 'white'), ('active', '#5e5e5e')])
            self.master.option_add('*TCombobox*Listbox.background', '#3e3e3e')
            self.master.option_add('*TCombobox*Listbox.foreground', 'white')
            self.master.option_add('*TCombobox*Listbox.selectBackground', '#0078D7')
            self.master.option_add('*TCombobox*Listbox.selectForeground', 'white')
        else:
            self.master.configure(bg="SystemButtonFace")
            style.theme_use("default")
            style.configure(".", background="SystemButtonFace", foreground="black", borderwidth=1)
            style.configure("TLabel", background="SystemButtonFace", foreground="black")
            style.configure("TButton") 
            style.map("TButton", background=[])
            style.configure("TCombobox", fieldbackground="white", background="white", foreground="black", arrowcolor="black")
            style.map('TCombobox', fieldbackground=[('readonly', 'white')])
            style.map('TCombobox', selectbackground=[('readonly', 'SystemHighlight')])
            style.map('TCombobox', selectforeground=[('readonly', 'SystemHighlightText')])
            style.configure("TCheckbutton") 
            style.map("TCheckbutton", indicatorcolor=[])
            self.master.option_add('*TCombobox*Listbox.background', 'white')
            self.master.option_add('*TCombobox*Listbox.foreground', 'black')
            self.master.option_add('*TCombobox*Listbox.selectBackground', 'SystemHighlight')
            self.master.option_add('*TCombobox*Listbox.selectForeground', 'SystemHighlightText')


    def refresh_all_image_lists_ui(self):
        print("Atualizando todas as listas de imagens das pastas...")
        self.pokemon_image_files = get_image_files_from_folder(POKEMON_FOLDER_PATH)
        self.estadio_image_files = get_image_files_from_folder(ESTADIO_FOLDER_PATH)
        self.prize_image_files = get_image_files_from_folder(PRIZES_FOLDER_PATH)
        print(f"  Pokémon: {len(self.pokemon_image_files)}, Estádios: {len(self.estadio_image_files)}, Prêmios: {len(self.prize_image_files)}")

        for source_name, dropdown_widget in self.dropdowns.items():
            current_selection = dropdown_widget.get()
            _, relevant_image_list = self.get_image_config_for_source(source_name)
            
            dropdown_widget['values'] = relevant_image_list
            if current_selection in relevant_image_list:
                dropdown_widget.set(current_selection)
            elif relevant_image_list:
                dropdown_widget.set('')
            else: 
                dropdown_widget.set('')
        print("Dropdowns atualizados com as novas listas de imagens.")

    def load_current_obs_settings(self):
        if not self.ws:
            print("Não conectado ao OBS. Não é possível carregar as configurações.")
            return

        print("Carregando configurações atuais do OBS...")
        self.refresh_all_image_lists_ui() 

        for source_name, dropdown_widget in self.dropdowns.items():
            try:
                response = self.ws.call(requests.GetInputSettings(inputName=source_name))
                current_settings = response.datain.get('inputSettings', {})
                if 'file' in current_settings:
                    full_path_from_obs = current_settings['file']
                    filename_from_obs = os.path.basename(full_path_from_obs)
                    
                    _, relevant_local_list = self.get_image_config_for_source(source_name)

                    if filename_from_obs in relevant_local_list:
                        dropdown_widget.set(filename_from_obs)
                        # print(f"  Fonte '{source_name}' definida para '{filename_from_obs}' (encontrada localmente).")
                    else:
                        dropdown_widget.set(filename_from_obs) 
                        print(f"  AVISO: Imagem '{filename_from_obs}' para '{source_name}' (do OBS) não encontrada na pasta local esperada. Exibindo nome do arquivo do OBS.")
                else:
                    dropdown_widget.set('')
                    # print(f"  Fonte '{source_name}' não parece ser uma fonte de imagem ou não tem arquivo definido no OBS.")
            except obsexceptions.OBSSDKError as e:
                print(f"Erro ao obter configurações para {source_name}: {e} (Fonte existe no OBS?)")
                dropdown_widget.set('')
            except Exception as e:
                print(f"Erro inesperado ao processar {source_name}: {e}")
                dropdown_widget.set('')

    def update_all_obs(self):
        if not self.ws:
            print("Não conectado ao OBS. Não é possível atualizar.")
            return

        print("Atualizando OBS...")
        for source_name, dropdown_widget in self.dropdowns.items():
            selected_filename = dropdown_widget.get()
            if selected_filename:
                image_folder_path, _ = self.get_image_config_for_source(source_name)
                full_image_path = os.path.abspath(os.path.join(image_folder_path, selected_filename))

                if not os.path.exists(full_image_path):
                    print(f"ERRO: Arquivo de imagem não encontrado em '{full_image_path}' para a fonte '{source_name}'. Verifique o nome do arquivo ou atualize a lista de imagens.")
                    if os.path.isabs(selected_filename) and os.path.exists(selected_filename):
                        print(f"  AVISO: '{selected_filename}' parece ser um caminho absoluto. Tentando usar diretamente...")
                        full_image_path = selected_filename 
                    else:
                        continue 

                try:
                    self.ws.call(requests.SetInputSettings(
                        inputName=source_name,
                        inputSettings={"file": full_image_path},
                        overlay=True 
                    ))
                    # print(f"  Fonte '{source_name}' atualizada para '{selected_filename}'")
                except obsexceptions.OBSSDKError as e:
                    print(f"Erro SDK OBS ao atualizar {source_name}: {e} (Fonte existe? É uma fonte de imagem?)")
                except Exception as e:
                    print(f"Erro ao atualizar {source_name}: {e}")
            else: 
                try:
                    self.ws.call(requests.SetInputSettings(inputName=source_name, inputSettings={"file": ""}, overlay=True))
                    # print(f"  Fonte '{source_name}' limpa no OBS (sem imagem selecionada).")
                except Exception as e:
                    print(f"  Erro ao tentar limpar a fonte {source_name} no OBS: {e}")
        print("Atualização do OBS concluída.")


    def __del__(self):
        if self.ws:
            try:
                self.ws.disconnect()
                print("Desconectado do OBS.")
            except Exception as e:
                print(f"Erro ao desconectar do OBS: {e}")


# --- Main Application Execution ---
if __name__ == "__main__":
    root = tk.Tk()
    if os.path.exists(ICONE_APP_PATH):
        try:
            root.iconbitmap(ICONE_APP_PATH)
        except tk.TclError:
            print(f"AVISO: Não foi possível carregar o ícone: {ICONE_APP_PATH}. Verifique se é um arquivo .ico válido (config.json).")
    else:
        print(f"AVISO: Arquivo de ícone não encontrado: {ICONE_APP_PATH} (config.json).")

    app = OBSSwitcherApp(root)

    def on_closing_window():
        print("Fechando aplicativo...")
        if hasattr(app, '__del__'): # Call custom destructor if it exists
            app.__del__()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_closing_window)
    root.mainloop()
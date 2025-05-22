import os
import tkinter as tk
from tkinter import ttk
from obswebsocket import obsws, requests, exceptions as obsexceptions # Import exceptions

# coisas do websocket
HOST = "localhost"
PORT = 4455
PASSWORD = "123456"  # coloca sua senha

# nome das fontes no obs
p1_sources = ["p1_ativo", "p1_banco1", "p1_banco2", "p1_banco3", "p1_banco4", "p1_banco5"]
p2_sources = ["p2_ativo", "p2_banco1", "p2_banco2", "p2_banco3", "p2_banco4", "p2_banco5"]
all_sources = p1_sources + p2_sources # Helper list

# pasta de imagens e ícone
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGE_FOLDER = os.path.join(BASE_DIR, "imagens")
iconeapp = os.path.join(BASE_DIR, "manafix.ico")

# pega as imagens
def get_image_files(folder):
    try:
        return [f for f in os.listdir(folder) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    except FileNotFoundError:
        print(f"ERRO: Pasta de imagens não encontrada: {folder}")
        return []

# liga no obs
def connect_obs():
    ws = obsws(HOST, PORT, PASSWORD)
    try:
        ws.connect()
        print("Conectado ao OBS.")
        return ws
    except obsexceptions.ConnectionFailure:
        print("ERRO: Não foi possível conectar ao OBS. Verifique se o OBS está aberto e o WebSocket server está habilitado com a senha correta.")
        return None
    except Exception as e:
        print(f"ERRO inesperado ao conectar ao OBS: {e}")
        return None

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
        for i, p1_source in enumerate(p1_sources, start=1):
            ttk.Label(master, text=p1_source).grid(row=i, column=0, padx=5, pady=3, sticky="e")
            p1_var = tk.StringVar()
            p1_combo = ttk.Combobox(master, textvariable=p1_var, values=self.image_files, width=25)
            p1_combo.grid(row=i, column=1, padx=5, pady=3)
            self.dropdowns[p1_source] = p1_combo

        for i, p2_source in enumerate(p2_sources, start=1):
            ttk.Label(master, text=p2_source).grid(row=i, column=2, padx=20, pady=3, sticky="e")
            p2_var = tk.StringVar()
            p2_combo = ttk.Combobox(master, textvariable=p2_var, values=self.image_files, width=25)
            p2_combo.grid(row=i, column=3, padx=5, pady=3)
            self.dropdowns[p2_source] = p2_combo
        
        if self.ws:
            # Schedule load_current_obs_settings to run after 100ms
            # This gives OBS and Tkinter a moment to settle.
            # Adjust the delay (in milliseconds) if needed (e.g., 200 or 500).
            print("Scheduling initial OBS settings load...")
            self.master.after(200, self.load_current_obs_settings) # Increased delay to 200ms
        else:
            print("OBS not connected, skipping initial settings load.")

        ttk.Button(master, text="Atualizar Tudo", command=self.update_all).grid(row=max(len(p1_sources), len(p2_sources)) + 1, column=0, columnspan=4, pady=10)
        # Add a refresh button to re-fetch from OBS
        ttk.Button(master, text="Recarregar do OBS", command=self.load_current_obs_settings).grid(row=max(len(p1_sources), len(p2_sources)) + 1, column=4, pady=10, padx=5)


    def set_theme(self):
        style = ttk.Style()
        if self.dark_mode.get():
            self.master.configure(bg="#2e2e2e")
            style.theme_use("clam") # 'clam' or 'alt' or 'default' often work well for dark themes
            style.configure(".", background="#2e2e2e", foreground="white") # General background
            style.configure("TLabel", background="#2e2e2e", foreground="white")
            style.configure("TButton", background="#3e3e3e", foreground="white", borderwidth=1)
            style.map("TButton", background=[('active', '#5e5e5e')])
            style.configure("TCombobox", fieldbackground="#3e3e3e", background="#3e3e3e", foreground="white", arrowcolor="white")
            style.map('TCombobox', fieldbackground=[('readonly', '#3e3e3e')])
            style.map('TCombobox', selectbackground=[('readonly', '#3e3e3e')])
            style.map('TCombobox', selectforeground=[('readonly', 'white')])
            style.configure("TCheckbutton", background="#2e2e2e", foreground="white", indicatorcolor="#5e5e5e")
            style.map("TCheckbutton", indicatorcolor=[('selected', 'white'), ('active', '#5e5e5e')])

        else:
            self.master.configure(bg="SystemButtonFace")
            style.theme_use("default") # Or 'vista' or 'xpnative' on Windows
            style.configure(".", background="SystemButtonFace", foreground="black")
            style.configure("TLabel", background="SystemButtonFace", foreground="black")
            style.configure("TButton", background="SystemButtonFace", foreground="black")
            style.configure("TCombobox", fieldbackground="white", background="white", foreground="black", arrowcolor="black")
            style.map('TCombobox', fieldbackground=[('readonly', 'white')])
            style.map('TCombobox', selectbackground=[('readonly', 'SystemHighlight')])
            style.map('TCombobox', selectforeground=[('readonly', 'SystemHighlightText')])
            style.configure("TCheckbutton", background="SystemButtonFace", foreground="black")

    def load_current_obs_settings(self):
        if not self.ws:
            print("Não conectado ao OBS. Não é possível carregar as configurações.")
            return

        print("Carregando configurações atuais do OBS...")
        for source_name, dropdown_widget in self.dropdowns.items():
            try:
                response = self.ws.call(requests.GetInputSettings(inputName=source_name))
                # The actual settings are usually under response.inputSettings or response.settings
                # For image sources, it's typically response.inputSettings['file']
                current_settings = response.datain.get('inputSettings', {}) # Use .get for safety
                if 'file' in current_settings:
                    full_path = current_settings['file']
                    filename = os.path.basename(full_path)
                    if filename in self.image_files:
                        dropdown_widget.set(filename)
                        print(f"  Fonte '{source_name}' definida para '{filename}'")
                    else:
                        dropdown_widget.set('') # Clear if file not in our list, or show full path
                        print(f"  AVISO: Imagem '{filename}' para '{source_name}' não encontrada na pasta local. Definindo como vazio.")
                else:
                    dropdown_widget.set('') # Clear if no file property
                    print(f"  Fonte '{source_name}' não parece ser uma fonte de imagem ou não tem arquivo definido.")

            except obsexceptions.OBSSDKError as e:
                # This can happen if the source doesn't exist in OBS
                print(f"Erro ao obter configurações para {source_name}: {e} (Fonte existe no OBS?)")
                dropdown_widget.set('') # Clear dropdown if source not found or error
            except Exception as e:
                print(f"Erro inesperado ao processar {source_name}: {e}")
                dropdown_widget.set('')

    def update_all(self):
        if not self.ws:
            print("Não conectado ao OBS. Não é possível atualizar.")
            # Optionally, try to reconnect here
            # self.ws = connect_obs()
            # if not self.ws: return
            return

        print("Atualizando OBS...")
        for source, dropdown in self.dropdowns.items():
            filename = dropdown.get()
            if filename:
                # Ensure we use an absolute path, especially if OBS runs with a different CWD
                image_path = os.path.abspath(os.path.join(IMAGE_FOLDER, filename))
                # Check if file exists before sending to OBS, to prevent errors
                if not os.path.exists(image_path):
                    print(f"ERRO: Arquivo de imagem não encontrado: {image_path} para a fonte {source}")
                    continue
                try:
                    self.ws.call(requests.SetInputSettings(
                        inputName=source,
                        inputSettings={"file": image_path},
                        overlay=True # overlay=True is often not needed for simple SetInputSettings
                                     # but keep if it was working for you
                    ))
                    print(f"  Fonte '{source}' atualizada para '{filename}'")
                except obsexceptions.OBSSDKError as e:
                    print(f"Erro SDK OBS ao atualizar {source}: {e} (Fonte existe? É uma fonte de imagem?)")
                except Exception as e:
                    print(f"Erro ao atualizar {source}: {e}")
            # else:
                # print(f"  Nenhuma imagem selecionada para {source}, não atualizando.")


    def __del__(self):
        if self.ws:
            try:
                self.ws.disconnect()
                print("Desconectado do OBS.")
            except Exception as e:
                print(f"Erro ao desconectar do OBS: {e}")


# roda o aplicativo
if __name__ == "__main__":
    root = tk.Tk()
    # Check if icon exists
    if os.path.exists(iconeapp):
        try:
            root.iconbitmap(iconeapp)
        except tk.TclError:
            print(f"AVISO: Não foi possível carregar o ícone: {iconeapp}. Verifique se é um arquivo .ico válido.")
    else:
        print(f"AVISO: Arquivo de ícone não encontrado: {iconeapp}")

    app = OBSSwitcherApp(root)
    
    # Handle window close event to ensure OBS disconnection
    def on_closing():
        print("Fechando aplicativo...")
        if hasattr(app, '__del__'): # Call custom destructor if it exists
            app.__del__()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()
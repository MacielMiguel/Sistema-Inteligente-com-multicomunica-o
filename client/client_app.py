import requests
import tkinter as tk
from tkinter import ttk, messagebox

API_URL = "http://localhost:5000"

def list_devices():
    try:
        response = requests.get(f"{API_URL}/devices")
        devices = response.json()
        device_listbox.delete(0, tk.END)
        for device in devices:
            device_listbox.insert(tk.END, device)
    except requests.exceptions.RequestException as e:
        messagebox.showerror("Erro", f"Erro ao listar dispositivos: {e}")

def toggle_device():
    device = device_listbox.get(device_listbox.curselection())
    if device:
        try:
            response = requests.post(f"{API_URL}/devices/{device}/toggle")
            messagebox.showinfo("Sucesso", response.json().get("message", "Dispositivo toggled"))
        except requests.exceptions.RequestException as e:
            messagebox.showerror("Erro", f"Erro ao togglar dispositivo: {e}")
    else:
        messagebox.showwarning("Atenção", "Selecione um dispositivo.")

def delete_device():
    device = device_listbox.get(device_listbox.curselection())
    if device:
        try:
            response = requests.delete(f"{API_URL}/devices/{device}")
            messagebox.showinfo("Sucesso", response.json().get("message", "Dispositivo deletado"))
            list_devices()
        except requests.exceptions.RequestException as e:
            messagebox.showerror("Erro", f"Erro ao deletar dispositivo: {e}")
    else:
        messagebox.showwarning("Atenção", "Selecione um dispositivo.")

def get_device_status():
    device = device_listbox.get(device_listbox.curselection())
    if device:
        try:
            response = requests.get(f"{API_URL}/devices/{device}")
            response.raise_for_status()
            device_data = response.json().get(device)
            if device_data:
                if device_data.get("type") == "AC":
                    status_label.config(text=f"Status: {device_data.get('status')}")
                    temperature_label.config(text=f"Temperatura: {device_data.get('temperature')}")
                    temperature_label.pack()
                else:
                    status_label.config(text=f"Status: {device_data.get('status')}")
                    temperature_label.pack_forget()  # Oculta o label de temperatura se não for um AC
                # Adicione outros labels para exibir outras informações do dispositivo
            else:
                status_label.config(text="Status: -")
                temperature_label.config(text="Temperatura: -")
                temperature_label.pack_forget()  # Mesma ocultação
        except requests.exceptions.RequestException as e:
            messagebox.showerror("Erro", f"Erro ao obter estado do dispositivo: {e}")
    else:
        messagebox.showwarning("Atenção", "Selecione um dispositivo.")

def edit_device():
    device = device_listbox.get(device_listbox.curselection())
    if device:
        try:
            # Abre uma nova janela para editar as informações do dispositivo
            edit_window = tk.Toplevel(root)
            edit_window.title(f"Editar {device}")

            # Obtém as informações atuais do dispositivo
            response = requests.get(f"{API_URL}/devices/{device}")
            device_info = response.json().get(device)

            # Cria labels e campos de entrada para cada informação do dispositivo
            labels = {}
            entries = {}
            for key, value in device_info.items():
                label = ttk.Label(edit_window, text=f"{key.capitalize()}:")
                label.grid(row=len(labels), column=0, padx=5, pady=5, sticky=tk.W)
                entry = ttk.Entry(edit_window)
                entry.insert(0, value)
                entry.grid(row=len(labels), column=1, padx=5, pady=5)
                labels[key] = label
                entries[key] = entry

            # Função para salvar as alterações
            def save_changes():
                new_info = {}
                for key, entry in entries.items():
                    new_info[key] = entry.get()
                try:
                    response = requests.put(f"{API_URL}/devices/{device}", json=new_info)
                    response.raise_for_status()
                    messagebox.showinfo("Sucesso", response.json().get("message", "Dispositivo atualizado"))
                    edit_window.destroy()
                    list_devices()
                except requests.exceptions.RequestException as e:
                    messagebox.showerror("Erro", f"Erro ao atualizar dispositivo: {e}")

            # Botão para salvar as alterações
            save_button = ttk.Button(edit_window, text="Salvar", command=save_changes)
            save_button.grid(row=len(labels), column=0, columnspan=2, pady=(10, 5))

        except requests.exceptions.RequestException as e:
            messagebox.showerror("Erro", f"Erro ao obter informações do dispositivo: {e}")
    else:
        messagebox.showwarning("Atenção", "Selecione um dispositivo para editar.")


# Função para lidar com operações sem seleção
def handle_operation(operation):
    def inner_function():
        if not device_listbox.curselection():
            messagebox.showwarning("Atenção", "Selecione um dispositivo para realizar esta operação.")
        else:
            operation()
    return inner_function

root = tk.Tk()
root.title("Controle de Dispositivos")

# Tema
style = ttk.Style()
style.theme_use("clam")

# Frame para a lista de dispositivos
device_frame = ttk.LabelFrame(root, text="Dispositivos")
device_frame.pack(padx=10, pady=10)

device_listbox = tk.Listbox(device_frame, height=10)
device_listbox.pack(padx=5, pady=5)

list_button = ttk.Button(device_frame, text="Listar Dispositivos", command=list_devices)
list_button.pack(pady=(0, 5))

# Frame para os botões de ação
action_frame = ttk.LabelFrame(root, text="Ações")
action_frame.pack(padx=10, pady=(0, 10))

# Usando a função handle_operation para criar os botões
toggle_button = ttk.Button(action_frame, text="Ligar/Desligar", command=handle_operation(toggle_device))
toggle_button.pack(side=tk.LEFT, padx=5)

delete_button = ttk.Button(action_frame, text="Deletar", command=handle_operation(delete_device))
delete_button.pack(side=tk.LEFT, padx=5)

status_button = ttk.Button(action_frame, text="Ver Estado", command=handle_operation(get_device_status))
status_button.pack(side=tk.LEFT, padx=5)

edit_button = ttk.Button(action_frame, text="Editar", command=handle_operation(edit_device))
edit_button.pack(side=tk.LEFT, padx=5)

# Frame para exibir o estado do dispositivo
status_frame = ttk.LabelFrame(root, text="Estado do Dispositivo")
status_frame.pack(padx=10, pady=(0, 10))

status_label = ttk.Label(status_frame, text="Status: -")
status_label.pack()

temperature_label = ttk.Label(status_frame, text="Temperatura: -")
temperature_label.pack()
temperature_label.pack_forget()

# Adicione outros labels para exibir outras informações do dispositivo

root.mainloop()
import socket
import os
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk

def send_file(server_ip, file_path, target_format):
    """Sends a file to the server for conversion."""
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((server_ip, 12345))
        
        file_name = os.path.basename(file_path)
        file_size = os.path.getsize(file_path)
        metadata = f"{file_name}|{target_format}|{file_size}"
        client_socket.sendall(metadata.encode(errors='ignore'))
        
        with open(file_path, "rb") as file:
            while chunk := file.read(4096):
                client_socket.sendall(chunk)
        
        response = client_socket.recv(1024).decode(errors='ignore')
        if response.isdigit():
            converted_size = int(response)
            output_file = f"converted_{file_name.split('.')[0]}.{target_format.lower()}"
            received_size = 0
            with open(output_file, "wb") as file:
                while received_size < converted_size:
                    data = client_socket.recv(4096)
                    if not data:
                        break
                    file.write(data)
                    received_size += len(data)
            messagebox.showinfo("Success", f"Converted file saved as {output_file}")
        else:
            messagebox.showerror("Error", f"Conversion failed: {response}")
        
    except Exception as e:
        messagebox.showerror("Error", f"Connection failed: {e}")
    finally:
        client_socket.close()

# GUI Setup
def select_file():
    file_path.set(filedialog.askopenfilename())

def start_conversion():
    ip = server_ip.get()
    file = file_path.get()
    format_selected = format_var.get()
    if not ip or not file or not format_selected:
        messagebox.showwarning("Warning", "Please enter all details!")
        return
    send_file(ip, file, format_selected)

# Initialize Tkinter
root = tk.Tk()
root.title("File Converter Client")
root.geometry("450x350")
root.configure(bg="#2c3e50")

style = ttk.Style()
style.configure("TButton", font=("Arial", 12), padding=5)
style.configure("TLabel", font=("Arial", 12), background="#2c3e50", foreground="white")
style.configure("TEntry", font=("Arial", 12), padding=5)
style.configure("TCombobox", font=("Arial", 12), padding=5)

server_ip = tk.StringVar()
file_path = tk.StringVar()
format_var = tk.StringVar()

frame = ttk.Frame(root, padding=20)
frame.pack(expand=True)

# Widgets
ttk.Label(frame, text="Server IP:").grid(row=0, column=0, sticky="w", pady=5)
ttk.Entry(frame, textvariable=server_ip, width=30).grid(row=0, column=1, pady=5)

ttk.Label(frame, text="Select File:").grid(row=1, column=0, sticky="w", pady=5)
ttk.Entry(frame, textvariable=file_path, width=30).grid(row=1, column=1, pady=5)
ttk.Button(frame, text="Browse", command=select_file).grid(row=1, column=2, padx=5)

formats = ["PNG", "JPG", "PDF", "DOCX", "XLSX", "CSV"]
ttk.Label(frame, text="Target Format:").grid(row=2, column=0, sticky="w", pady=5)
ttk.Combobox(frame, textvariable=format_var, values=formats, state="readonly").grid(row=2, column=1, pady=5)

ttk.Button(frame, text="Convert", command=start_conversion).grid(row=3, column=1, pady=10)

# Run GUI
root.mainloop()
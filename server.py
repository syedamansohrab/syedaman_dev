# Updated Server Code for Two-System Setup
import socket
import os
from PIL import Image
from docx2pdf import convert as docx_to_pdf
from pdf2docx import Converter
import pandas as pd

def convert_image(input_path, output_path, target_format):
    try:
        if target_format.upper() == "JPG":
            target_format = "JPEG"
        img = Image.open(input_path)
        if img.mode != "RGB":
            img = img.convert("RGB")
        img.save(output_path, format=target_format)
        return True
    except Exception as e:
        print(f"Image conversion error: {e}")
        return False

def convert_docx_to_pdf(input_path, output_path):
    try:
        docx_to_pdf(input_path, output_path)
        return True
    except Exception as e:
        print(f"DOCX to PDF conversion error: {e}")
        return False

def convert_pdf_to_docx(input_path, output_path):
    try:
        cv = Converter(input_path)
        cv.convert(output_path, start=0, end=None)
        cv.close()
        return True
    except Exception as e:
        print(f"PDF to DOCX conversion error: {e}")
        return False

def convert_csv_to_xlsx(input_path, output_path):
    try:
        df = pd.read_csv(input_path, encoding='utf-8', sep=None, engine='python')
        df.to_excel(output_path, index=False,engine='openpyxl')
        return True
    except Exception as e:
        print(f"CSV to XLSX conversion error: {e}")
        return False

def convert_xlsx_to_csv(input_path, output_path):
    try:
        df = pd.read_excel(input_path,engine='openpyxl')
        df.to_csv(output_path, index=False, encoding="utf-8")
        return True
    except Exception as e:
        print(f"XLSX to CSV conversion error: {e}")
        return False

def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("0.0.0.0", 12345))
    server_socket.listen(5)
    print("Server is listening on port 12345")
    
    while True:
        client_socket, client_address = server_socket.accept()
        print(f"Connection from {client_address}")
        try:
            metadata = client_socket.recv(1024).decode()
            file_name, target_format, file_size = metadata.split("|")
            file_size = int(file_size)
            file_path = f"received_{file_name}"
            output_path = f"converted_{file_name.split('.')[0]}.{target_format.lower()}"

            with open(file_path, "wb") as file:
                while file_size > 0:
                    data = client_socket.recv(4096)
                    if not data:
                        break
                    file.write(data)
                    file_size -= len(data)

            success = False
            if file_name.endswith(('.jpg', '.jpeg', '.png')):
                success = convert_image(file_path, output_path, target_format)
            elif file_name.endswith('.docx') and target_format == "PDF":
                success = convert_docx_to_pdf(file_path, output_path)
            elif file_name.endswith('.pdf') and target_format == "DOCX":
                success = convert_pdf_to_docx(file_path, output_path)
            elif file_name.endswith('.csv') and target_format == "XLSX":
                success = convert_csv_to_xlsx(file_path, output_path)
            elif file_name.endswith('.xlsx') and target_format == "CSV":
                success = convert_xlsx_to_csv(file_path, output_path)

            if success:
                converted_file_size = os.path.getsize(output_path)
                client_socket.sendall(str(converted_file_size).encode("utf-8"))
                with open(output_path, "rb") as file:
                    while chunk := file.read(4096):
                        client_socket.sendall(chunk)
            else:
                client_socket.sendall(b"Conversion failed")
        except Exception as e:
            print(f"Error: {e}")
        finally:
            client_socket.close()

if __name__ == "__main__":
    start_server()
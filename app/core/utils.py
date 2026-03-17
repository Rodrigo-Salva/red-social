import os
import uuid
from fastapi import UploadFile

def save_upload_file(upload_file: UploadFile, folder: str) -> str:
    # Asegurar que el nombre del archivo sea único
    file_ext = os.path.splitext(upload_file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_ext}"
    file_path = os.path.join(folder, unique_filename)
    
    with open(file_path, "wb") as buffer:
        buffer.write(upload_file.file.read())
        
    return f"/{file_path}"

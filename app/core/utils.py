import os
import uuid
from fastapi import UploadFile

from PIL import Image
from io import BytesIO

def save_upload_file(upload_file: UploadFile, folder: str) -> dict:
    # Asegurar que el nombre del archivo sea único y usar .webp
    base_id = str(uuid.uuid4())
    filename = f"{base_id}.webp"
    thumb_filename = f"{base_id}_thumb.webp"
    
    file_path = os.path.join(folder, filename)
    thumb_path = os.path.join(folder, thumb_filename)
    
    # Crear carpeta si no existe
    if not os.path.exists(folder):
        os.makedirs(folder)

    # Leer archivo
    content = upload_file.file.read()
    image = Image.open(BytesIO(content))
    
    # Convertir a RGB si es necesario (para WebP)
    if image.mode in ("RGBA", "P"):
        image = image.convert("RGB")
    
    # Imagen principal: Redimensionar si es muy grande (ej. max 1200px ancho)
    max_width = 1200
    if image.width > max_width:
        ratio = max_width / float(image.width)
        new_height = int(float(image.height) * ratio)
        image = image.resize((max_width, new_height), Image.Resampling.LANCZOS)
    
    # Guardar imagen principal
    image.save(file_path, "WEBP", quality=80)
    
    # Generar y guardar miniatura (ej. 300x300)
    image.thumbnail((300, 300), Image.Resampling.LANCZOS)
    image.save(thumb_path, "WEBP", quality=70)
        
    return {
        "image_url": f"/{file_path}",
        "thumbnail_url": f"/{thumb_path}"
    }

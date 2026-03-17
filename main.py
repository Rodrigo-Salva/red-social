from app.main import app

# Este archivo en la raíz actúa como punto de entrada para facilitar el uso de comandos simples
# como 'fastapi dev main.py' o 'uvicorn main:app --reload'

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
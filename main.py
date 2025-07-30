# main.py

from utils.hotkey import iniciar_hotkey
from dotenv import load_dotenv
import os

def main():
    # 🔐 Cargar API key desde .env
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("Falta tu OPENAI_API_KEY en el archivo .env")

    # 🎯 Iniciar hotkey global
    print("⌨️ Esperando que presiones Ctrl + Shift + V...")
    iniciar_hotkey(api_key)

if __name__ == "__main__":
    main()

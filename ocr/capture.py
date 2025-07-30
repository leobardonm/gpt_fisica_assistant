# ocr/capture.py

from PIL import Image, ImageGrab
import pytesseract
import platform
import tempfile
import os

def capturar_y_extraer_texto():
    print("📷 Esperando selección de pantalla...")

    sistema = platform.system()

    if sistema == "Darwin":
        try:
            import subprocess
            temp_path = tempfile.NamedTemporaryFile(suffix=".png", delete=False).name
            subprocess.run(["screencapture", "-i", temp_path])

            if not os.path.exists(temp_path) or os.path.getsize(temp_path) == 0:
                print("[❌] Captura cancelada o vacía.")
                return ""

            imagen = Image.open(temp_path)
        except Exception as e:
            print(f"[ERROR al abrir imagen]: {e}")
            return ""
    else:
        try:
            imagen = ImageGrab.grab()
        except Exception as e:
            print(f"[ERROR captura]: {e}")
            return ""

    try:
        texto = pytesseract.image_to_string(imagen, lang="spa+eng")
        print("🧠 Texto detectado:")
        print(texto.strip())
        return texto.strip()
    except Exception as e:
        print(f"[ERROR OCR]: {e}")
        return ""

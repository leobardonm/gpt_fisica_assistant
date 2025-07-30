# utils/hotkey.py

import keyboard
from audio.recorder import toggle_grabacion, grabar_y_transcribir
from gpt.client import consultar_gpt
from ui.overlay import mostrar_overlay
import pyperclip
import threading

# Estado de grabación
grabando = [False]  # Usamos lista mutable para permitir edición dentro de función

def manejar_toggle(api_key):
    if not grabando[0]:
        # Inicia grabación
        grabando[0] = True
        toggle_grabacion()
    else:
        # Detiene grabación y procesa
        grabando[0] = False
        toggle_grabacion()

        def flujo():
            print("🧠 Procesando...")
            texto = grabar_y_transcribir()
            if not texto:
                print("❌ No se entendió el audio.")
                return

            print(f"📝 Texto reconocido: {texto}")
            respuesta = consultar_gpt(api_key, texto)
            pyperclip.copy(respuesta)
            print("📋 Respuesta copiada al portapapeles.")
            mostrar_overlay(respuesta)

        # Ejecutar procesamiento en hilo aparte para no bloquear
        threading.Thread(target=flujo).start()

def iniciar_hotkey(api_key):
    keyboard.add_hotkey("ctrl+shift+v", lambda: manejar_toggle(api_key))
    keyboard.wait()  # Mantiene vivo el script

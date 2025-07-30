# audio/recorder.py

import sounddevice as sd
import numpy as np
import speech_recognition as sr
from scipy.io.wavfile import write
import tempfile

grabando = False
audio_buffer = []

def callback(indata, frames, time, status):
    if grabando:
        audio_buffer.append(indata.copy())

def grabar_y_transcribir():
    global grabando, audio_buffer

    print("🎙️ Presiona Ctrl+Shift+V para iniciar y detener grabación...")

    # Configurar stream de entrada
    samplerate = 16000
    channels = 1

    audio_buffer = []
    grabando = True

    with sd.InputStream(callback=callback, channels=channels, samplerate=samplerate):
        while grabando:
            sd.sleep(100)  # Mantiene el ciclo de grabación activo

    print("🛑 Grabación finalizada.")
    audio_np = np.concatenate(audio_buffer, axis=0)

    # Guardar audio temporalmente
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_wav:
        write(temp_wav.name, samplerate, audio_np)
        temp_path = temp_wav.name

    # Transcripción
    recognizer = sr.Recognizer()
    with sr.AudioFile(temp_path) as source:
        audio_data = recognizer.record(source)

    try:
        texto = recognizer.recognize_google(audio_data, language="es-MX")
        return texto
    except sr.UnknownValueError:
        return ""
    except sr.RequestError as e:
        return f"[ERROR de transcripción]: {e}"

# Función expuesta para detener la grabación (usada desde hotkey)
def toggle_grabacion():
    global grabando
    grabando = not grabando
    if grabando:
        print("🎙️ Grabando...")
    else:
        print("🛑 Deteniendo...")

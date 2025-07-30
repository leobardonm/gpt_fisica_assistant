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

    print("🎙️ Presiona nuevamente para detener grabación...")

    samplerate = 16000
    channels = 1

    audio_buffer = []
    grabando = True

    with sd.InputStream(callback=callback, channels=channels, samplerate=samplerate, dtype='int16'):
        while grabando:
            sd.sleep(100)

    print("🛑 Grabación finalizada.")
    audio_np = np.concatenate(audio_buffer, axis=0)

    # Guardar temporalmente como PCM WAV (int16)
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_wav:
        write(temp_wav.name, samplerate, audio_np.astype(np.int16))
        temp_path = temp_wav.name

    recognizer = sr.Recognizer()
    try:
        with sr.AudioFile(temp_path) as source:
            audio_data = recognizer.record(source)
        texto = recognizer.recognize_google(audio_data, language="es-MX")
        return texto
    except sr.UnknownValueError:
        return ""
    except sr.RequestError as e:
        return f"[ERROR de transcripción]: {e}"

def toggle_grabacion():
    global grabando
    grabando = not grabando
    if grabando:
        print("🎙️ Grabando...")
    else:
        print("🛑 Deteniendo...")

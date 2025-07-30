# audio/recorder.py

import sounddevice as sd
import soundfile as sf
import numpy as np
import queue
import tempfile
import os
import whisper

# Variables globales para el stream y la cola de audio
q = queue.Queue()
stream = None
archivo_temporal = None

# Empieza a grabar de inmediato
def toggle_grabacion():
    global stream, archivo_temporal
    if stream is None:
        q.queue.clear()  # limpia cualquier audio previo

        archivo_temporal = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
        samplerate = 16000
        channels = 1

        def callback(indata, frames, time, status):
            if status:
                print(f"[⚠️ Grabación] Estado: {status}")
            q.put(indata.copy())

        stream = sd.InputStream(
            samplerate=samplerate,
            channels=channels,
            dtype='int16',
            callback=callback
        )
        stream.start()
        print("🎙️ Grabación iniciada.")
    else:
        detener_y_guardar_audio()

# Detiene y guarda el archivo de audio en formato correcto
def detener_y_guardar_audio():
    global stream, archivo_temporal

    if stream:
        stream.stop()
        stream.close()
        stream = None
        print("🛑 Grabación detenida.")

        audio_total = []
        while not q.empty():
            audio_total.append(q.get())

        if audio_total:
            audio_np = np.concatenate(audio_total, axis=0)
            sf.write(archivo_temporal.name, audio_np, 16000, subtype='PCM_16')
            print(f"✅ Guardado en: {archivo_temporal.name}")
        else:
            print("⚠️ No se grabó audio.")
            archivo_temporal = None

# Transcribe usando Whisper y devuelve el texto
def grabar_y_transcribir():
    global archivo_temporal

    if not archivo_temporal or not os.path.exists(archivo_temporal.name):
        print("❌ No hay archivo para transcribir.")
        return ""

    try:
        modelo = whisper.load_model("base")  # Puedes usar tiny/base/small
        resultado = modelo.transcribe(archivo_temporal.name)
        print(f"📝 Transcripción: {resultado['text']}")
        return resultado["text"]
    except Exception as e:
        print(f"⚠️ Error al transcribir: {e}")
        return "⚠️ Error al transcribir el audio."
    finally:
        os.unlink(archivo_temporal.name)
        archivo_temporal = None

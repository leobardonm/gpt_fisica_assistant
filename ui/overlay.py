# ui/overlay.py

from PyQt5 import QtWidgets, QtCore
from gpt.client import consultar_gpt
from audio.recorder import toggle_grabacion, grabar_y_transcribir
from ocr.capture import capturar_y_extraer_texto
import pyperclip, threading, os
from dotenv import load_dotenv

import sys
if sys.platform == "darwin":
    from Cocoa import NSApp, NSWindowSharingNone
elif sys.platform == "win32":
    import ctypes

class VentanaOverlay(QtWidgets.QWidget):
    def __init__(self, texto):
        super().__init__()
        self.setWindowFlags(QtCore.Qt.Tool | QtCore.Qt.WindowStaysOnTopHint)
        self.setGeometry(400, 100, 600, 350)
        self.init_ui(texto)
        self.proteger_de_screen_share()

    def init_ui(self, texto):
        layout = QtWidgets.QVBoxLayout()
        scroll = QtWidgets.QScrollArea(); scroll.setWidgetResizable(True)
        scroll.setStyleSheet("background-color: rgba(20,20,20,220); border-radius: 12px;")
        content = QtWidgets.QWidget(); v = QtWidgets.QVBoxLayout()
        label = QtWidgets.QLabel(texto); label.setWordWrap(True)
        label.setStyleSheet("color: white; font-size:16px; padding:16px;")
        v.addWidget(label); content.setLayout(v); scroll.setWidget(content)
        layout.addWidget(scroll); self.setLayout(layout)

    def proteger_de_screen_share(self):
        if sys.platform == "darwin":
            try:
                for win in NSApp.windows():
                    win.setSharingType_(NSWindowSharingNone)
            except Exception:
                pass
        elif sys.platform == "win32":
            user32 = ctypes.windll.user32
            user32.SetWindowDisplayAffinity(int(self.winId()), 0x00000011)


class VentanaControl(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(
            QtCore.Qt.FramelessWindowHint |
            QtCore.Qt.WindowStaysOnTopHint |
            QtCore.Qt.Tool
        )
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.setStyleSheet("background: rgba(20, 20, 20, 200); border-radius: 20px;")
        self.resize(280, 200)
        self.move(50, 50)

        self.api_key = os.getenv("GEMINI_API_KEY")
        self.grabando = False
        self.overlay_ventana = None

        # Elementos UI
        self.btn_audio = QtWidgets.QPushButton("🎙️ Iniciar grabación")
        self.btn_audio.setStyleSheet("font-size: 14px; padding: 10px;")
        self.btn_audio.clicked.connect(self.toggle_grabar)

        self.btn_ocr = QtWidgets.QPushButton("📷 Capturar pantalla")
        self.btn_ocr.setStyleSheet("font-size: 14px; padding: 10px;")
        self.btn_ocr.clicked.connect(self.ocr_a_gpt)

        self.model_selector = QtWidgets.QComboBox()
        self.model_selector.addItems(["Gemini 1.5 Pro", "Gemini 1.5 Flash"])
        self.model_selector.setStyleSheet("padding: 6px; font-size: 13px;")

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.model_selector)
        layout.addWidget(self.btn_audio)
        layout.addWidget(self.btn_ocr)
        self.setLayout(layout)

        QtWidgets.QShortcut(QtCore.Qt.Key_Escape, self, self.close)
        self.show()

    def toggle_grabar(self):
        if not self.grabando:
            toggle_grabacion()
            self.btn_audio.setText("🛑 Detener y procesar")
            self.grabando = True
        else:
            toggle_grabacion()
            self.btn_audio.setText("🎙️ Iniciar grabación")
            self.grabando = False
            threading.Thread(target=self.procesar_audio).start()

    def procesar_audio(self):
        texto = grabar_y_transcribir()
        if not texto:
            self.btn_audio.setText("❌ No se entendió. Intenta de nuevo.")
            return
        modelo = self.model_selector.currentText()
        respuesta = consultar_gpt(self.api_key, texto, modelo)
        pyperclip.copy(respuesta)
        self.btn_audio.setText("✅ Copiado al portapapeles")
        QtCore.QMetaObject.invokeMethod(self, "mostrar_respuesta", QtCore.Qt.QueuedConnection, QtCore.Q_ARG(str, respuesta))

    def ocr_a_gpt(self):
        self.btn_ocr.setText("🔄 Procesando OCR...")
        threading.Thread(target=self.procesar_ocr).start()

    def procesar_ocr(self):
        texto = capturar_y_extraer_texto()
        if not texto:
            self.btn_ocr.setText("❌ Nada reconocido.")
            return
        modelo = self.model_selector.currentText()
        respuesta = consultar_gpt(self.api_key, texto, modelo)
        pyperclip.copy(respuesta)
        self.btn_ocr.setText("✅ Copiado al portapapeles")
        QtCore.QMetaObject.invokeMethod(self, "mostrar_respuesta", QtCore.Qt.QueuedConnection, QtCore.Q_ARG(str, respuesta))

    @QtCore.pyqtSlot(str)
    def mostrar_respuesta(self, texto):
        if self.overlay_ventana:
            self.overlay_ventana.close()
        self.overlay_ventana = VentanaOverlay(texto)
        self.overlay_ventana.show()

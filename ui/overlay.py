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
        self.setWindowFlags(
            QtCore.Qt.FramelessWindowHint |
            QtCore.Qt.WindowStaysOnTopHint |
            QtCore.Qt.Tool
        )
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.setStyleSheet("background: rgba(20, 20, 20, 200); border-radius: 20px;")
        self.init_ui(texto)

    def init_ui(self, texto):
        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(6)

        # Botón de cerrar
        cerrar_btn = QtWidgets.QPushButton("❌")
        cerrar_btn.setFixedSize(30, 30)
        cerrar_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 30);
                color: white;
                font-size: 16px;
                border: none;
                border-radius: 15px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 50);
            }
        """)
        cerrar_btn.clicked.connect(self.close)

        top_bar = QtWidgets.QHBoxLayout()
        top_bar.addStretch()
        top_bar.addWidget(cerrar_btn)

        # Label de texto sin scroll
        label = QtWidgets.QLabel(texto)
        label.setWordWrap(True)
        label.setStyleSheet("color: white; font-size: 16px; padding: 8px;")
        
        # Configurar tamaño máximo para la ventana
        label.setMaximumWidth(600)
        
        layout.addLayout(top_bar)
        layout.addWidget(label)
        self.setLayout(layout)
        
        # Ajustar tamaño de la ventana al contenido
        self.adjustSize()
        
        # Limitar tamaño máximo y posicionar
        max_width = 650
        max_height = 500
        if self.width() > max_width:
            self.resize(max_width, min(self.height(), max_height))
        if self.height() > max_height:
            self.resize(self.width(), max_height)
            
        # Posicionar en el centro-derecha de la pantalla
        self.move(400, 100)

    def proteger_de_screen_share(self):
        if sys.platform == "darwin":
            try:
                # Asegurar que el winId esté disponible
                self.winId()
                # Aplicar inmediatamente a todas las ventanas
                for win in NSApp.windows():
                    win.setSharingType_(NSWindowSharingNone)
                # Aplicar protección adicional múltiples veces para asegurar
                QtCore.QTimer.singleShot(10, self._aplicar_proteccion_adicional)
                QtCore.QTimer.singleShot(25, self._aplicar_proteccion_adicional)
                QtCore.QTimer.singleShot(50, self._aplicar_proteccion_adicional)
            except Exception as e:
                print(f"Error en protección macOS VentanaOverlay: {e}")
                pass
        elif sys.platform == "win32":
            try:
                user32 = ctypes.windll.user32
                user32.SetWindowDisplayAffinity(int(self.winId()), 0x00000011)
                # Aplicar protección adicional
                QtCore.QTimer.singleShot(10, lambda: user32.SetWindowDisplayAffinity(int(self.winId()), 0x00000011))
            except Exception as e:
                print(f"Error en protección Windows VentanaOverlay: {e}")
                pass

    def _aplicar_proteccion_adicional(self):
        """Aplicar protección adicional específica a esta ventana"""
        if sys.platform == "darwin":
            try:
                for win in NSApp.windows():
                    win.setSharingType_(NSWindowSharingNone)
            except Exception:
                pass


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
        # Conectar señales para proteger dropdown cuando se abra
        self.model_selector.showPopup = self._show_popup_protegido

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.model_selector)
        layout.addWidget(self.btn_audio)
        layout.addWidget(self.btn_ocr)
        self.setLayout(layout)

        QtWidgets.QShortcut(QtCore.Qt.Key_Escape, self, self.close)
        self.proteger_de_screen_share()
        self.show()

    def proteger_de_screen_share(self):
        if sys.platform == "darwin":
            try:
                # Asegurar que el winId esté disponible
                self.winId()
                # Aplicar a todas las ventanas de la aplicación
                for win in NSApp.windows():
                    win.setSharingType_(NSWindowSharingNone)
            except Exception as e:
                print(f"Error en protección macOS VentanaControl: {e}")
                pass
        elif sys.platform == "win32":
            try:
                user32 = ctypes.windll.user32
                user32.SetWindowDisplayAffinity(int(self.winId()), 0x00000011)
            except Exception as e:
                print(f"Error en protección Windows VentanaControl: {e}")
                pass

    def _show_popup_protegido(self):
        """Mostrar popup del combobox y protegerlo"""
        # Aplicar protección ANTES de mostrar el popup
        self._proteger_popup()
        # Pequeño delay para asegurar que la protección se aplique, luego mostrar popup
        QtCore.QTimer.singleShot(30, lambda: QtWidgets.QComboBox.showPopup(self.model_selector))
        # Reforzar protección después de mostrar
        QtCore.QTimer.singleShot(50, self._proteger_popup)

    def _proteger_popup(self):
        """Proteger el popup del dropdown"""
        if sys.platform == "darwin":
            try:
                # Aplicar inmediatamente a todas las ventanas
                for win in NSApp.windows():
                    win.setSharingType_(NSWindowSharingNone)
                # Aplicar protección adicional múltiples veces
                QtCore.QTimer.singleShot(10, self._proteger_popup_adicional)
                QtCore.QTimer.singleShot(25, self._proteger_popup_adicional)
                QtCore.QTimer.singleShot(40, self._proteger_popup_adicional)
            except Exception as e:
                print(f"Error protegiendo popup: {e}")
        elif sys.platform == "win32":
            try:
                # En Windows, aplicar protección a la ventana principal
                user32 = ctypes.windll.user32
                user32.SetWindowDisplayAffinity(int(self.winId()), 0x00000011)
                # También intentar proteger ventanas hijas múltiples veces
                QtCore.QTimer.singleShot(10, self._proteger_popup_adicional)
                QtCore.QTimer.singleShot(25, self._proteger_popup_adicional)
                QtCore.QTimer.singleShot(40, self._proteger_popup_adicional)
            except Exception as e:
                print(f"Error protegiendo popup Windows: {e}")

    def _proteger_popup_adicional(self):
        """Protección adicional para popup"""
        if sys.platform == "darwin":
            try:
                for win in NSApp.windows():
                    win.setSharingType_(NSWindowSharingNone)
            except Exception:
                pass
        elif sys.platform == "win32":
            try:
                user32 = ctypes.windll.user32
                user32.SetWindowDisplayAffinity(int(self.winId()), 0x00000011)
            except Exception:
                pass

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
        # Aplicar protección ANTES de mostrar la ventana
        self.overlay_ventana.proteger_de_screen_share()
        # Pequeño delay para asegurar que la protección se aplique
        QtCore.QTimer.singleShot(50, self.overlay_ventana.show)

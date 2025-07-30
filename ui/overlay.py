# ui/overlay.py

from PyQt5 import QtWidgets, QtCore
import sys

class VentanaOverlay(QtWidgets.QWidget):
    def __init__(self, texto):
        super().__init__()
        self.setWindowFlags(
            QtCore.Qt.FramelessWindowHint |
            QtCore.Qt.WindowStaysOnTopHint |
            QtCore.Qt.Tool
        )
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.setStyleSheet("background: rgba(0, 0, 0, 180); border-radius: 20px;")
        self.resize(600, 250)
        self.move(80, 80)

        label = QtWidgets.QLabel(texto, self)
        label.setWordWrap(True)
        label.setStyleSheet("color: white; font-size: 17px; padding: 25px;")

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(label)
        self.setLayout(layout)

        # Cierra al presionar Esc
        QtWidgets.QShortcut(QtCore.Qt.Key_Escape, self, self.close)

        self.show()

def mostrar_overlay(texto):
    app = QtWidgets.QApplication.instance()
    if app is None:
        app = QtWidgets.QApplication(sys.argv)

    overlay = VentanaOverlay(texto)
    app.exec_()

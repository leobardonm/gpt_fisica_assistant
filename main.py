from PyQt5 import QtWidgets
from ui.overlay import VentanaControl

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    ventana = VentanaControl()
    sys.exit(app.exec_())

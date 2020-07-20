import sys
from PyQt5 import QtWidgets
from src.window.main.main import MainWindow


if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    main = MainWindow()
    sys.exit(app.exec_())


from model import *
import sys
from PyQt5 import QtWidgets
from controller import Controller

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    ctrl = Controller()
    ctrl.show()
    sys.exit(app.exec_())

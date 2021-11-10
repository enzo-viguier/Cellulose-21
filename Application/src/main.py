from model import *
import sys
from PyQt5 import QtWidgets
from controller import control



if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    ctrl = control()
    ctrl.show()
    sys.exit(app.exec_())
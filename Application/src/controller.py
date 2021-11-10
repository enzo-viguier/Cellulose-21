from modele import Modele
import simulation
from PyQt5.QtWidgets import QMainWindow


# # essais avec les tuto :

# def start():
#     simulation.startView()

#    # if :
#         #return simulation.endView()

# if __name__ == "__init__":
#     #running controller function
#     start()

# #ce que joannides a fait :
# class control(QMainWindow):
#     def __init__(self, parent=None):
#         super().__init__(parent)
#         self.ui = Ui_Cellulose()
#         self.ui.setupUi(self)
# #      self.ui.updateButton.clicked.connect(self.update_view)
#         self.m = Modele(self.ui.mplView)
# #        self.m.stateChangedSignal.connect(self.update_view)

        
        
#     def update_view(self):
#         self.ui.mplView.data_ref.set_data(self.m.getData())
#         self.ui.mplView.draw()
#         pass

class control(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_Simulation()
        self.ui.setupUi(self)
#      self.ui.updateButton.clicked.connect(self.update_view)
        self.m = Modele(self.ui.mplView)
#        self.m.stateChangedSignal.connect(self.update_view)

        
        
    def update_view(self):
        self.ui.mplView.data_ref.set_data(self.m.getData())
        self.ui.mplView.draw()
        pass
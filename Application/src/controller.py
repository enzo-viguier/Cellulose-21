import numpy as np
from matplotlib import pyplot as plt

from model import Model
import Ui_Simulation
from PyQt5.QtWidgets import QMainWindow


class control(QMainWindow):
    def __init__(self, parent=None):
        # on initialise la main window
        super().__init__(parent)
        self.ui = Ui_Simulation.Ui_MainWindow()
        self.ui.setupUi(self)
        # on attribue un modele au controller
        self.m = Model()
        # on receptionne les signaux, stateChangedSignal va update la view tout seul
        self.m.stateChangedSignal.connect(self.update_view)
        # les boutons enverront des signaux qui feront chacun une action differente
        self.ui.start.clicked.connect(self.do_start)
        self.ui.stop.clicked.connect(self.do_stop)
        self.ui.entree.clicked.connect(self.do_entree)
        # on lance la simulation par défaut quand on ouvre la fenetre (a changé à la fin)
        self.m.start()

    def do_start(self):
        print("je me dépause")
        # remet la valeur de isRunning a true pour relancer la boucle
        self.m.isRunning = True
        pass

    def do_stop(self):
        print("je me stoppe !")
        # met la valeur de isRunning a false pour stoper la boucle
        self.m.isRunning = False
        pass

    def do_entree(self):
        print("entree des données")
        # donner les valeurs aux parametres + relancer la simu
        pass

    def update_view(self):
        # on attribue a chaque widget ce qu'il doit afficher, animationSubstrat affichera le substrat et les bacteries
        self.ui.animationSubstrat.update_plot((self.m.get_all_coords()))
        self.ui.animationSubstrat.data_ref.set_data(self.m.concentrations)
        self.ui.animationSubstrat.draw()
        # graph1 et 2 afficheront des graphiques différents en fonction de la concentration et de la population de
        # bacteries
        self.ui.graph_1.data_ref.set_data(self.m.concentrations)
        self.ui.graph_1.draw()
        self.ui.graph_2.data_ref.set_data(self.m.concentrations)
        self.ui.graph_2.draw()

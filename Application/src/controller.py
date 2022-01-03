import numpy as np
from matplotlib import pyplot as plt

from model import Model
import Ui_Simulation
from PyQt5.QtWidgets import QMainWindow


class Controller(QMainWindow):
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
        self.m.d_tore["longueur"] = self.ui.nbCasesVal
        self.m.d_tore["nb_cellules_large"] = self.ui.largeurVal
        self.m.d_cellulose["rayon_cell"] = self.ui.rayonVal
        self.m.d_cellulose["c_ini"] = self.ui.cIni
        self.m.d_cellulose["c_min"] = self.ui.cDiffVal
        self.m.d_cellulose["v_diff"] = self.ui.vDiffVal
        self.m.d_tore["temps_simu"] = self.ui.tempsVal
        self.m.d_tore["delta"] = self.ui.ptDeltaVal
        self.m.d_tore["Delta"] = self.ui.gdDeltaVal
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

    # CI-DESSOUS LES FONCTIONS DES GRAPHIQUES A MODIFIER POUR LES AFFICHER SUR L'INTERFACE

    def update_graph1(self):
        # Données
        x = np.array([0, 1]) # Donnée en abscisse
        y = np.array([]) # Donnée en ordonnée

        plt.plot(x, y) # Tracé de la courbe
        plt.title("Titre graphe 1") # Titre du graphique

        plt.xlabel("Nom abscisse")
        # plt.xlim() Si on veut ajouter une limite à l'axe des abscisses

        plt.ylabel("Nom ordonnée")
        # plt.ylim() Si on veut ajouter une limite à l'axe des ordonnées

        plt.grid() # Rajoute une grille -> optionnel
        plt.show() # Affichage

    def update_graph2(self):
        # Données
        x = np.array([0, 1])  # Donnée en abscisse
        y = np.array([])  # Donnée en ordonnée

        plt.plot(x, y)  # Tracé de la courbe
        plt.title("Titre graphe 2")  # Titre du graphique

        plt.xlabel("Nom abscisse")
        # plt.xlim() Si on veut ajouter une limite à l'axe des abscisses

        plt.ylabel("Nom ordonnée")
        # plt.ylim() Si on veut ajouter une limite à l'axe des ordonnées

        plt.grid()  # Rajoute une grille -> optionnel
        plt.show()  # Affichage
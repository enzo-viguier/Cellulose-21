import matplotlib as mpl
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib import cm
from matplotlib.colors import Normalize
import numpy as np
from matplotlib import pyplot as plt

mpl.use('QT5Agg')


class Mplwidget(FigureCanvasQTAgg):

    def __init__(self, parent):
        # on attribue une figure a la classe
        self.fig = Figure()
        # on lui donne un axe
        self.ax = self.fig.add_subplot(111)


        # on lui set des parents (je pense que c'est a bouger au debut ça)
        super().__init__(self.fig)
        self.setParent(parent)
        self.ax_scatter = None  # nuage de point des bacteries
        self.ax_plot_substra = None  # Graph de la masse de substra

    def init_data_ref(self, extent):
        # on fait une jolie matrice qui se reshape en fonction du modele
        data = np.zeros(2500).reshape((50, 50))
        # on installe le imshow avec tous ses parametres
        self.data_ref = self.ax.imshow(data, origin='lower',
                                       norm=Normalize(0, 0.4),
                                       cmap=cm.coolwarm,
                                       interpolation='bicubic',
                                       extent=extent,
                                       aspect='auto')


    def update_plot(self, data):
        if self.ax_scatter is not None:
            self.ax_scatter.remove()

        # Le *5/2 sert à positionner bien les bactéries en prenant en compte la taille du canvas
        self.ax_scatter = self.ax.scatter(data[0] * 5 / 200, data[1] * 5 / 200, 20, "green", marker="*")
        # print(self.ax.__class__)
        # print("scat = ", self.ax_scatter)

    # CI-DESSOUS LES FONCTIONS DES GRAPHIQUES A MODIFIER POUR LES AFFICHER SUR L'INTERFACE

    def update_graph1(self, nb_tour_affich, masse_substra, delta):
        """Met à jour le graphique sur la masse totale de substrat

        Args:
            n (int): nombre de tour de boucle effectue
            nb_tour_affich (int): nombre de tour de boucle entre deux appel de update_view
            masse_substra (float[]): masse totale de substrat 
        """
        # Données
        x = np.linspace(0, len(masse_substra) - 1, len(masse_substra)) * nb_tour_affich * delta  # Donnée en abscisse
        y = masse_substra  # Donnée en ordonnée
        self.ax_plot_substra = self.ax.plot(x, y, color='b')  # Tracé de la courbe
        plt.xlim(0, 200)
        plt.ylim(0, 200)
        self.fig.supxlabel("Temps (en heure)")
        self.fig.supylabel("Masse totale de substrat (en pg)")
        self.fig.suptitle("Concentration du substrat")

    def update_graph2(self, nb_tour_affich, nbs_bact, delta):
        x = np.linspace(0, len(nbs_bact) - 1, len(nbs_bact)) * nb_tour_affich * delta  # Donnée en abscisse
        y = nbs_bact  # Donnée en ordonnée
        self.ax_plot_substra = self.ax.plot(x, y, color='b' )  # Tracé de la courbe
        self.fig.supxlabel("Temps (en heure)")
        self.fig.supylabel("Nombre de bactérie")
        self.fig.suptitle("Population de bactérie")

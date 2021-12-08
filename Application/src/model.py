import numpy as np
from PyQt5 import QtCore
from bacterie import *
import threading


# Consignes générales :
# Toutes les durrées sont en heure, les longueurs en µm
# -> dimension de l'enceinte carrée : 1/2 longueur L = 40 µm (soit longueur = 80) de côté (en micron µ) 
# -> nombre de cases : n =  250 dans chaque direction, donc 250² cases en tout
# -> concentration initiale : c_ini = 0.4 pg/µm² (picogrammes par micromètre carré)
# -> concentration pour diffuser : c_min = 0.3 pg/µm²
# -> vitesse de diffusion : 5 µm²/h (micromètres carrés par heure)
# -> pas de temps pour diffuser : delta = 0.005h

# -> rayon du cercle initial de cellulose : R = 25 µm
# -> Temps de simulation : 30h
# -> pas de temps pour l'algorithme : Delta = 0.3h

# - masse initiale bactérie : m_ini = 0.4 pg
# vitesse max des bactéries : 10 µm/h
# - vitesse de dérive des bactéries : vd = 0.1 (µm^4/(pg h)
# - écart-type sur la vitesse de déplacement : b_diff = 1 µm/sqrt(h)
# constante de conversion masse/biomass : k_conv = 0.2 (sans unité)
# vitesse de consommation : v_cons = 0.2 pg/h
# population initiale : 50


class Model(QtCore.QObject, threading.Thread):
    # Dictionnaire de constantes d'algo
    d_tore = {}
    # Dictionnaire de constantes relatives à la cellulose
    d_cellulose = {}
    # PYQT
    stateChangedSignal = QtCore.pyqtSignal()
    # Stockage des bacteries
    bacteries = list()
    #compte le nombre de steps effectues par l'algo
    nb_step = 0


    def __init__(self, c_ini=0.4, c_min=0.3, v_diff=0.02,
                 rayon_cell=25, delta=0.005, longueur=80, nb_cellules_large=250, Delta=0.3,
                 masse_ini=0.4, v_absorb=0.1, v_deplacement=0.1, nb_bact_ini=50, k_conv=0.2):
        """Initialise le model avec le tore, les concentrations et les bactéries

        Args:
            view (MainWindow, optional): Contient la mainwindows pour l'interface. Si non remplis lance sans interface.
            c_ini (float, optional): Concentration initiale. Defaults to 0.4 .
            c_min (float, optional): Concentration minimale à partir de laquelle le substrat diffuse. Defaults to 5.
            v_diff (float, optional): Vitesse de diffusion du substrat. Defaults to 0.02.
            rayon_cell (int, optional): rayon du substrat (en nanometre). Defaults to 25.
            delta (float, optional): Pas de temps entre chaque boucle de la simulation (voir fonction step pour une boucle). Defaults to 0.005.
            longueur (int, optional): Longueur et largeur du tore. Defaults to 40.
            nb_cellules_large (int, optional): Nombre de cases en largeur et en longueur. Defaults to 250.
            Delta (float, optional) : Pas de temps utilisé pour les sorties de l'algorithme 
            masse_ini (float, optional): Masse initiale des bactéries
            v_absorb (float, optional): Vitesse d'absorption des bactéries
            v_deplacement (float, optional): Vitesse de déplacement des bactéries
        Raises:
            Exception: Si delta trop grand, la simulation ne peut pas fonctionner
        """
        threading.Thread.__init__(self)
        super(QtCore.QObject, self).__init__()
        # vérifie que les données sont cohérentes
        if (delta > longueur ** 2 / (4 * v_diff)):
            raise Exception("Erreur dans le pas de temps (delta est trop grand)")  # Lève une erreur

        # Initialisation des dictionnaires
        self.init_d_cellulose(c_ini, c_min, v_diff, rayon_cell)
        self.init_d_tore(delta, longueur, nb_cellules_large)
        self.init_d_biomasse(masse_ini, v_absorb, v_deplacement, k_conv)

        # Création des concentrations
        self.creer_concentrations()

        # Creation des bacteries
        self.__creer_bacterie(nb_bact_ini)

 





    # ---------------- Initialisation des différentes couches : le Tore, les concentrations et les bactéries---------

    def init_d_cellulose(self, c_ini, c_min, v_diff, rayon_cell):
        """Initialise le dictionnaire de cellulose. Voir __init__ pour les attributs
        """
        self.d_cellulose["c_ini"] = c_ini
        self.d_cellulose["c_min"] = c_min
        self.d_cellulose["v_diff"] = v_diff
        self.d_cellulose["rayon_cell"] = rayon_cell

    def init_d_tore(self, delta, longueur, nb_cellules_large):
        """ Initialise le dictionnaire du tore. Voir __init__ pour les attributs
        """
        self.d_tore["longueur"] = longueur
        self.d_tore["nb_cellules_large"] = nb_cellules_large
        self.d_tore["largeur_case"] = longueur / nb_cellules_large
        self.d_tore["delta"] = delta

    def init_d_biomasse(self, masse_ini, v_absorb, v_deplacement, k_conv):
        self.d_biomasse = {}
        self.d_biomasse["masse_ini"] = masse_ini
        self.d_biomasse["v_absorb"] = v_absorb
        self.d_biomasse["vd"] = v_deplacement
        self.d_biomasse["b_diff"] = 1 / np.sqrt(self.d_tore["largeur_case"])
        self.d_biomasse["k_conv"] = k_conv

    def creer_concentrations(self):
        """Creer la matrice de concentration et appelle la création du substrat
        """
        self.concentrations = np.zeros((self.d_tore["nb_cellules_large"], self.d_tore["nb_cellules_large"]),
                                       dtype=np.float64)
        self.__creer_substrat()

    def __creer_substrat(self):
        """Creer le substrat, c'est à dire une zone centrale où les concentrations sont à c_ini
        """

        # Met la concentration des cases centrales à c_ini
        nb_cel_large = self.d_tore["nb_cellules_large"]
        rayon_cases_subst = self.d_cellulose["rayon_cell"] / (self.d_tore["longueur"] / nb_cel_large)

        X, Y = np.meshgrid(np.linspace(-nb_cel_large / 2, nb_cel_large / 2, nb_cel_large),
                           np.linspace(nb_cel_large / 2, -nb_cel_large / 2, nb_cel_large),
                           indexing='xy')

        cellulose = ((X * X + Y * Y) <= (rayon_cases_subst * rayon_cases_subst))

        self.concentrations[cellulose] = self.d_cellulose["c_ini"]

    def __creer_bacterie(self, n):
        """
        :param n: le nombre de bactéries du modèle
        :return: void
        Place des bactéries de manière regulière à une case plus loin que le rayon du substrat (pour être en contact)
        """
        interval = 2 * np.pi / n

        for i in np.arange(1, n + 1):
            x = np.cos(i * interval) * self.d_cellulose["rayon_cell"] 
            y = np.sin(i * interval) * self.d_cellulose["rayon_cell"] 
            #print("type x, y : ", type(x), type(y))
            self.bacteries.append(Bacterie(self, x, y, self.d_biomasse["masse_ini"]))

    # ---------------- Gestion du multicouche et utilitaires ------------------------
    def convert_coord_xy_to_ij(self, coords):
        """Permet de convertir des coordonnées x, y en coordonnées i, j. x et y doivent être entre -largeurTore/2 et largeurTore/2

        Returns:
            (int, int): Coordonnées sur le tableau de concentration
        """
        x, y = coords

        j = ((x + self.d_tore['longueur'] / 2) / self.d_tore['largeur_case'])
        i = ((-y + self.d_tore['longueur'] / 2) / self.d_tore['largeur_case'])

        return (int(np.floor(i)), int(np.floor(j)))
        # floor() fait un arrondi à l'inférieur, on convertit ensuite la valeur en entier.

    # --------------- Gestion des concentrations-------------------------------------------

    def get_concentrations(self):
        return self.concentrations

    def get_concentration_by_coord_xy(self, coord):
        i, j = self.convert_coord_xy_to_ij(coord)
        return self.get_concentration_by_coord_ij((i, j))

    def get_concentration_by_coord_ij(self, coords):
        return self.concentrations[self.coord_in_tore_ij((coords[0], coords[1]))]

    def set_concentration_by_coord_ij(self, coords, c):
        self.concentrations[self.coord_in_tore_ij((coords[0], coords[1]))] = c


    def coord_in_tore_ij(self, coords):
        #change les coordonnes facon tore si elles depassent du tableau
        coord_i=0
        coord_j=0
        if(coords[0]==self.d_tore["longueur"]):
            coord_i = 0
        else:
            coord_i = coords[0]

        if(coords[0]<0):
            coord_i = self.d_tore["longueur"]-(1-coords[0])
        else:
            coord_i = coords[0]

        if(coords[1]==self.d_tore["longueur"]):
            coord_j = 0
        else:
            coord_j = coords[0]

        if(coords[1]<0):
            coord_j = self.d_tore["longueur"]-(1-coords[1])
        else:
            coord_j = coords[0]

        return (coord_i, coord_j)

    # ------------- Boucle du programme ---------------

    def __calcul_nb_tours(self):
        #Le temps total est de 30h chaque tour de boucle prend delta heures
        return 30/self.d_tore["delta"]

    def run(self):
        self.run_simu()

    def run_simu(self):
        self.creer_concentrations()

        while(self.nb_step<self.__calcul_nb_tours()):
            self.step()
            self.nb_step+=100
            print(self.nb_step)
            self.update_view()
        

    def step(self):
        """
        :return: void
        La fonction step lance les cinq étapes de la boucle
        """
        self.__diffuse()
        self.__mouvement_bacteries()
        self.__bacteries_se_nourrisent()
        self.__division_bacteries()
        self.__produire_image()

    # Les __ servent à declarer en private
    def __diffuse(self):
        """
        :return: none
        Met à jour les concentrations du modèle pour un pas de temps de diffusion
        """
        
        # c_actu + v_diff δ h² (Somme pour les 4 cases adj(c_case_adj*etat_case - c_actu)
        # Avec h la taille d'une cellule, δ le pas de temps, etat_case=1 si case à l'état liquide ou semi
        # La fonction roll() permet de décaller la matrice le long d'un axe
        self.concentrations += (self.d_cellulose["v_diff"] * self.d_tore["delta"] *
                                self.d_tore["largeur_case"] ** 2 * self.__somme_case_adj())

        self.concentrations = self.concentrations/(100/99)

    def __somme_case_adj(self):
        """
        Renvoie la somme des diffusions avec les cases voisines sans les constantes, FONCTION AUXILIAIRE DE __diffuse.
        :return: la partie de la formule (Somme pour les 4 cases adj(c_actu − c_case_adj*etat_case)

        """
        # creation des concentrations décallés d'une ligne ou d'une colone
        c_haut = np.roll(self.concentrations, 1, axis=0)
        c_bas = np.roll(self.concentrations, -1, axis=0)
        c_droite = np.roll(self.concentrations, 1, axis=1)
        c_gauche = np.roll(self.concentrations, -1, axis=1)
        c_min = self.d_cellulose['c_min']  # sert juste à améliorer la lisibilité des calculs

        new_concentrations = np.zeros((self.d_tore["nb_cellules_large"], self.d_tore["nb_cellules_large"]),
                                       dtype=np.float64)#np.copy(self.concentrations)


        new_concentrations[self.concentrations <= c_min] = \
            c_haut[c_haut <= c_min] - self.concentrations[self.concentrations <= c_min]

        new_concentrations[self.concentrations <= c_min] += \
            c_bas[c_bas <= c_min] - self.concentrations[self.concentrations <= c_min]

        new_concentrations[self.concentrations <= c_min] += \
            c_droite[c_droite <= c_min] - self.concentrations[self.concentrations <= c_min]

        new_concentrations[self.concentrations <= c_min] += \
            c_gauche[c_gauche <= c_min] - self.concentrations[self.concentrations <= c_min]
        return new_concentrations

    def __mouvement_bacteries(self):
        """
        :return: void
        Effectue un pas de temps de mouvement de bactéries
        """
        for bact in self.bacteries:
            bact.se_deplacer()

    def __bacteries_se_nourrisent(self):
        """
        :return: void
        Effectue une dégradation de la cellulose et un gain de masse des bactéries pour les nourrir
        """
        for bact in self.bacteries:
            bact.manger()


    def __division_bacteries(self):
        """
        :return: void
        Divise chaque bacterie ayant une masse supérieure à sa masse maximale en deux bactéries placées au même point
        """
        for bact in self.bacteries:
            if(bact.peut_se_dupliquer()):
                coords = bact.get_coord_xy()
                value = np.float64(0)
                nouv_bact = Bacterie(self, np.float64(coords[0]), np.float64(coords[1]), np.float64(bact.masse_act/2))
                self.bacteries.append(Bacterie(self, 0, 0, self.d_biomasse["masse_ini"]))
                if(len(self.bacteries)<100):
                    print(len(self.bacteries))
                bact.masse_act/=2

    def __produire_image(self):
        """
        :return: void
        Produit une image de la situation actuelle
        """
        # TODO
        pass

    # -------------------------------- Affichages ----------------------------------

    def to_string(self):
        """
        Retourne un string contenant les différentes valeurs des constantes
        """
        return f"d_cellulose = :\n \
        cIni = {self.d_cellulose['c_ini']}\
        cMin = {self.d_cellulose['c_min']}\
        v_diff = {self.d_cellulose['v_diff']}\
        rayon_cell = {self.d_cellulose['rayon_cell']} \
        \nd_tore = \n\
        longueur =  {self.d_tore['longueur']}\
        nb_cellules_large = {self.d_tore['nb_cellules_large']}\
        largeur_case = {self.d_tore['largeur_case']}\
        delta = {self.d_tore['delta']}"

    def afficher_concentrations(self):
        print("afficher concentrations")
        print(self.concentrations)

    # PYQT
    def update_view(self):
        self.stateChangedSignal.emit()

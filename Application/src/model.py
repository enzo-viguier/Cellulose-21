import numpy as np
from PyQt5 import QtCore


# Consignes générales :
#Toutes les durrées sont en heure, les longueurs en µm
# -> dimension de l'enceinte carrée : 1/2 longueur L = 40 µm de côté (en micron µ)
# -> nombre de cases : n =  250 dans chaque direction, donc 250² cases en tout
# -> concentration initiale : c_ini = 0.4 pg/µm² (picogrammes par micromètre carré)
# -> concentration pour diffuser : c_min = 0.3 pg/µm²
# -> vitesse de diffusion : 5 µm²/h (micromètres carrés par heure)
# -> pas de temps pour diffuser : delta = 0.005h

# -> rayon du cercle initial de cellulose : R = 25 µm
# -> Temps de simulation : 30h
# -> pas de temps pour l'algorithme : Delta = 0.3h


class Model(QtCore.QObject):
    # Dictionnaire de constantes d'algo
    d_tore = {}
    # Dictionnaire de constantes relatives à la cellulose
    d_cellulose = {}
    # PYQT
    stateChangedSignal = QtCore.pyqtSignal()
    # Stockage des bacteries
    bacteries = []

    def __init__(self, view=None, c_ini=0.4 , c_min=5, v_diff=0.02, rayon_ini=25, delta=0.005, longueur=40, nb_cellules_large=250, Delta=0.3):
        """Initialise le model avec le tore, les concentrations et les bactéries

        Args:
            view (MainWindow, optional): Contient la mainwindows pour l'interface. Si non remplis lance sans interface.
            c_ini (float, optional): Concentration initiale. Defaults to 0.4 .
            c_min (float, optional): Concentration minimale à partir de laquelle le substrat diffuse. Defaults to 5.
            v_diff (float, optional): Vitesse de diffusion du substrat. Defaults to 0.02.
            rayon_ini (int, optional): rayon du substrat (en nanometre). Defaults to 25.
            delta (float, optional): Pas de temps entre chaque boucle de la simulation (voir fonction jour pour une boucle). Defaults to 0.005.
            longueur (int, optional): Longueur et largeur du tore. Defaults to 40.
            nb_cellules_large (int, optional): Nombre de cases en largeur et en longueur. Defaults to 250.
            Delta (float, optional) : Pas de temps utilisé pour les sorties de l'algorithme 

        Raises:
            Exception: Si delta trop grand, la simulation ne peut pas fonctionner
        """
        # vérifie que les données sont cohérentes
        if (delta > longueur ** 2 / (4 * v_diff)):
            raise Exception("Erreur dans le pas de temps (delta est trop grand)")  # Lève une erreur

        #Initialisation des dictionnaires
        self.init_d_cellulose(c_ini, c_min, v_diff, rayon_ini)
        self.init_d_tore(delta, longueur, nb_cellules_large)
        
        # Création des concentrations
        self.creer_concentrations()
        

        super(QtCore.QObject, self).__init__()
        if(view != None): # Constructeur avec interface
            self.view = view
            self.data = np.arange(2500).reshape((50, 50))
            self.timer = QtCore.QTimer()
            self.timer.setInterval(10)
            self.timer.timeout.connect(self.updateView)
            self.timer.start()

    #---------------- Initialisation des différentes couches : le Tore, les concentrations et les bactéries---------

    def init_d_cellulose(self, c_ini, c_min, v_diff, rayon_ini):
        """Initialise le dictionnaire de cellulose. Voir __init__ pour les attributs
        """
        self.d_cellulose["c_ini"] = c_ini
        self.d_cellulose["c_min"] = c_min
        self.d_cellulose["v_diff"] = v_diff
        self.d_cellulose["rayon_ini"] = rayon_ini

    def init_d_tore(self, delta, longueur, nb_cellules_large):
        """ Initialise le dictionnaire du tore. Voir __init__ pour les attributs
        """
        self.d_tore["longueur"] = longueur
        self.d_tore["nb_cellules_large"] = nb_cellules_large
        self.d_tore["largeur_case"] = longueur / nb_cellules_large
        self.d_tore["delta"] = delta


    def creer_concentrations(self):
        """Creer la matrice de concentration et appelle la création du substrat
        """
        self.concentrations = np.zeros((self.d_tore["nb_cellules_large"], self.d_tore["nb_cellules_large"]), dtype=np.float64)
        self.__creer_substrat()


    def __creer_substrat(self):
        """Creer le substrat, c'est à dire une zone centrale où les concentrations sont à c_ini
        """

        # Met la concentration des cases centrales à c_ini
        nb_cel_large = self.d_tore["nb_cellules_large"]
        rayon_cases_subst = self.d_cellulose["rayon_ini"]/(self.d_tore["longueur"]/nb_cel_large)

        X, Y = np.meshgrid(np.linspace(-nb_cel_large/2, nb_cel_large/2, nb_cel_large),
                           np.linspace(nb_cel_large/2, -nb_cel_large/2, nb_cel_large),
                           indexing='xy')

        cellulose = ((X * X + Y * Y) <= (rayon_cases_subst * rayon_cases_subst))

        self.concentrations[cellulose] = self.d_cellulose["c_ini"]


    def __creer_bacterie(self, n):
        """
        :param n: le nombre de bactéries du modèle
        :return: void
        Place des bactéries de manière regulière à une case plus loin que le rayon du substrat (pour être en contact)
        """
        # TODO
        pass

    #---------------- Gestion du multicouche et utilitaires ------------------------
    def convert_coord_xy_to_ij(self, coord):
        """Permet de convertir des coordonnées x, y en coordonnées i, j. x et y doivent être entre -largeurTore/2 et largeurTore/2

        Returns:
            (int, int): Coordonnées sur le tableau de concentration
        """
        x, y = coord

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
        return self.concentrations[coords[0], coords[1]]


    def set_concentration_by_ij(self, coords, c):
        self.concentrations[coords[0], coords[1]] = c


    # ------------- Boucle du programme ---------------

    def jour(self):
        """
        :return: void
        La fonction jour lance les cinq étapes de la boucle
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

        new_concentrations = np.copy(self.concentrations)

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
        # TODO

        pass

    def __bacteries_se_nourrisent(self):
        """
        :return: void
        Effectue une dégradation de la cellulose et un gain de masse des bactéries pour les nourrir
        """
        # TODO
        pass

    def __division_bacteries(self):
        """
        :return: void
        Divise chaque bacterie ayant une masse supérieure à sa masse maximale en deux bactéries placées au même point
        """
        # TODO
        pass

    def __produire_image(self):
        """
        :return: void
        Produit une image de la situation actuelle
        """
        # TODO
        pass



    #-------------------------------- Affichages ----------------------------------

    def to_string(self):
        """
        Retourne un string contenant les différentes valeurs des constantes
        """
        return f"d_cellulose = :\n \
        cIni = {self.d_cellulose['c_ini']}\
        cMin = {self.d_cellulose['c_min']}\
        v_diff = {self.d_cellulose['v_diff']}\
        rayon_ini = {self.d_cellulose['rayon_ini']} \
        \nd_tore = \n\
        longueur =  {self.d_tore['longueur']}\
        nb_cellules_large = {self.d_tore['nb_cellules_large']}\
        largeur_case = {self.d_tore['largeur_case']}\
        delta = {self.d_tore['delta']}"

    
    def afficher_concentrations(self):
        print("afficher concentrations")
        print(self.concentrations)


    # PYQT
    def getData(self):
        return self.data

    def updateView(self):
        self.data = np.roll(self.data, 1)
        self.view.data_ref.set_data(self.data)
        self.view.draw()
        # self.stateChangedSignal.emit()


import numpy as np
from PyQt5 import QtCore
from bacterie import *
import threading
from time import sleep
import json

# Consignes générales :
# Toutes les durées sont en heure, les longueurs en µm
# -> dimension de l'enceinte carrée : 1/2 longueur L = 40 µm (soit longueur = 80) de côté (en micron µ) 
# -> nombre de cases : n =  250 dans chaque direction, donc 250² cases en tout
# -> pas de temps pour l'algorithme : Delta = 0.3h
# -> pas de temps pour diffuser : delta = 0.005h

# -> concentration initiale : c_ini = 0.4 pg/µm² (picogrammes par micromètre carré)
# -> concentration pour diffuser : c_min = 0.3 pg/µm²
# -> vitesse de diffusion : 5 µm²/h (micromètres carrés par heure)
# -> rayon du cercle initial de cellulose : R = 25 µm
# Temps de simulation : 30h

# -> masse initiale bactérie : m_ini = 0.4 pg
# -> vitesse max des bactéries : 10 µm/h
# -> vitesse de dérive des bactéries : vd = 0.1 (µm^4/(pg h)
# -> écart-type sur la vitesse de déplacement : b_diff = 1 µm/sqrt(h)
# -> constante de conversion masse/biomass : k_conv = 0.2 (sans unité)
# vitesse de consommation : v_absorb = 0.2 pg/h
# -> population initiale : 50


class Model(QtCore.QObject, threading.Thread):
    # Dictionnaire de constantes d'algo
    d_tore = {}
    # Dictionnaire de constantes relatives à la cellulose
    d_cellulose = {}
    # Dictionnaire de constantes raltives aux bactéries
    d_biomasse = {}
    # PYQT
    stateChangedSignal = QtCore.pyqtSignal()
    # Stockage des bacteries
    bacteries = list()
    # Compte le nombre de cycles (step()) effectués par l'algo
    nb_step = 0
    # gestion de la boucle
    isRunning = True
    # nombre de tour entre chaque affichage
    nb_tour_affich = 0
    # Etat du thread
    thread_lance = False

    # ---------------- Initialisations et lancement ------------------------------------------

    def __init__(self, c_ini=0.4, c_min=0.3, v_diff=0.02, rayon_cell=25,
                 longueur=80, nb_cellules_large=250, temps_simu=30, delta=0.005, Delta=0.3,
                 masse_ini=0.4, v_absorb=0.2, v_deplacement=0.1, v_max=10, k_conv=0.2, nb_bact_ini=50):
        """
        Constructeur
        Objectif : Initialiser le model avec le tore, les concentrations et les bactéries
        :arg:
            view (MainWindow, optional): Contient la mainwindows pour l'interface. Si non remplis lance sans interface.
            c_ini (float, optional): Concentration initiale. Defaults to 0.4 .
            c_min (float, optional): Concentration minimale à partir de laquelle le substrat diffuse. Defaults to 5.
            v_diff (float, optional): Vitesse de diffusion du substrat. Defaults to 0.02.
            rayon_cell (int, optional): rayon du substrat (en nanometre). Defaults to 25.
            longueur (int, optional): Longueur et largeur du tore. Defaults to 40.
            nb_cellules_large (int, optional): Nombre de cases en largeur et en longueur. Defaults to 250.
            temps_simu (float, optional): Temps de simulation en heures. Defaults to 3.
            delta (float, optional): Pas de temps entre chaque boucle de la simulation (cf. méthode step()). Defaults to 0.005.
            Delta (float, optional) : Pas de temps utilisé pour les sorties de l'algorithme 
            masse_ini (float, optional): Masse initiale des bactéries. Defaults to 0.4.
            v_absorb (float, optional): Vitesse d'absorption des bactéries. Defaults to 0.2.
            v_deplacement (float, optional): Vitesse de déplacement des bactéries. Defaults to 0.1.
            v_max (float, optional): Vitesse maximale d'une bactérie. Defaults to 10.
        :raise:
            Exception: Si delta trop grand, la simulation ne peut pas fonctionner
        """
        threading.Thread.__init__(self)

        super(QtCore.QObject, self).__init__()

        print("lancement")
        # Met les valeurs par défaut aux constantes
        self.init_d_cellulose(c_ini, c_min, v_diff, rayon_cell)
        self.init_d_tore(delta, longueur, nb_cellules_large, Delta, temps_simu)
        self.init_d_biomasse(masse_ini, v_absorb, v_deplacement, v_max, k_conv, nb_bact_ini)

    # Initialisation des différentes couches : le Tore, les concentrations et les bactéries

    def init_d_cellulose(self, c_ini, c_min, v_diff, rayon_cell):
        """
        Objectif : Initialiser le dictionnaire de cellulose. Voir __init__() pour les attributs
        """
        self.d_cellulose["c_ini"] = c_ini
        self.d_cellulose["c_min"] = c_min
        self.d_cellulose["v_diff"] = v_diff
        self.d_cellulose["rayon_cell"] = rayon_cell

    def init_d_tore(self, delta, longueur, nb_cellules_large, Delta, temps_simu):
        """
        Objectif : Initialiser le dictionnaire du tore. Voir __init__() pour les attributs
        """
        self.d_tore["longueur"] = longueur
        self.d_tore["nb_cellules_large"] = nb_cellules_large
        self.d_tore["largeur_case"] = longueur / nb_cellules_large
        self.d_tore["temps_simu"] = temps_simu
        self.d_tore["delta"] = delta
        self.d_tore["Delta"] = Delta
        self.nb_tour_affich = self.d_tore["Delta"] / self.d_tore["delta"]

    def init_d_biomasse(self, masse_ini, v_absorb, v_deplacement, v_max, k_conv, nb_bact_ini):
        """
        Objectif : Initialiser le dictionnaire des bactéries. Voir __init__() pour les attributs
        """
        self.d_biomasse["masse_ini"] = masse_ini  # masse initiale
        self.d_biomasse["v_absorb"] = v_absorb  # vitesse de consomation
        self.d_biomasse["vd"] = v_deplacement  # vitesse de deplacement
        self.d_biomasse["v_max"] = v_max  # deplacement maximal
        self.d_biomasse["b_diff"] = 1 / np.sqrt(self.d_tore["largeur_case"])
        self.d_biomasse["k_conv"] = k_conv  # constante de conversion
        self.d_biomasse["nb_bact_ini"] = nb_bact_ini  # nombre de bactéries initiales

    # Creation des matrices

    def creer_concentrations(self):
        """
        Objectif : Créer la matrice de concentrations et appeler la création du substrat
        """
        self.concentrations = np.zeros((self.d_tore["nb_cellules_large"], self.d_tore["nb_cellules_large"]),
                                       dtype=np.float64)

        self.__creer_substrat()

    def __creer_substrat(self):
        """
        Objectif : Créer le substrat, c'est-à-dire une zone centrale où les concentrations sont à c_ini
        """
        # Met la concentration des cases centrales à c_ini
        nb_cel_large = self.d_tore["nb_cellules_large"]
        rayon_cases_subst = self.d_cellulose["rayon_cell"] / (self.d_tore["longueur"] / nb_cel_large)

        X, Y = np.meshgrid(np.linspace(-nb_cel_large / 2, nb_cel_large / 2, nb_cel_large),
                           np.linspace(nb_cel_large / 2, -nb_cel_large / 2, nb_cel_large),
                           indexing='xy')

        cellulose = ((X * X + Y * Y) <= (rayon_cases_subst * rayon_cases_subst))

        self.concentrations[cellulose] = self.d_cellulose["c_ini"]

    def __creer_bacterie(self):
        """
        Objectif : Placer des bactéries de manière regulière à une case plus loin que le rayon du substrat
        pour être en contact)
        :return: void
        """
        n = self.d_biomasse["nb_bact_ini"]
        if n != 0:
            intervalle = 2 * np.pi / n

            for i in np.arange(1, n + 1):
                x = np.cos(i * intervalle) * self.d_cellulose["rayon_cell"]
                y = np.sin(i * intervalle) * self.d_cellulose["rayon_cell"]
                self.bacteries.append(Bacterie(self, x, y, self.d_biomasse["masse_ini"]))

    # Lancement

    def demarrer(self):
        """
        Objectif : Appeler les fonction de lancement
        """
        print("demarage de la simulation")
        # vérifie que les données sont cohérentes
        # if delta > longueur ** 2 / (4 * v_diff):
        #    raise Exception("Erreur dans le pas de temps (delta est trop grand)")  # Lève une erreur
        # Création des concentrations
        self.creer_concentrations()

        # Creation des bacteries
        self.__creer_bacterie()

        self.isRunning = True

        # dictionnaire contenant les sauvegardes du programme
        self.saved = {}
        # masse totale de substrat à chaqe pas Delta
        self.saved["masse_substrat"] = []
        # tableau du nombre de bactéries à chaque uipdate_view
        self.saved["bacteries"] = []
        #self.load_simu("test3")

    def run(self):
        self.thread_lance = True
        print("thread actif")
        self.run_simu()

    # ----------------------------- Getter ---------------------------------------------------

    # Getter de la matrice de concentrations

    def get_concentrations(self):
        return self.concentrations

    def get_concentration_by_coord_xy(self, coord):
        i, j = self.convert_coord_xy_to_ij(coord)
        return self.get_concentration_by_coord_ij((i, j))

    def get_concentration_by_coord_ij(self, coords):
        return self.concentrations[self.coord_in_tore_ij((coords[0], coords[1]))]

    def get_saved_masse_substra(self):
        return self.saved["masse_substrat"]

    # Getter des bacteries
    def get_all_coords(self):
        """
        Objectif : Retourner les coordonnées de toutes les bactéries dans deux arrays
        Returns:
            array(int), array(int): tableaux des coordonnées des bactéries
        """
        X = []
        Y = []
        for bact in self.bacteries:
            x, y = bact.get_coord_xy()
            X.append(x)
            Y.append(y)

        return np.array(X), np.array(Y)

    def get_nb_bacteries(self):
        return len(self.bacteries)

    def get_saved_bacteries(self):
        # Retourne le tableau sauvegardant le nombre de bactéries au cours du temps
        return self.saved["bacteries"]

    def get_all_masses(self):
        masses = []
        for bact in self.bacteries:
            masses.append(bact.get_masse())
        return masses


    # getters de d_tore

    def get_delta(self):
        return self.d_tore["delta"]

    # ----------------------------- Setter ---------------------------------------------------

    def set_concentration_by_coord_ij(self, coords, c):
        """
        Setter de la matrice de concentration
        :param coords: Coordonnées de la concentration
        :param c: Nouvelle concentration
        :return: void
        """
        self.concentrations[self.coord_in_tore_ij((coords[0], coords[1]))] = c

    # ----------------------------- Update ---------------------------------------------------

    # PYQT
    def update_view(self):
        self.stateChangedSignal.emit()

    def update_saved(self):
        self.saved["masse_substrat"].append(self.concentrations.sum() * self.d_tore[
            "largeur_case"] ** 2)  # Ajoute la concentration actuelle aux sauvegardes
        self.saved["bacteries"].append(self.get_nb_bacteries())  # ajoute le nombre de bactérie actuel

    def update_all(self):
        self.update_view()
        self.update_saved()

    # ----------------------- Boucle principale ----------------------------------------------

    def run_simu(self):
        self.creer_concentrations()
        self.update_all()
        sleep(1)  # On laisse le temps à l'interface de se lancer
        while self.nb_step < self.__calcul_nb_tours():
            if self.isRunning:
                # n'execute la boucle que si la simulation n'est pas en pause
                self.step()
                self.nb_step += 1
                if self.nb_step % self.nb_tour_affich == 0:
                    self.update_all()
            else:
                sleep(1)

    def step(self):
        """
        Objectif : Lancer les cinq étapes de la boucle
        :return: void
        """
        self.__diffuse()
        self.__mouvement_bacteries()
        self.__bacteries_se_nourrisent()
        self.__division_bacteries()

    # Les __ devant une méthode servent à la declarer en privée
    def __diffuse(self):
        """
        Objectif : Mettre à jour les concentrations du model pour un pas de temps de diffusion
        :return: void
        """
        # c_actu + v_diff δ h² (Somme pour les 4 cases adj(c_case_adj*etat_case - c_actu)
        # Avec h la taille d'une cellule, δ le pas de temps, etat_case=1 si case à l'état liquide ou semi
        # La fonction roll() permet de décaller la matrice le long d'un axe
        self.concentrations += (self.d_cellulose["v_diff"] * self.d_tore["delta"] *
                                self.d_tore["largeur_case"] ** 2 * self.__somme_case_adj())

    def __somme_case_adj(self):
        """
        Méthode auxiliaire DE __diffuse.
        Objectif : Renvoyer la somme des diffusions avec les cases voisines sans les constantes.
        :return: la partie de la formule (Somme pour les 4 cases adj(c_actu − c_case_adj*etat_case)
        """
        # creation des concentrations décallés d'une ligne ou d'une colone
        c_haut = np.roll(self.concentrations, 1, axis=0)
        c_bas = np.roll(self.concentrations, -1, axis=0)
        c_droite = np.roll(self.concentrations, 1, axis=1)
        c_gauche = np.roll(self.concentrations, -1, axis=1)
        c_min = self.d_cellulose['c_min']  # sert juste à améliorer la lisibilité des calculs

        new_concentrations = np.zeros((self.d_tore["nb_cellules_large"], self.d_tore["nb_cellules_large"]),
                                      dtype=np.float64)

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
        Objectif : Effectuer un pas de temps de mouvement de bactéries.
        :return: void
        """
        for bact in self.bacteries:
            bact.se_deplacer()

    def __bacteries_se_nourrisent(self):
        """
        Objectif : Effectuer une dégradation de la cellulose et un gain de masse des bactéries pour les nourrir
        :return: void
        """
        for bact in self.bacteries:
            bact.manger()

    def __division_bacteries(self):
        """
        Objectif : Diviser chaque bacterie ayant une masse supérieure à sa masse maximale
        en deux bactéries placées au même point.
        :return: void
        """
        for bact in self.bacteries:
            if bact.peut_se_dupliquer():
                coords = bact.get_coord_xy()

                value = np.float64(0)
                nouv_bact = Bacterie(self, np.float64(coords[0]), np.float64(coords[1]), np.float64(bact.masse_act / 2))
                self.bacteries.append(nouv_bact)
                bact.masse_act /= 2

    # ----------------------------- Utilitaires ----------------------------------------------
    def convert_coord_xy_to_ij(self, coords):
        """
        Objectif : Permettre de convertir des coordonnées x, y en coordonnées i, j.
        Pré-requis : x et y doivent être entre -largeurTore/2 et largeurTore/2
        :return: (int, int): Coordonnées sur le tableau de concentration
        """
        x, y = coords

        j = ((x + self.d_tore['longueur'] / 2) / self.d_tore['largeur_case'])
        i = ((y + self.d_tore['longueur'] / 2) / self.d_tore['largeur_case'])

        return int(np.floor(i)), int(np.floor(j))
        # floor() fait un arrondi à l'inférieur, on convertit ensuite la valeur en entier.

    def coord_in_tore_ij(self, coords):
        """
        Objectif : Changer les coordonnées façon tore si elles depassent du tableau
        :return: tuple
        """
        coord_i = coords[0]
        coord_j = coords[1]
        if coords[0] >= self.d_tore["nb_cellules_large"]:
            coord_i = self.d_tore["nb_cellules_large"] - coords[0]

        elif coords[0] < 0:
            coord_i = self.d_tore["nb_cellules_large"] - (1 - coords[0])

        if coords[1] >= self.d_tore["nb_cellules_large"]:
            coord_j = self.d_tore["nb_cellules_large"] - coords[1]

        elif coords[1] < 0:
            coord_j = self.d_tore["nb_cellules_large"] - (1 - coords[1])

        return coord_i, coord_j

    def __calcul_nb_tours(self):
        # Le temps total est de 30h chaque tour de boucle prend delta heures
        return self.d_tore["temps_simu"] / self.d_tore["delta"]

    def save_simulation(self, nom):
        with open("../save/" + nom + ".json", "w") as fichier:
            data = {
                "nb_step" : self.nb_step,
                "d_tore" : self.d_tore,
                "d_biomasse" : self.d_biomasse,
                "d_cellulose" : self.d_cellulose,
                "nb_bacteries" : self.get_nb_bacteries(),
                "coord_x_bacteries": self.get_all_coords()[0].tolist(),
                "coord_y_bacteries": self.get_all_coords()[1].tolist(),
                "masses_bacteries" : self.get_all_masses(),
                "concentrations" : self.concentrations.tolist(),
                "saved" : self.saved
            }
            json.dump(data, fichier, indent=4)

    def load_simu(self, nom):
        with open("../save/"+nom+".json", "r") as fichier:
            data = json.load(fichier)
            # On charge toutes les variables
            self.nb_step = data["nb_step"]
            self.d_tore = data["d_tore"]
            self.d_cellulose = data["d_cellulose"]
            self.d_biomasse = data["d_biomasse"]
            #creation des bactéries
            self.bacteries = list()
            for i in range(data["nb_bacteries"]):
                self.bacteries.append(Bacterie(self, data["coord_x_bacteries"][i], data["coord_y_bacteries"][i], data["masses_bacteries"][i]))
            self.concentrations = data["concentrations"]
            self.saved = data["saved"]
            
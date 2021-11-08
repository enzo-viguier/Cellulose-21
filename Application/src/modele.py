import numpy as np

# Consignes générales :
# -> dimension de l'enceinte carrée : 1/2 longueur L = 40 µm de côté (en micron µ)
# -> nombre de cases : n =  250 dans chaque direction, donc 250² cases en tout
# -> concentration initiale : c_ini = 0.4 pg/µm² (picogrammes par micromètre carré)
# -> concentration pour diffuser : c_min = 0.3 pg/µm²
# -> vitesse de diffusion : 5 µm²/h (micromètres carrés par heure)
# -> pas de temps pour diffuser : delta = 0.005

# -> rayon du cercle initial de cellulose : R = 25 µm
# -> Temps de simulation : 30h
# -> pas de temps pour l'algorithme : Delta = 20mn (0.3h)


class Modele:
    # Variables statiques
    # Dictionnaire de constantes d'algo
    d_tore = {}
    # Dictionnaire de constantes relatives à la cellulose
    d_cellulose = {}

    def __init__(self):
        """
        Crée le modèle contenant les concentrations. Les longueurs sont en micromètres.
        """
        # Constructeur
        # Si vous voyez des variables de classes qui ne changent jamais, on peut les signaler

        self.init_d_cellulose()
        self.init_d_tore(0.01)

        self.concentrations = None
        
        #self.creer_concentrations(self.d_tore["nb_cellules"], self.d_cellulose["rayon_ini"])
        # On multiplie la matrice np chaque jour par la formule donnée

    def init_d_cellulose(self, c_ini=10, c_min=5, v_diff=0.02, rayon_ini=25):
        """
        Les fonctions init servent à initialiser les différents dictionnaires.
        Les valeurs de base permettent de créer une simulation fonctionnelle, sans abération.
        :param c_ini: Concentration initiale des cases
        :param c_min: Concentration minimale des cases
        :param v_diff: vitesse de diffusion du liquide
        :param rayon_ini: Rayon du cercle de substrat.
        """
        self.d_cellulose["c_ini"] = c_ini
        self.d_cellulose["c_min"] = c_min
        self.d_cellulose["v_diff"] = v_diff
        self.d_cellulose["rayon_ini"] = rayon_ini

    def init_d_tore(self, delta, longueur=40, nb_cellules=250):
        """
        NECESSITE LES VALEURS DE d_cellulose INITIALISEES
        :param longueur: (int) Longueur et largeur du tore
        :param nb_cellules: (int) Nombre de cellules initiales dans la simulation
        """
        self.d_tore["longueur"] = longueur
        self.d_tore["nb_cellules"] = nb_cellules
        self.d_tore["largeur_case"] = longueur / nb_cellules
        # vérifie que les données sont cohérentes
        if (delta > self.d_tore["longueur"] ** 2 / (4 * self.d_cellulose["v_diff"])):
            raise Exception("Erreur dans le pas de temps (delta est trop grand)")  # Lève une erreur
        self.d_tore["delta"] = delta


    def to_string(self):
        """
        Retourne un string contenant les différentes valeurs des constantes
        """
        # return "test"
        return f"d_cellulose = :\n \
        cIni = {self.d_cellulose['c_ini']}\
        cMin = {self.d_cellulose['c_min']}\
        v_diff = {self.d_cellulose['v_diff']}\
        rayon_ini = {self.d_cellulose['rayon_ini']} \
        \nd_tore = \n\
        longueur =  {self.d_tore['longueur']}\
        nb_cellules = {self.d_tore['nb_cellules']}\
        largeur_case = {self.d_tore['largeur_case']}\
        delta = {self.d_tore['delta']}"

    def get_concentrations(self):
        return self.concentrations

    def get_concentration_by_coord_xy(self, coord, nb_case_decalage_droite=0, nb_case_decalage_haut=0):
        """
        Renvoie la concentration d'une case, la case est trouvée par les coordonnées
        coord décalées de nx case en horizontal et ny en vertical

        :param coord: (tuple) Coordonnées de la case centrale
        :param nb_case_decalage_droite: (float) Nombre de cases de décalage sur axe abscisses
        :param nb_case_decalage_haut: (float) Nombre de cases de décalage sur axe ordonnées
        """
        x, y= coord #depaquetage de la case demandé
        x = (x+nb_case_decalage_droite)%(self.d_tore['longueur']/2)
        y = (y+nb_case_decalage_haut)%(self.d_tore['longueur']/2)

        i, j = self.convert_coord_xy_to_ij((x, y))

        return self.concentrations[i, j]

    def convert_coord_xy_to_ij(self, coord):
        """Permet de convertir des coordonnées x, y en coordonnées i, j. x et y doivent être entre -largeurTore/2 et largeurTore/2

        Returns:
            (int, int): Coordonnées sur le tableau de concentration
        """
        x, y = coord
        
        j = ((x+self.d_tore['longueur']/2)/self.d_tore['largeur_case'])
        i = ((-y+self.d_tore['longueur']/2)/self.d_tore['largeur_case'])

        return (int(np.floor(i)), int(np.floor(j))) #Floor fait un arrondi à l'inferieur, on convertie ensuite la valeur en int
    

    def set_concentration_par_coord(self, coord, c, nb_case_decalage_x=0, nb_case_decalage_y=0):
        """change la concentration d'une case, la case est trouvé par les coordonnées 
        coord décalé de nx case en horizontal et ny en vertical

        :param coord: (tuple) Coordonnées de la case centrale
        :param nx: (int) Nombre de cases de décalage sur axe abscisses
        :param ny: (int) Nombre de cases de décalage sur axe ordonnées
        """

        x, y= coord
        x = x+nb_case_decalage_x%self.d_tore['longueur']
        y = y+nb_case_decalage_y%self.d_tore['longueur']

        i, j = self.convert_coord_xy_to_ij((x, y))

        self.concentrations[i, j] = c


    def __creer_substrat(self, nb_cellules_large, rayon_cercle_ini):
        # Créer un cercle de cases avec une concentration c_ini centré dans le repère de rayon rayon_cercle_ini

        X, Y = np.meshgrid(np.linspace(-125, 125, 250),
                           np.linspace(125, -125, 250),
                           indexing='xy')

        cellulose = ((X * X + Y * Y) <= (rayon_cercle_ini * rayon_cercle_ini))

        self.concentrations[cellulose] = self.d_cellulose["c_ini"]

    def creer_concentrations(self, nb_cellules_large, rayon_cercle_ini):
        self.concentrations = np.zeros((nb_cellules_large, nb_cellules_large), dtype=np.float64)*self.d_cellulose['c_ini']
        #self.__creer_substrat(nb_cellules_large, rayon_cercle_ini)



    def afficher_tore(self):
        #print("Taille tore (par un imshow) :")
        #np.imshow(self.tore)
        print("afficher tore")
        print(self.tore)

    def afficher_concentrations(self):
        print("afficher concentrations")
        print(self.concentrations)

    def __creer_bacterie(self, n):
        """
        :param n: le nombre de bactéries du modèle
        :return: void
        Place des bactéries de manière regulière à une case plus loin que le rayon du substrat (pour être en contact)
        """
        # TODO
        pass

    def jour(self):
        """
        :return: void
        La fonction jour lance les cinq étapes du cycle
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
        Renvoie la somme des diffusions avec les cases voisines sans les constantes. 
        :return: la partie de la formule (Somme pour les 4 cases adj(c_actu − c_case_adj*etat_case)
        Fait la somme des diffusions des cases adjacentes
        """
        # décomposition de (np.roll(concentrations, 1, axis=0)<self.cMin )*( concentrations<self.cMin)*((np.roll(concentrations, 1, axis=0))-concentrations)
        # np.roll(concentrations, 1, axis=0)<self.cMin )*( concentrations<self.cMin)
        # -> vérifie que les cases ne sont pas sous état solide
        # ((np.roll(concentrations, 1, axis=0))-concentrations) calcule la diffusion comme si la case est semi-liquide
        # En python, un boolean = False est equivalent à un int = 0 donc on peut en mettre dans les calculs


        #creation des concentrations décallés d'une ligne ou d'une colone
        c_haut = np.roll(self.concentrations, 1, axis=0)
        c_bas = np.roll(self.concentrations, -1, axis=0)
        c_droite = np.roll(self.concentrations, 1, axis=1)
        c_gauche =np.roll(self.concentrations, -1, axis=1)
        c_min = self.d_cellulose['c_min'] #sert juste à améliorer la lisibilité des calculs

        new_concentrations = np.copy(self.concentrations)

        new_concentrations[self.concentrations <= c_min] =\
            c_haut[c_haut <= c_min] - self.concentrations[self.concentrations <= c_min]


        new_concentrations[self.concentrations <= c_min] +=\
            c_bas[c_bas <= c_min] - self.concentrations[self.concentrations <= c_min]

        new_concentrations[self.concentrations <= c_min] +=\
            c_droite[c_droite <= c_min] - self.concentrations[self.concentrations <= c_min]

        new_concentrations[self.concentrations <= c_min] +=\
            c_gauche[c_gauche <= c_min] - self.concentrations[self.concentrations <= c_min]

        return new_concentrations
        
        
        #Code desactivé mais gard& en sauvegarde
        new_concentrations += (c_droite < self.d_cellulose["c_min"]) * (
                self.concentrations < self.d_cellulose["c_min"]) * (
                                      c_droite - self.concentrations)

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

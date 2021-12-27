import numpy as np

class Bacterie:
    # Mettre ici les variables statiques
    # Dictionnaire de constantes de la biomasse
    d_biomasse = {}

    def __init__(self, model, x, y, masse_ini):
        self.x = x
        self.y = y
        self.masse_act = masse_ini
        self.model = model

    def get_x(self):
        return self.x

    def get_y(self):
        return self.y

    def get_coord_xy(self):
        return self.x, self.y

    def se_deplacer(self):
        """
        Objectif :  Déplacer la bactérie en fonction de la vitesse de déplacement
        à finir !
        """
        if self.model.get_concentration_by_coord_xy((self.x, self.y)) <= self.model.d_cellulose["c_min"]:

            delta = self.model.d_tore["delta"]
            demi_longueur = self.model.d_tore["longueur"]/2
            vd_x, vd_y = self.__calcul_vitesse_deplacement()
            self.x = self.x + delta*vd_x + self.model.d_biomasse["b_diff"] * np.sqrt(delta) * self.random()
            # np.random.rand() ∈ [0;1]
            # Si les coordonnées sortent de l'environnement, les faire passer de l'autre côté du tore
            if self.x > demi_longueur:
                self.x = -demi_longueur
            elif self.x < -demi_longueur:
                self.x = demi_longueur

            self.y = self.y + delta*vd_y + self.model.d_biomasse["b_diff"] * np.sqrt(delta) * self.random()
            # Si les coordonnées sortent de l'environnement, les faire passer de l'autre côté du tore
            if self.y > demi_longueur:
                self.y = -demi_longueur
            elif self.y < -demi_longueur:
                self.y = demi_longueur

    def random(self):
        r = (np.random.rand()-0.5)*2
        print("random = ", r)
        return r


    def __calcul_vitesse_deplacement(self):
        """
        Méthode privée
        Objectif : Calculer la vitesse de déplacement d'une bactérie puis
        retourner la vitesse sur l'axe x et la vitesse sur l'axe y
        :return: tuple
        """
        vd = self.model.d_biomasse["vd"]
        # Convertir coordonnées x,y en i,j
        # (i, j) = self.model.convert_coord_xy_to_ij((self.x, self.y))
        # print("My i = ", i, ". My j = ", j)
        # Exemple des lignes suivantes décomposées
        # c_est = self.model.get_concentration_by_coord_ij((i + 1, j))
        # c_ouest = self.model.get_concentration_by_coord_ij((i - 1, j))
        # c_nord = self.model.get_concentration_by_coord_ij((i, j + 1))
        # c_sud = self.model.get_concentration_by_coord_ij((i, j - 1))
        c_est = self.model.get_concentration_by_coord_xy((self.x+1, self.y))
        c_ouest = self.model.get_concentration_by_coord_xy((self.x-1, self.y))
        c_nord = self.model.get_concentration_by_coord_xy((self.x, self.y+1))
        c_sud = self.model.get_concentration_by_coord_xy((self.x, self.y-1))
        h = self.model.d_tore["largeur_case"]
        print("c_est", c_est)
        print("c_ouest", c_ouest)
        print("c_nord", c_nord)
        print("c_sud", c_sud)
        vd_x = vd * (c_est - c_ouest) / (2 * h)
        vd_y = vd * (c_nord - c_sud) / (2 * h)
        print("vd_x : ", vd_x, "vd_y :", vd_y)
        return vd_x, vd_y

    def manger(self):
        """
        Objectif :
        :return: void
        """
        qt_mange = 0
        coord_case_xy = (self.x, self.y)
        coords_ij_centre = self.model.convert_coord_xy_to_ij(coord_case_xy)
        # On récupère les coordonnées de la case centrale (emplacement de la bactérie)
        print(coord_case_xy)
        print("ij = ", coords_ij_centre)
        # main_case = self.modele.get_concentration_by_coord_ij(coords_ij)
        for i in np.arange(-1, 2):
            for j in np.arange(-1, 2):

                # Vérification que les coordonnées ne sortent pas du tableau avec l'incrementation
                coords_ij = (coords_ij_centre[0]+i, coords_ij_centre[1]+j)

                # On prend les cases autour du centre ainsi que le centre
                case = self.model.get_concentration_by_coord_ij(coords_ij)
                conso = np.minimum(np.square(self.model.d_tore["largeur_case"]) * case, self.model.d_biomasse["v_absorb"])
                # carre à verifier
                qt_mange += conso
                self.model.set_concentration_by_coord_ij(coords_ij, case - (conso / np.square(self.model.d_tore["largeur_case"])))


    def gain_masse(self, conso):
        """
        Objectif : Augmenter la masse de la bactérie en fonction de ce qu'elle a absorbé
        :argument conso (float) masse de cellulose dégradée par la bactérie
        """
        self.masse_act += self.model.d_biomasse["k_conv"] * conso

    def peut_se_dupliquer(self):
        """
        Objectif : Déterminer si la bactérie peut se dupliquer
        :return: boolean
        """
        if self.masse_act > self.model.d_biomasse["masse_ini"]*2:
            return True
        return False
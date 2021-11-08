import numpy as np


class Bacterie:
    # Mettre ici les variables statiques
    # Dictionnaire de constantes de la biomasse
    d_biomasse = {}

    def __init__(self, modele, x, y, masse_act, masse_ini=1, v_absorb=0.1, v_deplacement=0.1): #Valeurs pour l'instant arbitraires
        # Il ne faudrait pas une masse actuelle ?
        self.x = x
        self.y = y
        self.masse_act = masse_act
        self.modele = modele
        self.init_d_biomasse(masse_ini, v_absorb, v_deplacement)

    def init_d_biomasse(self, masse_ini, v_absorb, v_deplacement):
        # print("d_biomasse['masse_ini']=", self.d_biomasse["masse_ini"])
        # print("type(d_biomasse['masse_ini'])=", type(self.d_biomasse["masse_ini"]))
        self.d_biomasse["masse_ini"] = masse_ini
        self.d_biomasse["v_absorb"] = v_absorb
        self.d_biomasse["v_deplace"] = v_deplacement


    def se_deplacer(self):
        """
        Déplace la bactérie en fonction de la vitesse de déplacement
        à finir !
        """
        delta = self.modele.d_cellulose["delta"]
        vd_x, vd_y = self.__calcul_vitesse_deplacement()
        self.x = self.x + delta*vd_x + 1 * (np.sqrt(delta)*np.random.rand()) # np.random.rand() ∈ [0;1]
        self.y = self.y + delta*vd_y + 1 * (np.sqrt(delta) * np.random.rand())

    def manger(self):
        coord_case = (self.x, self.y)
        main_case = self.modele.convert_coord_to_case(coord_case)
        for i in range(-1, 2):
            for j in range(-1, 2):
                case = self.modele.get_concentration_par_coord(coord_case, i, j) 
                conso = np.minimum(case * self.modele.d_tore["largeur_case"], self.d_biomasse["v_absorb"])
                self.modele.set_concentration_par_coord(coord_case, case-conso, i, j)

    def gain_masse(self, conso):
        """augmente la masse de la bactérie en fonction de ce qu'elle a absoré

        Args:
            conso (float): masse de cellulose dégradé par la bactérie
        """
        pass

    def se_dupliquer(self):
        # TODO
        pass

    def __calcul_vitesse_deplacement(self):
        """
        Calcule la vitesse de déplacement d'une bactérie
        et retourne la vitesse sur l'axe x et la vitesse sur l'axe y
        """
        vd = self.d_biomasse["v_deplace"]
        c_est = self.modele.get_concentration_par_coord((self.x, self.y), 1, 0)
        c_ouest = self.modele.get_concentration_par_coord((self.x, self.y), -1, 0)
        c_nord = self.modele.get_concentration_par_coord((self.x, self.y), 0, 1)
        c_sud = self.modele.get_concentration_par_coord((self.x, self.y), 0, -1)
        h = self.modele.d_cellulose["largeur_case"]
        vd_x = vd*(c_est - c_ouest) / 2*h
        vd_y = vd*(c_nord - c_sud) / 2*h
        return vd_x, vd_y

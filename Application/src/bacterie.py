import numpy as np

# - masse initiale bactérie : m_ini = 0.4 pg
# vitesse max des bactéries : 10 µm/h
# - vitesse de dérive des bactéries : vd = 0.1 (µm^4/(pg h)
# - écart-type sur la vitesse de déplacement : b_diff = 1 µm/sqrt(h)
# constante de conversion masse/biomass : k_conv = 0.2 (sans unité)
# vitesse de consommation : v_cons = 0.2 pg/h
# population initiale : 50

class Bacterie:
    # Mettre ici les variables statiques
    # Dictionnaire de constantes de la biomasse
    d_biomasse = {}

    def __init__(self, model, x, y, masse_act, masse_ini=0.4, v_absorb=0.1, v_deplacement=0.1):
        # Valeurs pour l'instant arbitraires
        # Il ne faudrait pas une masse actuelle ?
        self.x = x
        self.y = y
        self.masse_act = masse_act
        self.model = model
        self.init_d_biomasse(masse_ini, v_absorb, v_deplacement)

    def init_d_biomasse(self, masse_ini, v_absorb, v_deplacement):
        # print("d_biomasse['masse_ini']=", self.d_biomasse["masse_ini"])
        # print("type(d_biomasse['masse_ini'])=", type(self.d_biomasse["masse_ini"]))
        self.d_biomasse["masse_ini"] = masse_ini
        self.d_biomasse["v_absorb"] = v_absorb
        self.d_biomasse["vd"] = v_deplacement
        self.d_biomasse["b_diff"] = 1/np.sqrt(self.model.d_tore["largeur_case"])


    def se_deplacer(self):
        """
        Déplace la bactérie en fonction de la vitesse de déplacement
        à finir !
        """
        delta = self.model.d_cellulose["delta"]
        vd_x, vd_y = self.__calcul_vitesse_deplacement()
        self.x = self.x + delta*vd_x + self.d_biomasse["b_diff"] * (np.sqrt(delta)*np.random.rand()) # np.random.rand() ∈ [0;1]
        self.y = self.y + delta*vd_y + self.d_biomasse["b_diff"] * (np.sqrt(delta) * np.random.rand())


    def manger(self):
        coord_case_xy = (self.x, self.y)
        coords_ij_centre = self.model.convert_coord_xy_to_ij(coord_case_xy)
        # On recupere les coordonnes de la case centrale (emplacement de la bactérie)

        # main_case = self.modele.get_concentration_by_coord_ij(coords_ij)
        for i in np.arange(-1, 2):
            for j in np.arange(-1, 2):
                coords_ij = (coords_ij_centre[0]+i, coords_ij_centre[1]+j)
                # On prend les cases autour du centre ainsi que le centre
                case = self.model.get_concentration_by_coord_ij(coords_ij)
                conso = np.minimum(np.square(self.model.d_tore["largeur_case"]) * case, self.d_biomasse["v_absorb"]) #carre à verifier
                self.model.set_concentration_by_ij(coords_ij, case - (conso / np.square(self.model.d_tore["largeur_case"])))


    def gain_masse(self, conso):
        """augmente la masse de la bactérie en fonction de ce qu'elle a absorbé
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
        vd = self.d_biomasse["vd"]
        # Convertir coordonnées x,y en i,j
        (i, j) = self.model.convert_coord_xy_to_ij((self.x, self.y))
        c_est = self.model.get_concentration_by_coord_ij((i+1, j))
        c_ouest = self.model.get_concentration_by_coord_ij((i-1, j))
        c_nord = self.model.get_concentration_by_coord_ij((i, j+1))
        c_sud = self.model.get_concentration_by_coord_ij((i, j-1))
        h = self.model.d_tore["largeur_case"]
        vd_x = vd*(c_est - c_ouest) / 2*h
        vd_y = vd*(c_nord - c_sud) / 2*h
        return vd_x, vd_y

    def get_coord_xy(self):
        return (self.x, self.y)



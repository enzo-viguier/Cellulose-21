
class Bacterie:
    # Mettre ici les variables statiques
    # Dictionnaire de constantes de la biomasse
    d_biomasse = {"masse_ini": 0.0, "v_absorb":0, "v_deplace": 0.0},

    def __init__(self, modele, x, y, masse_ini, masse_act, v_absorb, v_deplacement):
        # Il ne faudrait pas une masse actuelle ?
        self.x = x
        self.y = y
        self.d_biomasse["masse_ini"] = masse_ini
        self.masse_act = masse_act
        self.d_biomasse["v_absorb"] = v_absorb
        self.d_biomasse["v_deplace"] = v_deplacement
        self.modele = modele

    def se_deplacer(self):
        # TODO
        pass

    def manger(self, modele):
        # TODO
        coord_case = (self.x, self.y)

        for i in range(-1, 2):
            for j in range(-1, 2):
                case = modele.get_concentration_par_coord(coord_case, i, j) 
                conso = max(case * modele.d_cellulose["largeur_case"], self.d_biomasse["v_absorb"])
                modele.set_concentration_par_coord(coord_case, case-conso, i, j)

    def gain_masse(self, conso):
        """augmente la masse de la bactérie en fonction de ce qu'elle a absoré

        Args:
            conso (float): masse de cellulose dégradé par la bactérie
        """
        pass

    def se_dupliquer(self):
        # TODO
        pass

    def calcul_vitesse_deplacement(self):
        """
        Calcule la vitesse de déplacement d'une bactérie
        et retourne la vitesse sur l'axe x et la vitesse sur l'axe y
        """
        vd = self.d_biomasse["v_deplace"]
        c_est = self.modele.get_concentration_par_coord((self.x self.y), 1, 0)
        c_ouest = self.modele.get_concentration_par_coord((self.x, self.y), -1, 0)
        c_nord = self.get_concentration_par_coord((self.x, self.y), 0, 1)
        c_sud = self.get_concentration_par_coord((self.x, self.y), 0, -1)
        h = self.modele.d_cellulose["largeur_case"]
        v_d_x = vd*(c_est - c_ouest) / 2*h
        v_d_y = vd*(c_nord - c_sud) / 2*h
        return v_d_x, v_d_y

def min(a, b):
    if(a<b):
        return a
    return b

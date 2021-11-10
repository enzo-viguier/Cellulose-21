from model import *
from bacterie import *

class TestBacterie:
    def test_calcul_vitesse_deplacement(self):
            model = Model()
            model.init_d_tore(1, 10, 10)
            model.init_d_cellulose(c_min=0, c_ini=2)
            model.creer_concentrations(10, 1)
            
            bact = Bacterie(model, 0, 0, 1, v_absorb=0.3)
            print("coordonnées xy bactérie avant : ", bact.get_coord_xy())
            vd_x, vd_y = bact.calcul_vitesse_deplacement()
            print("coordonnées xy bactérie après : ", vd_x, vd_y)

test = TestBacterie()
test.test_calcul_vitesse_deplacement()
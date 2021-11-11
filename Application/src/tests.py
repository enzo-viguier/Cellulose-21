import unittest
from model import *
from bacterie import *

class UneClasseDeTest(unittest.TestCase):

    def test_simple(self):
        self.assertTrue(True)

    def main_test_diffusion(self):
        model = Model(delta=1, longueur=3, nb_cellules=5, rayon_ini=1)

        model.creer_concentrations(model.d_tore["nb_cellules"], model.d_cellulose["rayon_ini"])
        model.set_concentration_by_ij((0, 0), 0.2)
        model.set_concentration_by_ij((0, 1), 0.4)

        #model.afficher_concentrations()


        for i in range(2000):
            model.jour()
            #imshow
        for i in range(5):
            for j in range(5):
                self.assertTrue(model.concentrations[i, j]<0.024001 and model.concentrations[i, j]>0.023999) #on a pas une concentration exacte



    def test_get_concentration_by_coord(self):
        model = Model(delta=1, longueur=3, nb_cellules=5, rayon_ini=1)
        model.creer_concentrations(model.d_tore["nb_cellules"], model.d_cellulose["rayon_ini"])



    def test_set_concentration_by_coord(self):
        model = Model(delta=1, longueur=10, nb_cellules=10, c_min=110)
        #model.init_d_tore(1, 10, 10)

        model.creer_concentrations(model.d_tore["nb_cellules"], model.d_cellulose["rayon_ini"])


        model.set_concentration_by_ij((0, 0), 100)

        for i in range(10000):
            model.jour()
        self.assertTrue(model.get_concentration_by_coord_ij((0, 0)) <1.0001 and model.get_concentration_by_coord_ij((0, 0)) > 0.99999 )
        

    def test_manger_bacterie(self):
        model = Model(delta=1, longueur=10, nb_cellules=10, c_min=0, c_ini=2)

       
        model.creer_concentrations(10, 1)

        bact = Bacterie(model, 0, 0, 1, v_absorb=0.3)
        print("coordonnées xy bactérie : ", bact.get_coord_xy())

        #On met la concentration du 0 xy à 2
        model.set_concentration_by_ij(model.convert_coord_xy_to_ij((0, 0)), 2)
        print("Concentration avant manger", model.get_concentration_by_coord_xy((0, 0)))
        for i in range(7):
            bact.manger()


        print("Concentration après manger", model.get_concentration_by_coord_xy((0, 0)))
        self.assertTrue(model.get_concentration_by_coord_ij((0, 0))==0)

test = UneClasseDeTest()
test.test_simple()
test.main_test_diffusion()
#test.test_get_concentration_by_coord()
test.test_set_concentration_by_coord()
test.test_manger_bacterie()
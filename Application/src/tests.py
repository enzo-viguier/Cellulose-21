import unittest
from model import *
from bacterie import *

class UneClasseDeTest(unittest.TestCase):

    def test_simple(self):
        self.assertTrue(True)

    def main_test_diffusion(self):
        model = Model(delta=1, longueur=3, nb_cellules_large=5, c_ini=0,rayon_cell=1)

        model.set_concentration_by_coord_ij((0, 0), 0.2)
        model.set_concentration_by_coord_ij((0, 1), 0.3)
        #model.afficher_concentrations()

        for i in range(1000):
            model.jour()
            #imshow

        #model.afficher_concentrations()
        for i in range(5):
            for j in range(5):
                self.assertTrue(model.concentrations[i, j]<0.021 and model.concentrations[i, j]>0.0199) #on a pas une concentration exacte



    def test_get_concentration_by_coord(self):
        model = Model(delta=1, longueur=3, nb_cellules_large=5, rayon_cell=1)



    def test_set_concentration_by_coord(self):
        model = Model()

        model.set_concentration_by_coord_ij((0, 0), 100)

        self.assertTrue(model.get_concentration_by_coord_ij((0, 0)) ==100)
        


    def test_manger_bacterie(self):
        model = Model(delta=1, longueur=10, nb_cellules_large=10, c_min=0, c_ini=2, v_absorb=0.3)

    
        bact = Bacterie(model, 0, 0, 1)
        print("coordonnées xy bactérie : ", bact.get_coord_xy())

        #On met la concentration du 0 xy à 2
        model.set_concentration_by_coord_ij(model.convert_coord_xy_to_ij((0, 0)), 2)
        print("Concentration avant manger", model.get_concentration_by_coord_xy((0, 0)))
        for i in range(7):
            bact.manger()

        print("Concentration après manger", model.get_concentration_by_coord_xy((0, 0)))
        self.assertTrue(model.get_concentration_by_coord_xy((0, 0))==0)

test = UneClasseDeTest()
test.test_simple()
test.main_test_diffusion()
#test.test_get_concentration_by_coord()
test.test_set_concentration_by_coord()
test.test_manger_bacterie()
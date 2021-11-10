import unittest
from modele import *
from bacterie import *

class UneClasseDeTest(unittest.TestCase):

    def test_simple(self):
        self.assertTrue(True)

    def main_test_diffusion(self):
        modele = Modele()
        modele.init_d_tore(1, 3, 5)
        modele.init_d_cellulose(rayon_ini=1)
        #print(modele.to_string())

        modele.creer_concentrations(modele.d_tore["nb_cellules"], modele.d_cellulose["rayon_ini"])
        modele.set_concentration_by_ij((0, 0), 0.2)
        modele.set_concentration_by_ij((0, 1), 0.4)

        #modele.afficher_concentrations()


        for i in range(2000):
            modele.jour()
        for i in range(5):
            for j in range(5):
                self.assertTrue(modele.concentrations[i, j]<0.024001 and modele.concentrations[i, j]>0.023999) #on a pas une concentration exacte



    def test_get_concentration_by_coord(self):
        modele = Modele()
        modele.init_d_tore(1, 3, 5)
        modele.init_d_cellulose(rayon_ini=1)
        modele.creer_concentrations(modele.d_tore["nb_cellules"], modele.d_cellulose["rayon_ini"])



    def test_set_concentration_by_coord(self):
        modele = Modele()
        modele.init_d_tore(1, 10, 10)
        modele.init_d_cellulose(c_min=110)

        modele.creer_concentrations(modele.d_tore["nb_cellules"], modele.d_cellulose["rayon_ini"])


        modele.set_concentration_by_ij((0, 0), 100)

        for i in range(10000):
            modele.jour()
        self.assertTrue(modele.get_concentration_by_coord_ij((0, 0)) <1.0001 and modele.get_concentration_by_coord_ij((0, 0)) > 0.99999 )
        

    def test_manger_bacterie(self):
        modele = Modele()
        modele.init_d_tore(1, 10, 10)
        modele.init_d_cellulose(c_min=0, c_ini=2)
        modele.creer_concentrations(10, 1)

        bact = Bacterie(modele, 0, 0, 1, v_absorb=0.3)

        modele.set_concentration_by_ij((0, 0), 2)
        print("Concentration avant manger", modele.get_concentration_by_coord_ij((0, 0)))
        for i in range(20):
            bact.manger()

        print("Concentration après manger", modele.get_concentration_by_coord_ij((0, 0)))
        self.assertTrue(modele.get_concentration_by_coord_ij((0, 0))==0)

test = UneClasseDeTest()
test.test_simple()
test.main_test_diffusion()
#test.test_get_concentration_by_coord()
test.test_set_concentration_by_coord()
test.test_manger_bacterie()
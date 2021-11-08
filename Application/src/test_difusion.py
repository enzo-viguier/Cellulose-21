import unittest
from modele import *
from bacterie import *

class UneClasseDeTest(unittest.TestCase):

    def test_simple(self):
        self.assertTrue(True)


    def test_diffusion(self):
        modele = Modele()
        self.assertTrue(modele.concentrations[0, 0]==self.d_cellulose["c_ini"])
        for i in range(10):
            modele.jour()

        assertTrue(modele.concentrations[0, 0]==self.d_cellulose["c_ini"])
        
    def main_test_diffusion(self):
        modele = Modele()
        modele.init_d_tore(1, 3, 5)
        modele.init_d_cellulose(rayon_ini=1)
        #print(modele.to_string())

        modele.creer_concentrations(modele.d_tore["nb_cellules"], modele.d_cellulose["rayon_ini"])
        modele.set_concentration_par_coord((0, 0), 0.2)
        modele.set_concentration_par_coord((0, 1), 0.4)

        #modele.afficher_concentrations()


        for i in range(2000):
            modele.jour()
        for i in range(5):
            for j in range(5):
                self.assertTrue(modele.concentrations[i, j]<0.024001 and modele.concentrations[i, j]>0.023999) #on a pas une concentration exacte

    def test_creer_tore(self):
        print("Test creer tore inactif")
        modele = Modele()
        modele.init_d_tore(1, 2, 5)
        modele.creer_tore()
        #modele.afficher_tore()

    def test_get_concentration_by_coord(self):
        modele = Modele()
        modele.init_d_tore(1, 3, 5)
        modele.init_d_cellulose(rayon_ini=1)
        modele.creer_concentrations(modele.d_tore["nb_cellules"], modele.d_cellulose["rayon_ini"])

        modele.set_concentration_par_coord((0, 0), 3)
        conc = modele.get_concentration_par_coord((0, 0))
        print("concentration =", conc)
        self.assertTrue(conc==3)
        conc = modele.get_concentration_par_coord((1, -1))
        print("concentration =", conc)
        self.assertTrue(conc==0)
        conc = modele.get_concentration_par_coord((3, -4))
        print("concentration =", conc)
        self.assertTrue(conc==0)
        conc = modele.get_concentration_par_coord((5, -8))
        print("concentration =", conc)
        self.assertTrue(conc==0)
        conc = modele.get_concentration_par_coord((10, -10))
        self.assertTrue(conc==0)


    def test_set_concentration_by_coord(self):
        modele = Modele()
        modele.init_d_tore(1, 10, 10)
        modele.init_d_cellulose(c_min=110)

        modele.creer_concentrations(modele.d_tore["nb_cellules"], modele.d_cellulose["rayon_ini"])


        modele.set_concentration_par_coord((0, 0), 100)

        for i in range(10000):
            modele.jour()
        self.assertTrue(modele.get_concentration_par_coord((0, 0)) <1.0001 and modele.get_concentration_par_coord((0, 0)) > 0.99999 )
        

    def test_bacterie_manger(self):
        modele = Modele()
        modele.init_d_tore(1, 10, 10)
        modele.init_d_cellulose(c_min=110)

        

test = UneClasseDeTest()
#test.test_simple()
#test.test_diffusion()
#test.main_test_diffusion()
#test.test_creer_tore()
test.test_get_concentration_by_coord()
test.test_set_concentration_by_coord()

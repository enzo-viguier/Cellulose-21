from modele import *


modele = Modele()

# Modifie 2 cases du tableau pour mettre des concentrations qui diffusent
modele.set_concentration_par_coord((0, 0), 0.2)
modele.set_concentration_par_coord((0, 1), 0.4)

modele.afficher_concentrations()
# Test des diffusions
for i in range(100):
    modele.jour()

modele.afficher_concentrations()

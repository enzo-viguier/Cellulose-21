from model import *


model = Model()

# Modifie 2 cases du tableau pour mettre des concentrations qui diffusent
model.set_concentration_par_coord((0, 0), 0.2)
model.set_concentration_par_coord((0, 1), 0.4)

model.afficher_concentrations()
# Test des diffusions
for i in range(100):
    model.jour()

model.afficher_concentrations()

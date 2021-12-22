import matplotlib as mpl
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib import cm
from matplotlib.colors import Normalize
import numpy as np

mpl.use('QT5Agg')


class Mplwidget(FigureCanvasQTAgg):
    def __init__(self, parent):
        self.fig = Figure()
        self.ax = self.fig.add_subplot(111)
        data = np.zeros(2500).reshape((50, 50))
        self.data_ref = self.ax.imshow(data, origin='lower',
                                       norm=Normalize(0, 0.4),
                                       cmap=cm.coolwarm,
                                       interpolation='bicubic',
                                       extent=([-1, 1, -1, 1]),
                                       aspect='auto')
        
        super().__init__(self.fig)
        self.setParent(parent)

    def update_plot(self, data):
        #Le *5/2 sert à positionner bien les bactéries en prenant en compte la taille du canvas
        self.ax.scatter(data[0]*5/2, data[1]*5/2, 20, "green", marker="*")
        #print(self.ax.__class__)

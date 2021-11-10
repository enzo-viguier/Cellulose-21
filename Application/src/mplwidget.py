import matplotlib as mpl
mpl.use('QT5Agg')
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib import cm
from matplotlib.colors import Normalize
import numpy as np

class Mplwidget(FigureCanvasQTAgg):
    def __init__(self, parent):
        self.fig = Figure()
        self.ax = self.fig.add_subplot(111)
        data = np.arange(900).reshape((30, 30))
        self.data_ref = self.ax.imshow(data, origin='lower',
                                       norm=Normalize(0, 2500),
                                       cmap=cm.coolwarm,
                                       interpolation='bicubic',
                                       extent=([-1, 1, -1, 1]))
        super().__init__(self.fig)
        self.setParent(parent)

    #        FigureCanvasQTAgg.__init__(self,self.fig)
    #        super(Canvas, self).__init__(self.fig,parent)

    def update_plot(self):
        print(self.ax.__class__)
#        self.canvas.axes.plot(self.xdata, self.ydata)

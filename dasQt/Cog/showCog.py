

import sys
from PyQt6.QtWidgets import (QApplication, QWidget, QPushButton, QToolTip, QMessageBox,
                             QMainWindow, QHBoxLayout, QVBoxLayout, QFileDialog, QSizePolicy,
                             QSlider, QLabel, QLineEdit, QGridLayout, QGroupBox, QListWidget,
                             QTabWidget, QDialog)
from PyQt6.QtGui import QIcon, QFont, QAction, QGuiApplication
from PyQt6.QtCore import Qt, QTimer

import matplotlib
matplotlib.use('QtAgg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import numpy as np
import dasQt.das as das
import os
import matplotlib.pyplot as plt
plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.serif'] = ['Times New Roman'] + plt.rcParams['font.serif']
plt.rcParams['font.size'] = 16


from dasQt.Logging.logPy3 import HandleLog



class CogMainWindow(QMainWindow):
    def __init__(self, MyProgram, title="Dispersion"):
        super().__init__()

        self.is_closed = False
        
        self.logger = HandleLog(os.path.split(__file__)[-1].split(".")[0], path=os.getcwd(), level="DEBUG")
        self.MyProgram = MyProgram
        self.setWindowTitle(title)
        self.initUI()


    def initUI(self):
        # 创建一个主窗口的中心部件
        central_widget = QWidget()
        central_widget.setLayout(QHBoxLayout())
        self.setCentralWidget(central_widget)

        self.layout = central_widget.layout()

        # 设置主窗口的大小策略
        size_policy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setSizePolicy(size_policy)
        
        self.initFigure()
        self.show()



    def initFigure(self):
        self.figAll = Figure()
        self.canvasAll = FigureCanvas(self.figAll)
        toolbar = NavigationToolbar(self.canvasAll, self)

        widFig = QWidget()
        newLayout = QVBoxLayout()
        widFig.setLayout(newLayout)
        newLayout.addWidget(self.canvasAll, 0)
        newLayout.addWidget(toolbar, 0)
        self.layout.addWidget(widFig, 1)


    def imshowCog(self, Ndata, win, nwin, overlap, offset, fmin1=2., fmin2=3., fmax1=20., fmax2=21., ylim=None, vmin=None, vmax=None):
        self.figAll.clear(); ax1 = self.figAll.add_subplot(111)
        ax1.cla()
        
        self.MyProgram.imshowCog(ax1, Ndata, win, nwin, overlap, offset, fmin1, fmin2, fmax1, fmax2, ylim, vmin, vmax)
        self.canvasAll.draw()
        self.update_content()
        print('\n\n')
        print('COG')
        print('\n\n')


    def closeEvent(self, event):
        """重写关闭事件"""
        self.is_closed = True
        print("窗口已关闭")
        event.accept()  # 接受关闭事件，完成窗口关闭
        
    def isVisible(self):
        return self.is_closed
    
    def update_content(self):
        # 获取当前窗口位置
        current_pos = self.pos()

        # 确保窗口位置不变
        self.move(current_pos)
    
    
        
        
        
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = CogMainWindow(das.DAS())
    window.show()
    sys.exit(app.exec())
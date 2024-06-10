


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

class TraceMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.is_closed = False
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
        
        
        self.initFigure1()
        self.initFigure2()
        self.show()


    def initFigure1(self):
        self.fig1 = Figure()
        self.canvas1 = FigureCanvas(self.fig1)
        toolbar = NavigationToolbar(self.canvas1, self)

        widFig = QWidget()
        newLayout = QVBoxLayout()
        widFig.setLayout(newLayout)
        newLayout.addWidget(self.canvas1, 0)
        newLayout.addWidget(toolbar, 0)
        self.layout.addWidget(widFig, 1)
        
    def initFigure2(self):
        self.fig2 = Figure()
        self.canvas2 = FigureCanvas(self.fig2)
        toolbar = NavigationToolbar(self.canvas2, self)

        widFig = QWidget()
        newLayout = QVBoxLayout()
        widFig.setLayout(newLayout)
        newLayout.addWidget(self.canvas2, 0)
        newLayout.addWidget(toolbar, 0)
        self.layout.addWidget(widFig, 2)


    def imshowTrace(self, t, data, xf, yf):
        # self.ax1.cla() 
        with plt.style.context('ggplot'):
            self.fig1.clear()
            self.fig2.clear()
            ax1 = self.fig1.add_subplot(111)
            ax2 = self.fig2.add_subplot(211)
            ax3 = self.fig2.add_subplot(212)
            ax1.cla(); ax2.cla(); ax3.cla()

            ax1.plot(t, data)
            ax1.set_title('Trace')
            ax1.set_xlabel('Time (s)')
            ax1.set_ylabel('Amplitude')
            ax1.grid(True)
            
            ax2.plot(xf, yf)
            ax2.set_title('Spectrum')
            ax2.set_xlabel('Frequency (Hz)')
            ax2.set_ylabel('Amplitude')
            ax2.grid(True)
            
            fs = 1/(t[1]-t[0])
            ax3.specgram(data, Fs=fs, cmap='jet')
            ax3.set_title('Spectrogram')
            ax3.set_xlabel('Time (s)')
            ax3.set_ylabel('Frequency (Hz)')
            ax3.grid(False)
            
            self.fig1.tight_layout()
            self.fig2.tight_layout()
            
            self.canvas1.draw()
        self.update_content()
        print('\n\n')
        print('imshowTrace')
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
    window = TraceMainWindow()
    window.show()
    sys.exit(app.exec())
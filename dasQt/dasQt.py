"""
    * @file: dasQt.py
    * @version: v1.0.0
    * @author: Zhiyu Zhang
    * @desc: GUI for DAS data
    * @date: 2023-07-25 10:08:16
    * @Email: erbiaoger@gmail.com
    * @url: erbiaoger.site

"""

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
from dasQt.CarClass.getPoints import GetPoints
from dasQt.Logging.logPy3 import HandleLog

#import _thread

class OptionWindow(QDialog):
    def __init__(self, moduleName):
        super().__init__()
        self.setWindowTitle("模块选项")
        self.layout = QVBoxLayout()
        self.label = QLabel(f"为 {moduleName} 设置选项")
        self.layout.addWidget(self.label)
        self.setLayout(self.layout)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.logger = HandleLog(os.path.split(__file__)[-1].split(".")[0], path=os.getcwd())

        self.MyProgram = das.DAS()
        self.indexTime = 0
        self.fIndex = 0
        self.tabNum = 0
        self.ms = 100
        self.readNextDataBool = False
        self.rawDataBool = True
        self.filterBool = False
        self.cutDataBool = False
        self.initUI()
        

    def initUI(self):
        # 设置主窗口的位置和大小
        screen = QGuiApplication.primaryScreen()
        width = screen.geometry().width()
        height = screen.geometry().height()
        self.resize(width, height)
        
        # 创建一个主窗口的中心部件
        central_widget = QWidget()
        central_widget.setLayout(QHBoxLayout())
        self.setCentralWidget(central_widget)
        self.layout = central_widget.layout()

        # 设置主窗口的大小策略
        size_policy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setSizePolicy(size_policy)

        # 设置主窗口的标题和图标
        self.setWindowTitle('DAS Show')
        self.setWindowIcon(QIcon('web.png'))
        QToolTip.setFont(QFont('SansSerif', 10))
        self.setToolTip('This is <b>DAS Show</b> GUI')

        fig_TabWidget = QTabWidget()
        fig_TabWidget.tabBarClicked.connect(self.tabBarClicked) 
        self.initFigure(fig_TabWidget)
        self.initWigb(fig_TabWidget)
        self.layout.addWidget(fig_TabWidget, 3)

        # 初始化主窗口的菜单栏、工具栏和状态栏
        

        
        self.initStatusBar()
        self.initMenu()
        #self.inittoggleMenu()
        
        control_TabWidget = QTabWidget()
        # control_TabWidget.tabBarClicked.connect(self.carClassTabBarClicked)
        self.initControl(control_TabWidget)
        self.tabProcess(control_TabWidget)
        self.initcarClass(control_TabWidget)
        
        self.initDispersion(control_TabWidget)
        self.initRadon(control_TabWidget)
        self.layout.addWidget(control_TabWidget, 1)
        
        
        #self.inittoolbar()
        #self.initDialog()

        #self.initData(self.MyProgram)

        #self.imshowData(self.MyProgram)
        #self.wigbShow()
        self.timer = QTimer()
        self.timer.timeout.connect(self.updatePlot)
        self.timerWigb = QTimer()
        self.timerWigb.timeout.connect(self.updateWigb)

        self.show()

    def initFigure(self, fig_TabWidget):

        self.fig = Figure()
        self.canvas = FigureCanvas(self.fig)
        toolbar = NavigationToolbar(self.canvas, self)

        widFig = QWidget()
        newLayout = QVBoxLayout()
        widFig.setLayout(newLayout)
        newLayout.addWidget(self.canvas, 0)
        newLayout.addWidget(toolbar, 0)
        fig_TabWidget.addTab(widFig, "Figure")

    def initWigb(self, fig_TabWidget):

        self.figWigb = Figure()
        self.canvasWigb = FigureCanvas(self.figWigb)
        toolbar = NavigationToolbar(self.canvasWigb, self)

        widFig = QWidget()
        newLayout = QVBoxLayout()
        widFig.setLayout(newLayout)
        newLayout.addWidget(self.canvasWigb, 0)
        newLayout.addWidget(toolbar, 0)
        fig_TabWidget.addTab(widFig, "Wigb")


    def initMenu(self):
        # define a menu bar
        menubar = self.menuBar()
        # First menu
        fileMenu = menubar.addMenu('File')
        EditMenu = menubar.addMenu('Edit')
        ViewMenu = menubar.addMenu('View')
        ToolsMenu = menubar.addMenu('Tools')
        AGCMenu = menubar.addMenu('AGC')
        HelpMenu = menubar.addMenu('Help')

        def act(name, shortcut, tip, func):
            # define a action
            name.setShortcut(shortcut)
            name.setStatusTip(tip)
            name.setCheckable(True)
            name.triggered.connect(func)

        openAct = QAction(QIcon('open.png'), 'Open', self)
        act(openAct, 'Ctrl+O', 'Open new File', \
            lambda: [self.importData(self.MyProgram), self.imshowData(self.MyProgram)])
        
        openFolderAct = QAction(QIcon('open.png'), 'Open Folder', self)
        act(openFolderAct, 'Ctrl+Shift+O', 'Open new Folder', \
            lambda: [self.openFolder()])
        
        # saveAct = QAction(QIcon('save.png'), 'Save', self)
        # act(saveAct, 'Ctrl+S', 'Save File', \
        #     lambda: [self.saveData(MyProgram)])
        
        undoAct = QAction(QIcon('undo.png'), 'Undo', self)
        act(undoAct, 'Ctrl+Z', 'Undo', \
            lambda: [self.MyProgram.undo(), self.imshowData(self.MyProgram)])
        
        redoAct = QAction(QIcon('redo.png'), 'Redo', self)
        act(redoAct, 'Ctrl+R', 'Redo', \
            lambda: [self.MyProgram.redo(), self.imshowData(self.MyProgram)])

        fileMenu.addAction(openAct)
        fileMenu.addAction(openFolderAct)
        # fileMenu.addAction(saveAct)
        EditMenu.addAction(undoAct)
        EditMenu.addAction(redoAct)
    

    def initStatusBar(self):
        self.statusbar = self.statusBar()
        self.statusbar.showMessage('Statusbar')

    def initControl(self, control_TabWidget):
        # Control
        widBtn = QGroupBox("Control", self)
        controlLayout = QVBoxLayout()
        widBtn.setLayout(controlLayout)
        
        self.sliderLabel = QLabel("Speed: 1")
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setMinimum(1)
        self.slider.setMaximum(500)
        self.slider.valueChanged.connect(self.sliderValueChanged)
        
        self.sliderLabelFig = QLabel("Fig color scale: 10")
        self.sliderFig = QSlider(Qt.Orientation.Horizontal)
        self.sliderFig.setMinimum(1)
        self.sliderFig.setMaximum(200)
        self.sliderFig.valueChanged.connect(self.sliderFigChanged)

        # Folder
        self.list_widget = QListWidget(self)
        self.list_widget.itemClicked.connect(self.on_item_clicked)
        widFolder = QGroupBox("Folder", self)
        LayoutFolder = QVBoxLayout()
        LayoutFolder.addWidget(self.list_widget, 1)
        widFolder.setLayout(LayoutFolder)
        controlLayout.addWidget(widFolder, 2)

        # Animation 
        # 创建一个QGroupBox，并设置标题
        widAnimation = QGroupBox("Animation", self)
        grid1 = QGridLayout()
        grid1.setSpacing(10)

        btnStarAnimation = QPushButton('start Animation', self)
        btnStarAnimation.setToolTip('This is a <b>QPushButton</b> widget')
        btnStarAnimation.clicked.connect(lambda: [self.startAnimation(tabNum=self.tabNum)])

        btnStopAnimation = QPushButton('Stop Animation', self)
        btnStopAnimation.setToolTip('This is a <b>QPushButton</b> widget')
        btnStopAnimation.clicked.connect(lambda: [self.stopAnimation()])

        btnNextTime = QPushButton('Next Time', self)
        btnNextTime.setToolTip('This is a <b>QPushButton</b> widget')
        btnNextTime.clicked.connect(lambda: [self.nextTime()])

        btnPrevTime = QPushButton('Prev Time', self)
        btnPrevTime.setToolTip('This is a <b>QPushButton</b> widget')
        btnPrevTime.clicked.connect(lambda: [self.prevTime()])


        grid1.addWidget(btnStarAnimation, 1, 0)
        grid1.addWidget(btnStopAnimation, 1, 1)
        grid1.addWidget(btnNextTime, 2, 0)
        grid1.addWidget(btnPrevTime, 2, 1)
        grid1.addWidget(self.sliderLabel, 3, 0)
        grid1.addWidget(self.slider, 3, 1)
        widAnimation.setLayout(grid1)
        controlLayout.addWidget(widAnimation, 0)

        # TODO: Filter
        # Filter
        # labFmin = QLabel('fmin', self)
        # labFmax = QLabel('fmax', self)
        # editFmin = QLineEdit('2', self)
        # editFmax = QLineEdit('30', self)
        # btnBandpass = QPushButton('Bandpass', self)
        # btnBandpass.setToolTip('This is a <b>QPushButton</b> widget')
        # btnBandpass.clicked.connect(
        #     lambda: [self.filter(editFmin.text(), editFmax.text())])
        # btnRawData = QPushButton('Raw Data', self)
        # btnRawData.setToolTip('This is a <b>QPushButton</b> widget')
        # btnRawData.clicked.connect(
        #     lambda: [self.rawData()])
        
        # # labDownSampling = QLabel('Down Sampling', self) 
        # intNumDownSampling = QLineEdit('10', self)
        # btnDownSampling = QPushButton('Down Sampling', self)
        # btnDownSampling.setToolTip('This is a <b>QPushButton</b> widget')
        # btnDownSampling.clicked.connect(
        #     lambda: [self.downSampling(intNumDownSampling=int(intNumDownSampling.text()))])
        # gridDownSampling = QGridLayout()
        # gridDownSampling.setSpacing(10)
        # # gridDownSampling.addWidget(labDownSampling, 1, 0)
        # gridDownSampling.addWidget(intNumDownSampling, 1, 0)
        # gridDownSampling.addWidget(btnDownSampling, 1, 1)
        # widDownSampling = QGroupBox(self)
        # widDownSampling.setLayout(gridDownSampling)


        # grid2 = QGridLayout()
        # grid2.setSpacing(10)
        # grid2.addWidget(labFmin, 1, 0)
        # grid2.addWidget(editFmin, 1, 1)
        # grid2.addWidget(labFmax, 2, 0)
        # grid2.addWidget(editFmax, 2, 1)
        # widFs = QGroupBox(self)
        # widFs.setLayout(grid2)

        # widFilter = QGroupBox("Filter", self)
        # LayoutFilter = QVBoxLayout()
        # LayoutFilter.addWidget(widFs, 0)
        # LayoutFilter.addWidget(btnBandpass, 1)
        # LayoutFilter.addWidget(btnRawData, 2)
        # LayoutFilter.addWidget(widDownSampling, 3)
        # widFilter.setLayout(LayoutFilter)
        # controlLayout.addWidget(widFilter, 0)


        # Fig
        widFig = QGroupBox("Fig", self)
        LayoutFig = QVBoxLayout()

        speedFig = QWidget()
        LayoutSpeed = QHBoxLayout()
        LayoutSpeed.addWidget(self.sliderLabelFig, 0)
        LayoutSpeed.addWidget(self.sliderFig, 0)
        speedFig.setLayout(LayoutSpeed)
        LayoutFig.addWidget(speedFig, 0)

        labXmin = QLabel('Xmin', self)
        labXmax = QLabel('Xmax', self)
        editXmin = QLineEdit('40', self)
        editXmax = QLineEdit('50', self)

        grid3 = QGridLayout()
        grid3.setSpacing(10)
        grid3.addWidget(labXmin, 1, 0)
        grid3.addWidget(editXmin, 1, 1)
        grid3.addWidget(labXmax, 2, 0)
        grid3.addWidget(editXmax, 2, 1)
        widCut = QGroupBox(self)
        widCut.setLayout(grid3)
        LayoutFig.addWidget(widCut, 0)


        btnCut = QPushButton('Cut', self)
        btnCut.setToolTip('This is a <b>QPushButton</b> widget')
        btnCut.clicked.connect(
            lambda: [self.cutData(editXmin.text(), editXmax.text())])
        LayoutFig.addWidget(btnCut, 1)

        widFig.setLayout(LayoutFig)
        controlLayout.addWidget(widFig, 0)

        btnNextData = QPushButton('Next Data', self)
        btnNextData.setToolTip('This is a <b>QPushButton</b> widget')
        btnNextData.clicked.connect(
            lambda: [self.readNextData(), self.imshowData(self.MyProgram)])
        controlLayout.addWidget(btnNextData, 2)
        
        btnPickPoint = QPushButton('Pick Point', self)
        btnPickPoint.setToolTip('This is a <b>QPushButton</b> widget')
        btnPickPoint.clicked.connect(
            lambda: [self.getPoints()])
        controlLayout.addWidget(btnPickPoint, 2)


        control_TabWidget.addTab(widBtn, "Control")



    def tabProcess(self, TabWidget):
        
        widProcess = QGroupBox("Process", self)
        processLayout = QVBoxLayout()
        widProcess.setLayout(processLayout)
        
        # 创建两个列表控件
        self.availableModulesList = QListWidget()
        self.selectedModulesList = QListWidget()

        # 添加一些示例模块到可用模块列表
        self.availableModulesList.addItems(["Cut",
                                            "DownSampling",
                                            "Filter",
                                            "Module1",
                                            ])

        # 创建添加按钮
        self.addButton = QPushButton("Add to selected")
        self.addButton.clicked.connect(self.addModule)

        # 创建布局并添加控件
        layout = QVBoxLayout()
        layout.addWidget(self.availableModulesList)
        layout.addWidget(self.addButton)
        layout.addWidget(self.selectedModulesList)
        widList = QGroupBox("List", self)
        widList.setLayout(layout)
        processLayout.addWidget(widList, 0)
        
        TabWidget.addTab(widProcess, "Process")
        
        # 为选中模块列表添加点击事件
        self.selectedModulesList.itemClicked.connect(self.showOptionWindow)



    def initcarClass(self, TabWidget):
        widBtn = QGroupBox("Car Class", self)
        carClassLayout = QVBoxLayout()
        widBtn.setLayout(carClassLayout)
        
        
        # Pick Point
        widPickPoint = QGroupBox("Pick Point", self)
        LayoutPickPoint = QVBoxLayout()

        labThreshold = QLabel('threshold', self)
        labSkipNch = QLabel('skip_Nch', self)
        labSkipNt = QLabel('skip_Nt', self)
        labMode         = QLabel('Mode', self)  
        self.editThreshold = QLineEdit('0.08', self)
        self.editSkipNch = QLineEdit('1', self)
        self.editSkipNt = QLineEdit('200', self)
        self.editMode        = QLineEdit('max', self)

        grid3 = QGridLayout()
        grid3.setSpacing(10)
        grid3.addWidget(labThreshold, 1, 0)
        grid3.addWidget(self.editThreshold, 1, 1)
        grid3.addWidget(labSkipNch, 2, 0)
        grid3.addWidget(self.editSkipNch, 2, 1)
        grid3.addWidget(labSkipNt, 3, 0)
        grid3.addWidget(self.editSkipNt, 3, 1)
        grid3.addWidget(labMode, 4, 0)
        grid3.addWidget(self.editMode, 4, 1)
        
        widCut = QGroupBox(self)
        widCut.setLayout(grid3)
        LayoutPickPoint.addWidget(widCut, 0)
        
        # Auto Separation
        widSeparation = QGroupBox("Auto Separation", self)
        LayoutSeparation = QVBoxLayout()
        
        labMaxMode      = QLabel('MaxMode', self)
        labMinCarNum    = QLabel('MinCarNum', self)
        labTo           = QLabel('to', self)
        labLine         = QLabel('line', self)
        self.editMaxMode     = QLineEdit('10', self)
        self.editMinCarNum   = QLineEdit('15', self)
        self.editTo          = QLineEdit('0.05', self)
        self.editLine        = QLineEdit('0.65', self)

        grid3 = QGridLayout()
        grid3.setSpacing(10)
        grid3.addWidget(labMaxMode, 1, 0)
        grid3.addWidget(self.editMaxMode, 1, 1)
        grid3.addWidget(labMinCarNum, 2, 0)
        grid3.addWidget(self.editMinCarNum, 2, 1)
        grid3.addWidget(labTo, 3, 0)
        grid3.addWidget(self.editTo, 3, 1)
        grid3.addWidget(labLine, 4, 0)
        grid3.addWidget(self.editLine, 4, 1)
        
        # widSeparation = QGroupBox(self)
        widSeparation.setLayout(grid3)
        LayoutPickPoint.addWidget(widSeparation, 0)

        widPickPoint.setLayout(LayoutPickPoint)
        
        btnNextData = QPushButton('Next Data', self)
        btnNextData.setToolTip('This is a <b>QPushButton</b> widget')
        btnNextData.clicked.connect(
            lambda: [self.readNextData(), self.imshowCarClass(self.MyProgram)])

        btnCarClass = QPushButton('Car Class', self)
        btnCarClass.setToolTip('This is a <b>QPushButton</b> widget')
        btnCarClass.clicked.connect(
            lambda: [self.imshowCarClass(self.MyProgram)])
        

        
        carClassLayout.addWidget(widPickPoint, 0)
        carClassLayout.addWidget(btnNextData, 2)
        carClassLayout.addWidget(btnCarClass, 2)

        TabWidget.addTab(widBtn, "Car Class")
        
        

    def initDispersion(self, TabWidget):
        widBtn = QGroupBox("Dispersion", self)
        dispersionLayout = QVBoxLayout()
        widBtn.setLayout(dispersionLayout)

        labFmin = QLabel('fmin', self)
        labFmax = QLabel('fmax', self)
        labSmooth_N = QLabel('smooth_N', self)
        labSmoothspect_N = QLabel('smoothspect_N', self)
        labMaxlag = QLabel('maxlag', self)
        labCC_len = QLabel('CC_len', self)
        labCh1 = QLabel('Ch1', self)
        labCh2 = QLabel('Ch2', self)
        
        
        self.editFmin = QLineEdit('1', self)
        self.editFmax = QLineEdit('30', self)
        self.editSmooth_N = QLineEdit('5', self)
        self.editSmoothspect_N = QLineEdit('5', self)
        self.editMaxlag = QLineEdit('0.2', self)
        self.editCC_len = QLineEdit('5', self)
        self.editCh1 = QLineEdit('41', self)
        self.editCh2 = QLineEdit('90', self)
        

        grid1 = QGridLayout()
        grid1.setSpacing(10)
        grid1.addWidget(labFmin, 1, 0)
        grid1.addWidget(self.editFmin, 1, 1)
        grid1.addWidget(labFmax, 2, 0)
        grid1.addWidget(self.editFmax, 2, 1)

        grid2 = QGridLayout()
        grid2.setSpacing(10)
        grid2.addWidget(labSmooth_N, 1, 0)
        grid2.addWidget(self.editSmooth_N, 1, 1)
        grid2.addWidget(labSmoothspect_N, 2, 0)
        grid2.addWidget(self.editSmoothspect_N, 2, 1)
        grid2.addWidget(labMaxlag, 3, 0)
        grid2.addWidget(self.editMaxlag, 3, 1)
        
        grid3 = QGridLayout()
        grid3.setSpacing(10)
        grid3.addWidget(labCC_len, 1, 0)
        grid3.addWidget(self.editCC_len, 1, 1)
        grid3.addWidget(labCh1, 2, 0)
        grid3.addWidget(self.editCh1, 2, 1)
        grid3.addWidget(labCh2, 3, 0)
        grid3.addWidget(self.editCh2, 3, 1)
        
        
        
        widFilter = QGroupBox("Filter", self)
        widFilter.setLayout(grid1)
        dispersionLayout.addWidget(widFilter, 0)
        
        widSmooth = QGroupBox("Smooth", self)
        widSmooth.setLayout(grid2)
        dispersionLayout.addWidget(widSmooth, 0)
        
        widCC = QGroupBox("CC", self)
        widCC.setLayout(grid3)
        dispersionLayout.addWidget(widCC, 0)

        btnNextData = QPushButton('Next Data', self)
        btnNextData.setToolTip('This is a <b>QPushButton</b> widget')
        btnNextData.clicked.connect(
            lambda: [self.readNextData(), self.imshowDispersion(self.MyProgram)])

        btnCarClass = QPushButton('Get Dispersion', self)
        btnCarClass.setToolTip('This is a <b>QPushButton</b> widget')
        btnCarClass.clicked.connect(
            lambda: [self.imshowDispersion(self.MyProgram)])

        dispersionLayout.addWidget(btnNextData, 2)
        dispersionLayout.addWidget(btnCarClass, 2)
        widBtn.setLayout(dispersionLayout)

        TabWidget.addTab(widBtn, "Dispersion")
        
    def initRadon(self, TabWidget):
        widBtn = QGroupBox("Radon", self)
        dispersionLayout = QVBoxLayout()
        widBtn.setLayout(dispersionLayout)

        labFminRadon = QLabel('fmin', self)
        labFminRadon1= QLabel('fmin1', self)
        labFmaxRadon = QLabel('fmax', self)
        labFmaxRadon1 = QLabel('fmax1', self)
        labVmaxRadon = QLabel('Vmax', self)
        labVminRadon = QLabel('Vmin', self)
        labDvRadon = QLabel('dv', self)
        labDfRadon = QLabel('df', self)

        labCh1Radon = QLabel('Ch1', self)
        labCh2Radon = QLabel('Ch2', self)
        
        
        self.editFminRadon = QLineEdit('0.01', self)
        self.editFminRadon1 = QLineEdit('0.1', self)
        self.editFmaxRadon = QLineEdit('1.0', self)
        self.editFmaxRadon1 = QLineEdit('2.0', self)
        self.editVmaxRadon = QLineEdit('15', self)
        self.editVminRadon = QLineEdit('-15', self)
        self.editDvRadon = QLineEdit('0.1', self)
        self.editDfRadon = QLineEdit('0.01', self)

        self.editCh1Radon = QLineEdit('30', self)
        self.editCh2Radon = QLineEdit('90', self)


        grid1 = QGridLayout()
        grid1.setSpacing(10)
        grid1.addWidget(labFminRadon, 1, 0)
        grid1.addWidget(self.editFminRadon, 1, 1)
        grid1.addWidget(labFminRadon1, 2, 0)
        grid1.addWidget(self.editFminRadon1, 2, 1)
        grid1.addWidget(labFmaxRadon, 3, 0)
        grid1.addWidget(self.editFmaxRadon, 3, 1)
        grid1.addWidget(labFmaxRadon1, 4, 0)
        grid1.addWidget(self.editFmaxRadon1, 4, 1)
        
        btnBPFilter = QPushButton('BPFilter', self)
        btnBPFilter.setToolTip('This is a <b>QPushButton</b> widget')
        btnBPFilter.clicked.connect(
            lambda: [self.bp_filter()])


        grid2 = QGridLayout()
        grid2.setSpacing(10)
        grid2.addWidget(labVminRadon, 1, 0)
        grid2.addWidget(self.editVminRadon, 1, 1)
        grid2.addWidget(labVmaxRadon, 2, 0)
        grid2.addWidget(self.editVmaxRadon, 2, 1)
        grid2.addWidget(labDvRadon, 3, 0)
        grid2.addWidget(self.editDvRadon, 3, 1)
        grid2.addWidget(labDfRadon, 4, 0)
        grid2.addWidget(self.editDfRadon, 4, 1)
        
        
        btnNormalTrace = QPushButton('NormalTrace', self)
        btnNormalTrace.setToolTip('This is a <b>QPushButton</b> widget')
        btnNormalTrace.clicked.connect(
            lambda: [self.norm_trace()])
        
        grid3 = QGridLayout()
        grid3.setSpacing(10)
        grid3.addWidget(labCh1Radon, 1, 0)
        grid3.addWidget(self.editCh1Radon, 1, 1)
        grid3.addWidget(labCh2Radon, 2, 0)
        grid3.addWidget(self.editCh2Radon, 2, 1)

        
        widFilter = QGroupBox("Filter", self)
        widFilter.setLayout(grid1)
        dispersionLayout.addWidget(widFilter, 0)
        dispersionLayout.addWidget(btnBPFilter, 1)
        
        widSmooth = QGroupBox("Radon", self)
        widSmooth.setLayout(grid2)
        dispersionLayout.addWidget(widSmooth, 0)
        dispersionLayout.addWidget(btnNormalTrace, 1)
        
        widCC = QGroupBox("Channel", self)
        widCC.setLayout(grid3)
        dispersionLayout.addWidget(widCC, 0)

        btnNextData = QPushButton('Next Data', self)
        btnNextData.setToolTip('This is a <b>QPushButton</b> widget')
        btnNextData.clicked.connect(
            lambda: [self.readNextData(), 
                     self.bp_filter(), 
                     self.norm_trace(), 
                     self.imshowRadon(self.MyProgram)])

        btnRadon = QPushButton('Radon', self)
        btnRadon.setToolTip('This is a <b>QPushButton</b> widget')
        btnRadon.clicked.connect(
            lambda: [self.imshowRadon(self.MyProgram)])

        btnAllRadon = QPushButton('All Radon', self)
        btnAllRadon.setToolTip('This is a <b>QPushButton</b> widget')
        btnAllRadon.clicked.connect(
            lambda: [self.bp_filter(), self.norm_trace(), self.imshowRadon(self.MyProgram)])


        dispersionLayout.addWidget(btnNextData, 2)
        dispersionLayout.addWidget(btnRadon, 2)
        dispersionLayout.addWidget(btnAllRadon, 2)
        widBtn.setLayout(dispersionLayout)

        TabWidget.addTab(widBtn, "Radon")

    def on_item_clicked(self, item):
        self.MyProgram.getFileID(item.text())

        self.indexTime = 0

        try:
            self.MyProgram.readData(os.path.join(self.folderName, item.text()))
        except Exception as e:
            self.logger.error(e)
            self.statusbar.showMessage('Error: '+str(e))
            return
        self.fig.clear(); ax1 = self.fig.add_subplot(111)
        
        ax1 = self.MyProgram.imshowData(ax1, indexTime=self.indexTime, scale=self.sliderFig.value())
        self.canvas.draw()

    # TODO: filter
    def addModule(self):
        # 获取当前选中的模块项
        selectedItem = self.availableModulesList.currentItem()

        # 如果有选中的项，则添加到选中模块列表
        if selectedItem:
            self.selectedModulesList.addItem(selectedItem.text())

    def showOptionWindow(self, item):
        # 当点击选中的模块时，显示选项窗口
        optionWindow = OptionWindow(item.text())
        optionWindow.exec()


    def sliderValueChanged(self, value):
        """
        Set speed of animation, help function of sliderSpeed
        """
        self.sliderLabel.setText(f"Speed: {value}")
        self.startAnimation(tabNum=self.tabNum)

    def sliderFigChanged(self, value):
        """
        Set speed of animation, help function of sliderSpeed
        """
        self.sliderLabelFig.setText(f"Fig color scale: {value}")
        self.fig.clear(); ax1 = self.fig.add_subplot(111)
        ax1 = self.MyProgram.imshowData(ax1, indexTime=self.indexTime, scale=value)
        self.canvas.draw()

    def sliderThresholdChanged(self, value):
        """
        Set speed of animation, help function of sliderSpeed
        """
        self.sliderLabelThreshold.setText(f"threshold: {value/100.}")
        self.MyProgram.threshold = value / 100.
        # self.fig.clear(); ax1 = self.fig.add_subplot(111)
        # ax1 = self.MyProgram.imshowData(ax1, indexTime=self.indexTime, scale=value)
        # self.canvas.draw()


    # def wheelEvent(self, event):
    #     delta = event.angleDelta().y()  # 获取滚轮滚动的距离
    #     print(delta)
    #     if delta > 0:
    #         self.statusbar.showMessage('Scroll Up')
    #         self.prevTime()
    #     elif delta < 0:
    #         self.statusbar.showMessage('Scroll Down')
    #         self.nextTime()

    def tabBarClicked(self, index):
        if index == 0:
            self.timerWigb.stop()
            self.timer.start(self.ms)
            self.tabNum = 0
        elif index == 1:
            self.timer.stop()
            self.timerWigb.start(self.ms)
            self.tabNum = 1

    def carClassTabBarClicked(self, index):
        if index == 0:
            self.initControl
        elif index == 1:
            self.initControl


    def importData(self, MyProgram):
        
        filetypes = 'All (*.mat *.h5 *.dat);;HDF5 (*.h5)'
        fname, _ = QFileDialog.getOpenFileName(self, 'Open file', '.', filetypes)

        self.logger.info('Importing data from ' + fname)
        self.statusbar.showMessage('Importing data from ' + fname)
        MyProgram.readData(fname)
        self.statusbar.showMessage('Data imported! Data shape: '+str(MyProgram.data.shape))


    def openFolder(self):

        folderName = QFileDialog.getExistingDirectory(self, "Select Directory", "./")
        self.folderName = folderName


        emptyFolderName = ''
        if folderName == emptyFolderName:
            # 创建并显示消息框
            QMessageBox.warning(self, "Message", "Folder is empty! Please select again.")
            self.logger.error('No folder selected!')
            self.openFolder()
            # return
        else:
            self.statusbar.showMessage('Importing data from ' + folderName)
            files = self.MyProgram.openFolder(folderName)
            self.statusbar.showMessage('Folder imported!')

            self.list_widget.clear()
            files = sorted(files)
            for file in files:
                self.list_widget.addItem(file)

    def readNextData(self):
        self.readNextDataBool = True
        #_thread.start_new_thread(self.readNextData, ())
        try:
            self.MyProgram.readNextData()
        except Exception as e:
            self.logger.error(e)
            self.statusbar.showMessage('Error: '+str(e))
            QMessageBox.warning(self, "Message", "No more data!")
            return
        if self.filterBool:
            self.MyProgram.bandpassData(self.fmin, self.fmax)
        if self.cutDataBool:
            self.MyProgram.cutData(self.Xmin, self.Xmax)

        self.indexTime = 0
        self.fIndex += 1

    def initData(self, MyProgram):
        fname = './Data/SR_2023-07-20_09-09-38_UTC.h5'
        MyProgram.readData(fname)
        self.statusbar.showMessage('Data imported')

    def imshowData(self, MyProgram):
        """
        Display data in a figure
        """
        self.indexTime = 0
        self.fig.clear(); ax1 = self.fig.add_subplot(111)
        ax1 = self.MyProgram.imshowData(ax1, indexTime=self.indexTime, scale=self.sliderFig.value())
        self.indexTime += int(self.slider.value())
        self.canvas.draw()

        # self.ax1 = ax1
        self.timer = QTimer()
        self.timer.timeout.connect(self.updatePlot)
        self.timer.start(self.ms)

        return self.fig, ax1
    
    def imshowCarClass(self, MyProgram):
        """
        Display data in a figure
        """
        self.MyProgram.threshold = float(self.editThreshold.text())
        self.MyProgram.skip_Nch = int(self.editSkipNch.text())
        self.MyProgram.skip_Nt = int(self.editSkipNt.text())
        self.MyProgram.maxMode = int(self.editMaxMode.text())
        self.MyProgram.minCarNum = int(self.editMinCarNum.text())
        self.MyProgram.to = float(self.editTo.text())
        self.MyProgram.mode = self.editMode.text()
        self.MyProgram.line = float(self.editLine.text())
        self.indexTime = 0
        
        self.fig.clear(); ax1 = self.fig.add_subplot(121); ax2 = self.fig.add_subplot(122)
        ax1 = self.MyProgram.imshowData(ax1, indexTime=self.indexTime, scale=self.sliderFig.value())
        self.indexTime += int(self.slider.value())
        self.canvas.draw()

        ax2 = self.MyProgram.imshowCarClass(ax2, indexTime=self.indexTime, scale=self.sliderFig.value())
        
        self.ax1 = ax1
        self.timer = QTimer()
        self.timer.timeout.connect(self.updateCarClass)
        self.timer.start(self.ms)

        return self.fig, ax1

    def imshowDispersion(self, MyProgram):
        
        # self.MyProgram.dispersion_parse['fmin'] = float(self.editFmin.text())
        # self.MyProgram.dispersion_parse['fmax'] = float(self.editFmax.text())
        # self.MyProgram.dispersion_parse['smooth_N'] = int(self.editSmooth_N.text())
        # self.MyProgram.dispersion_parse['smoothspect_N'] = int(self.editSmoothspect_N.text())
        # self.MyProgram.dispersion_parse['maxlag'] = float(self.editMaxlag.text())
        # self.MyProgram.dispersion_parse['CC_len'] = int(self.editCC_len.text())
        # self.MyProgram.dispersion_parse['cha1'] = int(self.editCh1.text())
        # self.MyProgram.dispersion_parse['cha2'] = int(self.editCh2.text())

        dispersion_parse = {
            'sps'           : 1/self.MyProgram.dt,    # current sampling rate
            'samp_freq'     : 1/self.MyProgram.dt,    # targeted sampling rate
            'freqmin'       : float(self.editFmin.text()),          # pre filtering frequency bandwidth预滤波频率带宽
            'freqmax'       : float(self.editFmax.text()),           # note this cannot exceed Nquist freq
            'freq_norm'     : 'rma',        # 'no' for no whitening, or 'rma' for running-mean average, 'phase_only' for sign-bit normalization in freq domain.
            'time_norm'     : 'one_bit',    # 'no' for no normalization, or 'rma', 'one_bit' for normalization in time domain
            'cc_method'     : 'xcorr',      # 'xcorr' for pure cross correlation, 'deconv' for deconvolution;
            'smooth_N'      : int(self.editSmooth_N.text()),            # moving window length for time domain normalization if selected (points)
            'smoothspect_N' : int(self.editSmoothspect_N.text()),            # moving window length to smooth spectrum amplitude (points)
            'maxlag'        : float(self.editMaxlag.text()),          # lags of cross-correlation to save (sec)
            'max_over_std'  : 10**9,        # threahold to remove window of bad signals: set it to 10*9 if prefer not to remove them
            'cc_len'        : int(self.editCC_len.text()),            # correlate length in second(sec)
            'cha1'          : int(self.editCh1.text()),           # start channel index for the sub-array
            'cha2'          : int(self.editCh2.text()),           # end channel index for the sub-array
        }


        self.fig.clear(); ax1 = self.fig.add_subplot(121); ax2 = self.fig.add_subplot(122)
        ax1 = self.MyProgram.imshowData(ax1, indexTime=self.indexTime, scale=self.sliderFig.value())
        self.indexTime += int(self.slider.value())
        self.canvas.draw()
        
        ax2 = self.MyProgram.imshowDispersion(self.fig, ax2, 
                                              dispersion_parse=dispersion_parse, 
                                              indexTime=self.fIndex, 
                                              scale=self.sliderFig.value())
        
        self.ax1 = ax1
        self.timer = QTimer()
        self.timer.timeout.connect(self.updateCarClass)
        self.timer.start(self.ms)
        
    def imshowRadon(self, MyProgram):
        
        radon_parse = {
            'fmin': float(self.editFminRadon.text()),
            'fmin1': float(self.editFminRadon1.text()),
            'fmax': float(self.editFmaxRadon.text()),
            'fmax1': float(self.editFmaxRadon1.text()),
            'Vmax': float(self.editVmaxRadon.text()),
            'Vmin': float(self.editVminRadon.text()),
            'dv': float(self.editDvRadon.text()),
            'df': float(self.editDfRadon.text()),
            'cha1': int(self.editCh1Radon.text()),
            'cha2': int(self.editCh2Radon.text()),
        }
        self.MyProgram.radon_parse = radon_parse
        
        self.fig.clear(); ax1 = self.fig.add_subplot(121); ax2 = self.fig.add_subplot(122)
        ax1 = self.MyProgram.imshowData(ax1, indexTime=self.indexTime, scale=self.sliderFig.value())
        self.indexTime += int(self.slider.value())
        self.canvas.draw()
        
        ax2 = self.MyProgram.imshowRadon(ax2, indexTime=self.indexTime, scale=self.sliderFig.value())
        
        self.ax1 = ax1
        self.timer = QTimer()
        self.timer.timeout.connect(self.updateRadon)
        self.timer.start(self.ms)

    def updatePlot(self):
        """
        Update plot, help function of imshowAllData
        """
        self.fig.clear(); ax1 = self.fig.add_subplot(111) 
        # ax1 = self.ax1
        # ax1.cla()
        ax1 = self.MyProgram.imshowData(ax1, indexTime=self.indexTime, scale=self.sliderFig.value())
        self.canvas.draw()

        display_nt = self.MyProgram.display_nt
        nt = self.MyProgram.nt
        self.indexTime += int(self.slider.value())
        if self.indexTime >= nt - display_nt:
            self.stopAnimation()

            if self.readNextDataBool:
                self.readNextData()
                self.imshowData(self.MyProgram)
            else:
                pass
            
    def updateCarClass(self):
        """
        Update plot, help function of imshowAllData
        """
        ax1 = self.ax1
        ax1.cla()
        # ax1 = self.fig.add_subplot(121) 
        ax1 = self.MyProgram.imshowData(ax1, indexTime=self.indexTime, scale=self.sliderFig.value())
        self.canvas.draw()

        display_nt = self.MyProgram.display_nt
        nt = self.MyProgram.nt
        self.indexTime += int(self.slider.value())
        if self.indexTime >= nt - display_nt:
            self.stopAnimation()

            if self.readNextDataBool:
                self.readNextData()
                self.imshowData(self.MyProgram)
            else:
                pass

    def updateRadon(self):
        """
        Update plot, help function of imshowAllData
        """
        ax1 = self.ax1
        ax1.cla()
        # ax1 = self.fig.add_subplot(121) 
        ax1 = self.MyProgram.imshowData(ax1, indexTime=self.indexTime, scale=self.sliderFig.value())
        self.canvas.draw()

        display_nt = self.MyProgram.display_nt
        nt = self.MyProgram.nt
        self.indexTime += int(self.slider.value())
        if self.indexTime >= nt - display_nt:
            self.stopAnimation()

            if self.readNextDataBool:
                self.readNextData()
                self.imshowData(self.MyProgram)
            else:
                pass

    def wigbShow(self):
        """
        Display data in a figure
        """
        self.figWigb.clear(); ax1 = self.figWigb.add_subplot(111)
        ax1 = self.MyProgram.wigb(ax1, indexTime=self.indexTime, scale=self.sliderFig.value())
        self.canvasWigb.draw()

        self.timerWigb = QTimer()
        self.timerWigb.timeout.connect(self.updateWigb)
        #self.timer.stop()
        #self.timerWigb.start(self.ms)
        return self.figWigb, ax1
    
    def updateWigb(self):
        """
        Update plot, help function of imshowAllData
        """
        self.figWigb.clear(); ax1 = self.figWigb.add_subplot(111)
        ax1 = self.MyProgram.wigb(ax1, indexTime=self.indexTime, scale=self.sliderFig.value())
        self.canvasWigb.draw()

        display_nt = self.MyProgram.display_nt
        nt = self.MyProgram.nt
        self.indexTime += int(self.slider.value())
        if self.indexTime >= nt - display_nt:
            self.stopAnimation()


    def startAnimation(self, tabNum=0):
        """
        Start animation, help function of imshowAllData
        """
        if tabNum == 0:
            self.timer.start(self.ms)
        elif tabNum == 1:
            self.timerWigb.start(self.ms)

    def stopAnimation(self):
        """
        Stop animation, help function of imshowAllData
        """
        self.timer.stop()
        self.timerWigb.stop()

    def nextTime(self):
        #self.basePlot()
        self.indexTime += int(self.slider.value())
        if self.tabNum == 0:
            self.fig.clear(); ax1 = self.fig.add_subplot(111)
            ax1 = self.MyProgram.imshowData(ax1, indexTime=self.indexTime, scale=self.sliderFig.value())
            self.canvas.draw()
        elif self.tabNum == 1:
            self.figWigb.clear(); ax1 = self.figWigb.add_subplot(111)
            ax1 = self.MyProgram.wigb(ax1, indexTime=self.indexTime, scale=self.sliderFig.value())
            self.canvasWigb.draw()

        

    def prevTime(self):
        self.indexTime -= int(self.slider.value())
        if self.tabNum == 0:
            self.fig.clear(); ax1 = self.fig.add_subplot(111)
            ax1 = self.MyProgram.imshowData(ax1, indexTime=self.indexTime, scale=self.sliderFig.value())
            self.canvas.draw()
        elif self.tabNum == 1:
            self.figWigb.clear(); ax1 = self.figWigb.add_subplot(111)
            ax1 = self.MyProgram.wigb(ax1, indexTime=self.indexTime, scale=self.sliderFig.value())
            self.canvasWigb.draw()

    def filter(self, editFmin, editFmax):
        self.filterBool = True
        self.fmin = float(editFmin); self.fmax = float(editFmax)
        # self.MyProgram.bandpassData(
        #     float(editFmin), float(editFmax))
        
        self.MyProgram.RawDataBpFilter(self.fmin, self.fmax)
        
    def rawData(self):
        self.filterBool = False
        self.cutDataBool = False
        self.data = self.MyProgram.rawData()
        self.fig.clear(); ax1 = self.fig.add_subplot(111)
        ax1 = self.MyProgram.imshowData(ax1, indexTime=self.indexTime, scale=self.sliderFig.value())
        self.canvas.draw()

    def downSampling(self, intNumDownSampling=2):
        self.MyProgram.downSampling(intNumDownSampling=intNumDownSampling)
        self.fig.clear(); ax1 = self.fig.add_subplot(111)
        ax1 = self.MyProgram.imshowData(ax1, indexTime=self.indexTime, scale=self.sliderFig.value())
        self.canvas.draw()

    def cutData(self, Xmin, Xmax):
        self.cutDataBool = True
        self.MyProgram.cutData(Xmin, Xmax)
        self.Xmin = Xmin; self.Xmax = Xmax

        self.fig.clear(); ax1 = self.fig.add_subplot(111)
        ax1 = self.MyProgram.imshowData(ax1, indexTime=self.indexTime, scale=self.sliderFig.value())
        self.canvas.draw()

        self.fig.clear(); ax1 = self.fig.add_subplot(111)
        ax1 = self.MyProgram.wigb(ax1, indexTime=self.indexTime, scale=self.sliderFig.value())
        self.canvas.draw()

    def getPoints(self):
        self.getPoints = GetPoints()
        self.getPoints.show()
    
    # TODO: 
    def bp_filter(self):
        radon_parse = {
            'fmin': float(self.editFminRadon.text()),
            'fmin1': float(self.editFminRadon1.text()),
            'fmax': float(self.editFmaxRadon.text()),
            'fmax1': float(self.editFmaxRadon1.text()),
            'Vmax': float(self.editVmaxRadon.text()),
            'Vmin': float(self.editVminRadon.text()),
            'dv': float(self.editDvRadon.text()),
            'df': float(self.editDfRadon.text()),
            'cha1': int(self.editCh1Radon.text()),
            'cha2': int(self.editCh2Radon.text()),
        }
        self.MyProgram.radon_parse = radon_parse
        self.MyProgram.bp_filter()

        
    def norm_trace(self):
        radon_parse = {
            'fmin': float(self.editFminRadon.text()),
            'fmin1': float(self.editFminRadon1.text()),
            'fmax': float(self.editFmaxRadon.text()),
            'fmax1': float(self.editFmaxRadon1.text()),
            'Vmax': float(self.editVmaxRadon.text()),
            'Vmin': float(self.editVminRadon.text()),
            'dv': float(self.editDvRadon.text()),
            'df': float(self.editDfRadon.text()),
            'cha1': int(self.editCh1Radon.text()),
            'cha2': int(self.editCh2Radon.text()),
        }
        self.MyProgram.radon_parse = radon_parse
        self.MyProgram.norm_trace()

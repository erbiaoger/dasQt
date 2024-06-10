import sys
import numpy as np
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QPushButton, QWidget
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class PlotCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        FigureCanvas.__init__(self, fig)
        self.setParent(parent)
        self.edit_mode = False
        self.click_points = []

    def plot(self, data):
        self.axes.imshow(data, origin='lower')
        self.draw()

    def enter_edit_mode(self):
        self.edit_mode = True
        self.click_points = []  # 清空之前的点击点
        self.mpl_connect('button_press_event', self.on_click)

    def on_click(self, event):
        if self.edit_mode and event.inaxes == self.axes:
            # 记录点击的点
            self.click_points.append((int(event.xdata), int(event.ydata)))
            if len(self.click_points) == 2:
                self.edit_mode = False  # 退出编辑模式
                self.draw_line_and_refill()

    def draw_line_and_refill(self):
        # 绘制线并填充
        x = [p[0] for p in self.click_points]
        y = [p[1] for p in self.click_points]
        self.axes.plot(x, y, color='red')
        # 填充逻辑（此处需要自己实现根据具体需求）
        # 例如，self.data 是您的二维数据数组
        # 更新 self.data 以将连线下部的数据重新填充为0
        self.draw()
        self.click_points = []  # 重置点击点

class App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.left = 10
        self.top = 10
        self.title = 'PyQt6 & Matplotlib Demo'
        self.width = 640
        self.height = 400
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        # 创建一个 matplotlib 图表画布
        self.canvas = PlotCanvas(self, width=5, height=4)
        self.canvas.plot(np.random.rand(10,10))  # 示例数据

        # 创建按钮
        edit_button = QPushButton('Edit Mode', self)
        edit_button.clicked.connect(self.canvas.enter_edit_mode)

        # 设置布局
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        layout.addWidget(edit_button)

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

        self.show()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec())

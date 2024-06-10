import sys
import numpy as np
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QFileDialog
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class MyMplCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(MyMplCanvas, self).__init__(fig)
        self.setParent(parent)

    def plot(self, data):
        self.data = data
        self.axes.imshow(data, aspect='auto')
        self.draw()

    def clear_plot(self):
        self.axes.cla()  # Clear the canvas.
        self.draw()
    def enter_edit_mode(self):
        self.edit_mode = True
        self.click_points = []  # 清空之前的点击点
        self.mpl_connect('button_press_event', self.on_click)

    def toggle_edit_mode(self):
        # 切换编辑模式
        self.edit_mode = not self.edit_mode
        self.btn_edit_mode.setText("Exit Edit Mode" if self.edit_mode else "Enter Edit Mode")

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
        self.x = x
        self.y = y

        self.axes.plot(x, y, color='red')
        # 填充逻辑（此处需要自己实现根据具体需求）
        # 例如，self.data 是您的二维数据数组
        # 更新 self.data 以将连线下部的数据重新填充为0
        self.draw()
        self.click_points = []  # 重置点击点


class ApplicationWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.data = None
        self.click_points = []
        

        self.setWindowTitle("PyQt6 & Matplotlib Example")

        self.main_widget = QWidget(self)
        self.layout = QVBoxLayout(self.main_widget)

        self.canvas = MyMplCanvas(self.main_widget, width=5, height=4, dpi=100)
        self.layout.addWidget(self.canvas)

        self.button = QPushButton("Import Data and Plot")
        self.button.clicked.connect(self.load_data)
        self.layout.addWidget(self.button)
        
        # 创建按钮
        edit_button = QPushButton('Edit Mode', self)
        edit_button.clicked.connect(self.canvas.enter_edit_mode)
        self.layout.addWidget(edit_button)
        
        self.fill_button = QPushButton("Fill Below Line")
        self.fill_button.clicked.connect(lambda: [self.fill_below_line(), 
                                                  self.canvas.clear_plot(),
                                                  self.canvas.plot(self.data)])
        self.layout.addWidget(self.fill_button)

        self.setCentralWidget(self.main_widget)



    def load_data(self):
        fileName, _ = QFileDialog.getOpenFileName(self, "QFileDialog.getOpenFileName()", "",
                                                  "All Files (*);;Python Files (*.py)")
        if fileName:
            self.data = np.loadtxt(fileName)  # Assuming the data is in a format that can be read by np.loadtxt
            self.canvas.plot(self.data)


    def fill_below_line(self):
        
        x, y = self.canvas.x, self.canvas.y
        x1 = x[0]
        x2 = x[1]
        y1 = y[0]
        y2 = y[1]
        print(x1, x2, y1, y2)
    
        # 遍历x1到x2之间的每个x坐标
        
        for x in range(x1, x2 + 1):
            y = y1 + (y2 - y1) * (x - x1) / (x2 - x1)

            # 将y坐标以下的所有点设置为0
            self.data[x, int(np.ceil(y)):] = 0


if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = ApplicationWindow()
    w.show()
    sys.exit(app.exec())

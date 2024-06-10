import sys
import numpy as np
import pyqtgraph as pg
from PyQt6.QtWidgets import QApplication, QMainWindow

# 创建主窗口类
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # 创建 3D 图形窗口
        # self.graphWidget = pg.opengl.GLViewWidget()
        self.setCentralWidget(self.graphWidget)

        # 设置初始视角
        self.graphWidget.opts['distance'] = 40  # 调整距离
        self.graphWidget.opts['elevation'] = 30  # 仰角
        self.graphWidget.opts['azimuth'] = 45  # 方位角

        # 创建数据点
        x = np.random.standard_normal(100)
        y = np.random.standard_normal(100)
        z = np.random.standard_normal(100)
        colors = np.random.randint(0, 255, size=(100, 4))  # 生成随机颜色
        colors[:, 3] = 255  # 确保点不透明

        # 创建散点图对象
        scatter = pg.opengl.GLScatterPlotItem(pos=np.vstack([x, y, z]).T, size=2, color=pg.glColor((0, 255, 0, 255)), pxMode=False)
        self.graphWidget.addItem(scatter)

# 创建应用实例和窗口
app = QApplication(sys.argv)
window = MainWindow()
window.show()

# 运行应用
sys.exit(app.exec())

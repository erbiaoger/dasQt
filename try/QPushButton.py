import sys
from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        # 创建一个可切换状态的按钮
        self.toggle_button = QPushButton("按下去", self)
        self.toggle_button.setCheckable(True)
        self.toggle_button.clicked.connect(self.on_click)

        # 设置布局
        layout = QVBoxLayout(self)
        layout.addWidget(self.toggle_button)

    def on_click(self):
        if self.toggle_button.isChecked():
            self.toggle_button.setText("按下去")
        else:
            self.toggle_button.setText("按回来")

# 初始化应用和窗口
app = QApplication(sys.argv)
window = MainWindow()
window.show()

# 运行应用
sys.exit(app.exec())

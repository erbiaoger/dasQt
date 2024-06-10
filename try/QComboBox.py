import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QComboBox, QVBoxLayout, QWidget

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("PyQt6 ComboBox Example")
        self.setGeometry(100, 100, 300, 200)

        # 设置中央窗口和布局
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # 创建下拉菜单
        self.combo_box = QComboBox()
        self.combo_box.addItem("Option 1")
        self.combo_box.addItem("Option 2")
        self.combo_box.addItem("Option 3")
        self.combo_box.addItem("Option 4")

        # 添加到布局
        layout.addWidget(self.combo_box)

        # 连接信号
        self.combo_box.activated.connect(self.on_combobox_activated)

    def on_combobox_activated(self, index):
        # 这里的 index 参数是选项的索引
        print(f"Selected: {self.combo_box.itemText(index)}")
        # 在此处执行任何根据选项需要执行的操作

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec())

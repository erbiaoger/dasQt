import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QListWidget, QPushButton, QVBoxLayout, QWidget, QDialog, QLabel, QVBoxLayout

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

        self.setWindowTitle("模块选择示例")

        # 创建两个列表控件
        self.availableModulesList = QListWidget()
        self.selectedModulesList = QListWidget()

        # 添加一些示例模块到可用模块列表
        self.availableModulesList.addItems(["模块1", "模块2", "模块3", "模块4"])

        # 创建添加按钮
        self.addButton = QPushButton("添加到选中")
        self.addButton.clicked.connect(self.addModule)

        # 创建布局并添加控件
        layout = QVBoxLayout()
        layout.addWidget(self.availableModulesList)
        layout.addWidget(self.addButton)
        layout.addWidget(self.selectedModulesList)

        # 设置主窗口的中心部件和布局
        centralWidget = QWidget()
        centralWidget.setLayout(layout)
        self.setCentralWidget(centralWidget)

        # 为选中模块列表添加点击事件
        self.selectedModulesList.itemClicked.connect(self.showOptionWindow)

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

if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec())

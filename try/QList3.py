import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QListWidget, QPushButton, QVBoxLayout, QWidget, QDialog, QLabel, QVBoxLayout

# 为不同模块定义不同的选项窗口类
class OptionWindowA(QDialog):
    def __init__(self, moduleName):
        super().__init__()
        self.setWindowTitle(f"{moduleName} 的选项")
        self.layout = QVBoxLayout()
        self.label = QLabel(f"{moduleName}: 选项 A")
        self.layout.addWidget(self.label)
        self.setLayout(self.layout)

class OptionWindowB(QDialog):
    def __init__(self, moduleName):
        super().__init__()
        self.setWindowTitle(f"{moduleName} 的选项")
        self.layout = QVBoxLayout()
        self.label = QLabel(f"{moduleName}: 选项 B")
        self.layout.addWidget(self.label)
        self.setLayout(self.layout)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("模块选择示例")

        self.availableModulesList = QListWidget()
        self.selectedModulesList = QListWidget()
        self.availableModulesList.addItems(["模块1", "模块2", "模块3", "模块4"])

        self.addButton = QPushButton("添加到选中")
        self.addButton.clicked.connect(self.addModule)

        layout = QVBoxLayout()
        layout.addWidget(self.availableModulesList)
        layout.addWidget(self.addButton)
        layout.addWidget(self.selectedModulesList)

        centralWidget = QWidget()
        centralWidget.setLayout(layout)
        self.setCentralWidget(centralWidget)

        self.selectedModulesList.itemClicked.connect(self.showOptionWindow)

    def addModule(self):
        selectedItem = self.availableModulesList.currentItem()
        if selectedItem:
            self.selectedModulesList.addItem(selectedItem.text())

    def showOptionWindow(self, item):
        moduleName = item.text()
        # 根据模块名称决定弹出哪个选项窗口
        if moduleName == "模块1":
            optionWindow = OptionWindowA(moduleName)
        elif moduleName == "模块2":
            optionWindow = OptionWindowB(moduleName)
        else:
            # 默认选项窗口，或者提示没有为此模块定义选项
            optionWindow = QDialog()
            optionWindow.setWindowTitle("提示")
            layout = QVBoxLayout()
            label = QLabel("此模块没有特定的选项窗口")
            layout.addWidget(label)
            optionWindow.setLayout(layout)

        optionWindow.exec()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec())

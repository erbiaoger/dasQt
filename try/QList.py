import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QListWidget, QPushButton, QVBoxLayout, QWidget, QDialog, QLabel, QVBoxLayout

# 假设的选项窗口类，简化示例
class OptionWindow(QDialog):
    def __init__(self, moduleName):
        super().__init__()
        self.setWindowTitle(f"{moduleName} 的选项")
        self.layout = QVBoxLayout()
        self.label = QLabel(f"{moduleName}: 选项配置")
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

        self.processButton = QPushButton("处理数据")
        self.processButton.clicked.connect(self.processData)

        layout = QVBoxLayout()
        layout.addWidget(self.availableModulesList)
        layout.addWidget(self.addButton)
        layout.addWidget(self.selectedModulesList)
        layout.addWidget(self.processButton)

        centralWidget = QWidget()
        centralWidget.setLayout(layout)
        self.setCentralWidget(centralWidget)

        self.selectedModulesList.itemClicked.connect(self.showOptionWindow)

        # 维护一个列表来记录选中的模块
        self.selectedModules = []

    def addModule(self):
        selectedItem = self.availableModulesList.currentItem()
        if selectedItem and selectedItem.text() not in self.selectedModules:
            self.selectedModulesList.addItem(selectedItem.text())
            # 将选中的模块添加到列表中
            self.selectedModules.append(selectedItem.text())

    def showOptionWindow(self, item):
        optionWindow = OptionWindow(item.text())
        optionWindow.exec()

    def processData(self):
        # 假设的处理数据函数，根据选中的模块列表处理数据
        print("正在处理数据，使用的模块包括：", self.selectedModules)
        # 这里可以添加实际处理数据的代码，根据selectedModules中的模块来处理数据

if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec())

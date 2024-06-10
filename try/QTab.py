import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QTabWidget, QVBoxLayout, QWidget

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.tabWidget = QTabWidget()
        self.tab1 = QWidget()
        self.tab2 = QWidget()

        self.tabWidget.addTab(self.tab1, "Tab 1")
        self.tabWidget.addTab(self.tab2, "Tab 2")

        self.button1 = QPushButton("Switch to Tab 1")
        self.button1.clicked.connect(lambda: self.switchTab(0))
        
        self.button2 = QPushButton("Switch to Tab 2")
        self.button2.clicked.connect(lambda: self.switchTab(1))

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.tabWidget)
        self.layout.addWidget(self.button1)
        self.layout.addWidget(self.button2)

        self.mainWidget = QWidget()
        self.mainWidget.setLayout(self.layout)

        self.setCentralWidget(self.mainWidget)

    def switchTab(self, index):
        self.tabWidget.setCurrentIndex(index)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

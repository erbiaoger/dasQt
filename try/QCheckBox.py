from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QWidget, QCheckBox, QVBoxLayout
import sys

class Example(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.checkBox = QCheckBox('Show Title', self)
        self.checkBox.setChecked(False)
        self.checkBox.stateChanged.connect(self.checkBoxChanged)
        
        layout = QVBoxLayout(self)
        layout.addWidget(self.checkBox)
        
        self.setGeometry(300, 300, 250, 150)
        self.setWindowTitle('QCheckBox Example')
        self.show()
    
    def checkBoxChanged(self, state):
        if state == 0:
            self.setWindowTitle('QCheckBox Example')
            print('Checked')

        else:
            self.setWindowTitle('')
            print('Unchecked')

            

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec())

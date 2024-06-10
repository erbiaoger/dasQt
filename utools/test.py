import sys
from PyQt6.QtWidgets import QApplication, QWidget, QMessageBox, QVBoxLayout, QPushButton

class App(QWidget):
    def __init__(self):
        super().__init__()

        # 设置窗口的标题和大小
        self.setWindowTitle("PyQt6 MessageBox Example")
        self.setGeometry(300, 300, 300, 200)

        # 创建一个按钮，点击时会显示消息框
        self.button = QPushButton("Show MessageBox", self)
        self.button.clicked.connect(self.show_message_box)

        # 创建布局并添加按钮
        layout = QVBoxLayout(self)
        layout.addWidget(self.button)

    def show_message_box(self):
        # 创建并显示消息框
        QMessageBox.warning(self, "Message", "Please input again")

def main():
    app = QApplication(sys.argv)
    ex = App()
    ex.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()

import sys
sys.path.append('./src')
from PyQt5.QtWidgets import QWidget,QApplication, QMainWindow, QFileDialog, QLabel
from control import ImageProcessor
from PyQt5.QtCore import Qt  # Add this line to import the Qt module

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__() 
        self.image_processor = ImageProcessor()  
        self.setCentralWidget(self.image_processor)
        self.setWindowTitle("证件照背景换色")
        self.resize(700, 400)

if __name__ == "__main__":
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)  # 启用高DPI缩放
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)  # 使用高分辨率图标
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


import cv2
import numpy as np
from scipy import stats
from PyQt5.QtWidgets import QWidget,QFileDialog,QMainWindow
from PyQt5.QtGui import QPixmap,QImage
from PyQt5.QtCore import Qt,QUrl
from mainwindow.mainui_ui import Ui_Form

class ImageProcessor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        self.ui.progressBar.setVisible(False)
        self.ui.pushButton_open.clicked.connect(self.open_image)
        self.ui.pushButton_start.clicked.connect(self.change_background)
        self.ui.pushButton_save.clicked.connect(self.save_image)
    def open_image(self):
        self.file_name, _ = QFileDialog.getOpenFileName(self, "Open Image", "", "Image Files (*.png *.jpg *.bmp)")
        if self.file_name:
            self.file_name = QUrl.fromLocalFile(self.file_name).toLocalFile()
            pixmap = QPixmap(self.file_name)
            label_width = self.ui.label_image_src.width()
            label_height = self.ui.label_image_src.height()
            # 缩放图片，保持原始比例
            scaled_pixmap = pixmap.scaled(label_width, label_height, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            # 将缩放后的图片显示在QLabel上
            self.ui.label_image_src.setPixmap(scaled_pixmap)
    
    def change_background(self):
        #对导入的图片扣出背景并根据选择按钮的值将背景替换为白色、红色、蓝色
         # 检查哪个单选按钮被选中，并设置相应的背景颜色
        if self.ui.radioButton_white.isChecked():
            new_color = (255, 255, 255)
        elif self.ui.radioButton_red.isChecked():
            new_color = (0, 0, 255)
        elif self.ui.radioButton_blue.isChecked():
            new_color = (255, 0, 0)
        else:
            # 如果没有选中任何按钮，默认为白色背景
            new_color = (255, 255, 255)
        new_color_bgr = np.uint8([[new_color]])  # 将new_color转换为正确的形状
        new_color_hsv = cv2.cvtColor(new_color_bgr, cv2.COLOR_BGR2HSV)[0][0]
        # 使用OpenCV读取图片，图片在label_image_src中
        img = cv2.imread(self.file_name)
        if img is None:
            return  # 如果图片不存在，直接返回

        # 转换颜色空间到HSV
        self.ui.progressBar.setVisible(True)
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
          # 定义边缘宽度
        edge_width = 10
        # 获取图像边缘的像素
        top_edge = hsv[:edge_width, :, :]
        # 计算边缘区域中最常见的颜色（HSV）
        most_common_hue = stats.mode(top_edge[:, :, 0], axis=None)[0]
        most_common_saturation = stats.mode(top_edge[:, :, 1], axis=None)[0]
        most_common_value = stats.mode(top_edge[:, :, 2], axis=None)[0]
        # 定义背景色的HSV范围
        # 这里我们假设背景色在最常见颜色的基础上有一定的范围波动
        lower_bound = np.array([most_common_hue-10, max(most_common_saturation-40, 0), max(most_common_value-40, 0)])
        upper_bound = np.array([most_common_hue+10, min(most_common_saturation+40, 255), min(most_common_value+40, 255)])
        # 根据阈值将图片二值化
        mask = cv2.inRange(hsv, lower_bound, upper_bound)
        # 使用膨胀操作扩大白色区域
        kernel = np.ones((5, 5), np.uint8)
        mask = cv2.dilate(mask, kernel, iterations=1) 
        # 循环遍历每个像素，将背景替换为新的颜色
        # 这里我们使用HSV颜色空间，因为它更适合处理颜色
        self.ui.progressBar.setValue(10) 
        k = 0
        total_iterations = img.shape[0] * img.shape[1]
        last_progress = 10
        for i in range(img.shape[0]):

            for j in range(img.shape[1]):
                if mask[i, j] == 255:
                    hsv[i, j] = np.array(new_color_hsv) 
                k += 1 
                progress = k * 90 // total_iterations
                if progress >= last_progress + 10:
                    self.ui.progressBar.setValue(progress+10)
                    last_progress = progress

        # 将图片转换回BGR颜色空间
        self.ui.progressBar.setValue(100) 
        result = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
        result_rgb = cv2.cvtColor(result, cv2.COLOR_BGR2RGB)
        height, width, channels = result_rgb.shape
        bytesPerLine = channels * width
        qImg = QImage(result_rgb.data, width, height, bytesPerLine, QImage.Format_RGB888)
        self.pixmap = QPixmap.fromImage(qImg)
        label_width = self.ui.label_image_src.width()
        label_height = self.ui.label_image_src.height()
        # 缩放图片，保持原始比例
        scaled_pixmap = self.pixmap.scaled(label_width, label_height, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        # 将缩放后的图片显示在QLabel上
        self.ui.progressBar.setValue(100)
        self.ui.progressBar.setVisible(False)
        self.ui.label_image_tar.setPixmap(scaled_pixmap)  
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    def save_image(self):
        #取出转换后的图片并保存，弹出保存对话框
        file_name, _ = QFileDialog.getSaveFileName(self, "Save Image", "", "Image Files (*.png *.jpg *.bmp)")
        if file_name:
            self.pixmap.save(file_name)
        



    
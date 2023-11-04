import sys
import os
from PyQt5.QtWidgets import QLineEdit,QMessageBox, QFontDialog, QComboBox, QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QSlider, QColorDialog, QFileDialog
from PyQt5.QtGui import QPixmap, QPainter, QColor, QFont, QPen
from PyQt5.QtCore import Qt
from PyQt5 import QtGui

basedir = os.path.dirname(__file__)

try:
    from ctypes import windll  # Only exists on Windows.
    myappid = 'subreddit.downloader'
    windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except ImportError:
    pass

class WatermarkApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Image Watermarking App")
        self.setGeometry(100, 100, 800, 600)
        self.setWindowState(Qt.WindowMaximized)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QHBoxLayout()
        self.central_widget.setLayout(self.layout)

        # Preview Area
        self.preview_label = QLabel()
        self.layout.addWidget(self.preview_label)

        # Controls Area
        controls_layout = QVBoxLayout()

        controls_layout.addSpacing(20)
        self.select_button = QPushButton("Select Images")
        self.select_button.clicked.connect(self.openFileDialog)
        controls_layout.addWidget(self.select_button)

        controls_layout.addSpacing(20)
        self.img_watermark_button = QPushButton("Select Watermark Image")
        self.img_watermark_button.clicked.connect(self.fileDialogToSelectWatermarkImage)
        controls_layout.addWidget(self.img_watermark_button)
        self.img_watermark_button.setVisible(False)

        self.type_label = QLabel("Watermark Type:")
        controls_layout.addWidget(self.type_label)
        self.type_combo = QComboBox()
        self.type_combo.addItems(["Text Watermark", "Image Watermark"])
        self.type_combo.currentIndexChanged.connect(self.update_controls)
        controls_layout.addWidget(self.type_combo)

        self.watermark_text = "Your Watermark"
        self.watermark_label = QLabel("Watermark Text:")
        controls_layout.addWidget(self.watermark_label)
        self.watermark_input = QLineEdit(self.watermark_text)
        self.watermark_input.textChanged.connect(self.updatePreview)
        controls_layout.addWidget(self.watermark_input)

        controls_layout.addSpacing(20)
        self.select_font_button = QPushButton("Select Font")
        self.select_font_button.clicked.connect(self.selectFont)
        controls_layout.addWidget(self.select_font_button)

        self.size_label = QLabel("Watermark Size:")
        controls_layout.addWidget(self.size_label)
        self.size_slider = QSlider(Qt.Horizontal)
        self.size_slider.valueChanged.connect(self.updatePreview)
        controls_layout.addWidget(self.size_slider)
        self.size_label.setVisible(False)
        self.size_slider.setVisible(False)

        self.color_label = QLabel("Watermark Color:")
        controls_layout.addWidget(self.color_label)
        self.color_button = QPushButton("Select Color")
        self.color_button.clicked.connect(self.selectColor)
        controls_layout.addWidget(self.color_button)

        self.opacity_label = QLabel("Watermark Opacity:")
        controls_layout.addWidget(self.opacity_label)
        self.opacity_slider = QSlider(Qt.Horizontal)
        self.opacity_slider.valueChanged.connect(self.updatePreview)
        controls_layout.addWidget(self.opacity_slider)

        self.angle_label = QLabel("Watermark Angle:")
        controls_layout.addWidget(self.angle_label)
        self.angle_slider = QSlider(Qt.Horizontal)
        self.angle_slider.valueChanged.connect(self.updatePreview)
        controls_layout.addWidget(self.angle_slider)

        self.layout.addLayout(controls_layout)

        self.image_paths = []
        self.selected_image = None
        self.watermark_color = QColor(0, 0, 0)
        self.watermark_font = QFont("Arial", 12)

        self.selected_image = self.selected_image = QPixmap(os.path.join(basedir,'default.png'))
        self.updatePreview()
        self.selected_watermarkimage = QPixmap(os.path.join(basedir,'img_watermark_default.png'))
        
        controls_layout.addSpacing(20)
        self.apply_button = QPushButton("Apply Watermark To All Selected Images")
        self.apply_button.clicked.connect(self.applyWatermarkToImages)
        controls_layout.addWidget(self.apply_button)
        controls_layout.addSpacing(20)        

    def openFileDialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        file_paths, _ = QFileDialog.getOpenFileNames(self, "Select Images", "", "Images (*.png *.jpg *.jpeg *.bmp);;All Files (*)", options=options)
        if file_paths:
            self.image_paths = file_paths
            self.selected_image = QPixmap(file_paths[0])
            self.selected_image = self.selected_image.scaled(800, 800, aspectRatioMode=Qt.KeepAspectRatio)
            self.updatePreview()

    def fileDialogToSelectWatermarkImage(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ExistingFile  # Allow selecting only one existing file
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Image", "", "Images (*.png *.jpg *.jpeg *.bmp);;All Files (*)", options=options)
        if file_path:
            self.selected_watermarkimage = QPixmap(file_path)
            self.updatePreview()

    def selectColor(self):
        color = QColorDialog.getColor(self.watermark_color, self, "Select Color")
        if color.isValid():
            self.watermark_color = color
            self.updatePreview()

    def selectFont(self):
        font, ok = QFontDialog.getFont(self.watermark_font, self, "Select Font")
        
        if ok:
            # The user selected a font
            self.watermark_font = font
            self.updatePreview()

    def updatePreview(self):
        if self.selected_image:
            opacity = self.opacity_slider.value() / 100.0
            angle = self.angle_slider.value()

            self.watermark_image = self.generateWatermarkImage(opacity, angle)
            result_image = self.addWatermarkToImage(self.selected_image, self.watermark_image)

            self.preview_label.setPixmap(result_image)

    def generateWatermarkImage(self, opacity, angle):
        
        if self.type_combo.currentIndex() == 1:
            watermark = self.selected_watermarkimage
            val = self.size_slider.value()
            if val == 0:
                val = 1
            watermark = watermark.scaled(watermark.width()*val, watermark.height()*val)
            painter = QPainter(watermark)
            painter.end()
        else:
            # Create a QPixmap object with a transparent background
            watermark = QPixmap(200, 100)
            watermark.fill(Qt.transparent)
            painter = QPainter(watermark)
            painter.setFont(self.watermark_font)
            painter.setPen(QPen(self.watermark_color))
            painter.setOpacity(opacity)
            painter.rotate(angle)
            painter.drawText(watermark.rect(), Qt.AlignCenter, self.watermark_input.text())
            painter.end()
        
        return watermark

    def addWatermarkToImage(self, image, watermark):
        result = image.copy()
        painter = QPainter(result)

        for i in range(0, result.width(), watermark.width()):
            for j in range(0, result.height(), watermark.height()):
                painter.drawPixmap(i, j, watermark)

        painter.end()

        return result
    
    def applyWatermarkToImages(self):
        if self.image_paths == []:
            QMessageBox.warning(self, "Images?", "No images selected.")
            return

        base_dir = os.path.dirname(self.image_paths[0])
        output_folder_800 = os.path.join(base_dir, '800x800')
        output_folder_1000 = os.path.join(base_dir, '1000x1500')
        
        os.makedirs(output_folder_800, exist_ok=True)
        os.makedirs(output_folder_1000, exist_ok=True)

        for image_path in self.image_paths:
            original_image = QPixmap(image_path)

            # Scale the original image to 800x800 while preserving aspect ratio and adding a white background
            scaled_image_800 = self.scaleImage(original_image, 800, 800)
            scaled_image_800_with_watermark = self.addWatermarkToImage(scaled_image_800, self.watermark_image)

            # Save the watermarked image to the output folder
            base_name = os.path.basename(image_path)
            scaled_image_800_with_watermark.save(os.path.join(output_folder_800, base_name))

            # Scale the original image to 1000x1500 while preserving aspect ratio and adding a white background
            scaled_image_1000 = self.scaleImage(original_image, 1000, 1500)
            scaled_image_1000_with_watermark = self.addWatermarkToImage(scaled_image_1000, self.watermark_image)

            # Save the watermarked image to the output folder
            scaled_image_1000_with_watermark.save(os.path.join(output_folder_1000, base_name))

        # Inform the user that the watermark has been applied and images saved
        QMessageBox.information(self, "Watermark Applied", "Watermark applied to all selected images and saved to the output folder.")
    
    def scaleImage(self, original_pixmap, width, height):
        new_pixmap = QPixmap(width, height)
        new_pixmap.fill(Qt.white)
        
        painter = QPainter(new_pixmap)
        painter.drawPixmap(new_pixmap.rect(), original_pixmap, original_pixmap.rect())
        painter.end()
        
        return new_pixmap.scaled(width, height, aspectRatioMode=Qt.KeepAspectRatio)
    
    def update_controls(self):
        if self.type_combo.currentIndex() == 1:
            self.img_watermark_button.setVisible(True)
            self.watermark_label.setVisible(False)
            self.watermark_input.setVisible(False)
            self.select_font_button.setVisible(False)
            self.color_label.setVisible(False)
            self.color_button.setVisible(False)
            self.size_label.setVisible(True)
            self.size_slider.setVisible(True)
            self.opacity_label.setVisible(False)
            self.opacity_slider.setVisible(False)
            self.angle_label.setVisible(False)
            self.angle_slider.setVisible(False)

        else:
            self.img_watermark_button.setVisible(False)
            self.size_label.setVisible(False)
            self.size_slider.setVisible(False)
            self.watermark_label.setVisible(True)
            self.watermark_input.setVisible(True)
            self.select_font_button.setVisible(True)
            self.color_label.setVisible(True)
            self.color_button.setVisible(True)
            self.opacity_label.setVisible(True)
            self.opacity_slider.setVisible(True)
            self.angle_label.setVisible(True)
            self.angle_slider.setVisible(True)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QtGui.QIcon(os.path.join(basedir, 'icon.ico')))
    window = WatermarkApp()
    window.show()
    sys.exit(app.exec_())

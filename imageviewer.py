from PySide6.QtWidgets import QApplication, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QFileDialog, QWidget, QRubberBand, QFrame, QMenuBar, QInputDialog, QScrollArea, QSizePolicy
from PySide6.QtGui import QImage, QPixmap, QAction, QColor
from PySide6.QtCore import Qt, QRect, QPoint, QSettings
from PySide6.QtGui import qGray

class ImageResizer(QWidget):
    def __init__(self):
        super().__init__()

        self.settings = QSettings("MyApp", "ImageResizer")

        self.main_layout = QHBoxLayout(self)

        self.menu_bar = QMenuBar(self)
        self.main_layout.setMenuBar(self.menu_bar)
        
        self.file_menu = self.menu_bar.addMenu('File')
        self.load_image_action = QAction('Load Image', self)
        self.load_image_action.triggered.connect(self.load_image)
        self.file_menu.addAction(self.load_image_action)

        self.crop_tool_action = QAction('Toggle Crop Tool', self)
        self.crop_tool_action.setCheckable(True)
        self.crop_tool_action.toggled.connect(self.toggle_crop_tool)
        self.file_menu.addAction(self.crop_tool_action)

        self.snip_tool_action = QAction('Snip Image', self)
        self.snip_tool_action.triggered.connect(self.snip_image)
        self.file_menu.addAction(self.snip_tool_action)

        self.bw_tool_action = QAction('Toggle B/W Crop', self)
        self.bw_tool_action.setCheckable(True)
        self.bw_tool_action.toggled.connect(self.toggle_bw_crop)
        self.file_menu.addAction(self.bw_tool_action)

        self.resolution_menu = self.menu_bar.addMenu('Resolution')
        self.change_resolution_action = QAction('Change default resolution', self)
        self.change_resolution_action.triggered.connect(self.change_resolution)
        self.resolution_menu.addAction(self.change_resolution_action)

        self.scroll_area_original = QScrollArea(self)
        self.scroll_area_original.setWidgetResizable(True)

        self.scroll_area_cropped = QScrollArea(self)
        self.scroll_area_cropped.setWidgetResizable(True)

        self.frame_original = QFrame(self.scroll_area_original)
        self.frame_original.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.frame_cropped = QFrame(self.scroll_area_cropped)
        self.frame_cropped.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.image_label_original = QLabel(self.frame_original)
        self.image_label_original.setMouseTracking(True)
        self.image_label_original.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.image_label_cropped = QLabel(self.frame_cropped)
        self.image_label_cropped.setMouseTracking(True)
        self.image_label_cropped.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.scroll_area_original.setWidget(self.frame_original)
        self.scroll_area_cropped.setWidget(self.frame_cropped)

        self.main_layout.addWidget(self.scroll_area_original)
        self.main_layout.addWidget(self.scroll_area_cropped)

        self.origin = None
        self.rubberband = QRubberBand(QRubberBand.Rectangle, self.image_label_original)

        self.default_width = self.settings.value("DefaultWidth", 800, type=int)
        self.default_height = self.settings.value("DefaultHeight", 600, type=int)
        self.image_file = None
        self.loaded_image = None
        self.original_image = None  # This will store the original colored image

        self.crop_info_label = QLabel(self)
        self.crop_info_label.setAlignment(Qt.AlignCenter)
        self.main_layout.addWidget(self.crop_info_label)

    def update_crop_info_label(self, rect):
        width = rect.width() if rect.width() > 0 else 0
        height = rect.height() if rect.height() > 0 else 0
        self.crop_info_label.setText(f"Crop Area: {width}x{height} pixels")

    def change_resolution(self):
        width, ok = QInputDialog.getInt(self, 'Change default width', 'Enter new width:', self.default_width, 1, 5000)
        if ok:
            self.default_width = width
            self.settings.setValue("DefaultWidth", self.default_width)
        height, ok = QInputDialog.getInt(self, 'Change default height', 'Enter new height:', self.default_height, 1, 5000)
        if ok:
            self.default_height = height
            self.settings.setValue("DefaultHeight", self.default_height)

        if self.loaded_image:
            self.load_image()

    def load_image(self):
        image_file, _ = QFileDialog.getOpenFileName(self, 'Open Image File', r"<Default dir>", 'Images (*.png *.xpm *.jpg)')
        if image_file:
            self.image_file = image_file
        
        if self.image_file:
            self.loaded_image = QImage()
            self.loaded_image.load(self.image_file)
            
            # Adjust resolution
            self.resized_image = self.loaded_image.scaled(self.default_width, self.default_height, Qt.KeepAspectRatio)
            self.original_image = self.resized_image.copy()  # Keep a copy of the original colored image
            
            self.image_label_original.setPixmap(QPixmap.fromImage(self.resized_image))
            self.image_label_original.setFixedSize(self.resized_image.size())
            self.frame_original.setFixedSize(self.resized_image.size())

    def toggle_crop_tool(self, checked):
        if not checked:
            self.rubberband.hide()
            self.crop_info_label.clear()
        else:
            self.crop_info_label.setText("Click and drag to select crop area")

    def snip_image(self):
        if self.crop_tool_action.isChecked() and self.loaded_image:
            rect = self.rubberband.geometry()
            self.resized_image = self.resized_image.copy(rect)
            self.original_image = self.resized_image.copy()  # Keep a copy of the snipped colored image

            self.image_label_original.setPixmap(QPixmap.fromImage(self.resized_image))
            self.image_label_original.setFixedSize(self.resized_image.size())
            self.frame_original.setFixedSize(self.resized_image.size())

    def toggle_bw_crop(self, checked):
        if self.crop_tool_action.isChecked() and self.loaded_image:
            rect = self.rubberband.geometry()
            if checked:
                for y in range(rect.top(), rect.bottom()):
                    for x in range(rect.left(), rect.right()):
                        color = QColor(self.resized_image.pixel(x, y))
                        gray = qGray(color.rgb())
                        self.resized_image.setPixel(x, y, QColor(gray, gray, gray).rgb())
            else:
                self.resized_image = self.original_image.copy()  # Restore the original colored image

            self.image_label_original.setPixmap(QPixmap.fromImage(self.resized_image))
            self.image_label_cropped.setPixmap(QPixmap.fromImage(self.resized_image.copy(rect)))

    def mousePressEvent(self, event):
        if self.crop_tool_action.isChecked():
            frame_pos = self.frame_original.mapFrom(self, event.pos())
            self.origin = frame_pos
            self.rubberband.setGeometry(QRect(self.origin, frame_pos))
            self.rubberband.show()

    def mouseMoveEvent(self, event):
        if self.crop_tool_action.isChecked():
            frame_pos = self.frame_original.mapFrom(self, event.pos())
            rect = QRect(self.origin, frame_pos).normalized()
            rect = rect.intersected(self.image_label_original.geometry())
            self.rubberband.setGeometry(rect)
            self.update_crop_info_label(rect)

    def mouseReleaseEvent(self, event):
        if self.crop_tool_action.isChecked():
            rect = self.rubberband.geometry()
            rect = rect.intersected(self.image_label_original.geometry())  # Ensure operations only on the image area
            cropped_image = self.resized_image.copy(rect)
            
            self.image_label_cropped.setPixmap(QPixmap.fromImage(cropped_image))
            self.image_label_cropped.setFixedSize(cropped_image.size())
            self.frame_cropped.setFixedSize(cropped_image.size())

if __name__ == '__main__':
    app = QApplication([])

    window = ImageResizer()
    window.showMaximized()

    app.exec()

from PySide6.QtWidgets import QApplication, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QFileDialog, QWidget, QRubberBand, QFrame, QMenuBar, QInputDialog, QScrollArea, QSizePolicy
from PySide6.QtGui import QImage, QPixmap, QAction
from PySide6.QtCore import Qt, QRect, QPoint, QSettings

class ImageResizer(QWidget):
    def __init__(self):
        super().__init__()

        self.settings = QSettings("MyApp", "ImageResizer")

        self.main_layout = QVBoxLayout(self)

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

        self.resolution_menu = self.menu_bar.addMenu('Resolution')
        self.change_resolution_action = QAction('Change default resolution', self)
        self.change_resolution_action.triggered.connect(self.change_resolution)
        self.resolution_menu.addAction(self.change_resolution_action)

        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)

        self.frame = QFrame(self.scroll_area)
        self.frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.image_label = QLabel(self.frame)
        self.image_label.setMouseTracking(True)
        self.image_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.scroll_area.setWidget(self.frame)

        self.main_layout.addWidget(self.scroll_area)

        self.origin = None
        self.rubberband = QRubberBand(QRubberBand.Rectangle, self.image_label)
        self.child_windows = []  # Store child windows here

        self.default_width = self.settings.value("DefaultWidth", 800, type=int)
        self.default_height = self.settings.value("DefaultHeight", 600, type=int)
        self.image_file = None
        self.loaded_image = None

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
            
            self.image_label.setPixmap(QPixmap.fromImage(self.resized_image))
            self.image_label.setFixedSize(self.resized_image.size())
            self.frame.setFixedSize(self.resized_image.size())

    def toggle_crop_tool(self, checked):
        if not checked:
            self.rubberband.hide()
            self.crop_info_label.clear()
        else:
            self.crop_info_label.setText("Click and drag to select crop area")

    def mousePressEvent(self, event):
        if self.crop_tool_action.isChecked() and self.frame.geometry().contains(event.pos()):
            frame_pos = self.frame.mapFrom(self, event.pos())
            self.origin = frame_pos
            self.rubberband.setGeometry(QRect(self.origin, frame_pos))
            self.rubberband.show()

    def mouseMoveEvent(self, event):
        if self.crop_tool_action.isChecked() and self.frame.geometry().contains(event.pos()):
            frame_pos = self.frame.mapFrom(self, event.pos())
            rect = QRect(self.origin, frame_pos).normalized()
            rect = rect.intersected(self.image_label.geometry())
            self.rubberband.setGeometry(rect)
            self.update_crop_info_label(rect)

    def mouseReleaseEvent(self, event):
        if self.crop_tool_action.isChecked() and self.frame.geometry().contains(event.pos()):
            rect = self.rubberband.geometry()
            cropped_image = self.resized_image.copy(rect)
            cropped_window = ImageWindow(cropped_image)
            self.child_windows.append(cropped_window) 
            cropped_window.show()

class ImageWindow(QWidget):
    def __init__(self, image):
        super().__init__()

        self.image = image

        layout = QVBoxLayout(self)
        scroll_area = QScrollArea(self)
        layout.addWidget(scroll_area)

        frame = QFrame(scroll_area)
        scroll_area.setWidget(frame)

        label = QLabel(frame)
        label.setPixmap(QPixmap.fromImage(image))
        label.setFixedSize(image.size())

        scroll_area.setWidgetResizable(True)

        save_button = QPushButton('Save Image', self)
        save_button.clicked.connect(self.save_image)
        layout.addWidget(save_button)

    def save_image(self):
        image_file, _ = QFileDialog.getSaveFileName(self, 'Save Image File', r"<Default dir>", 'Images (*.png *.xpm *.jpg)')
        if image_file:
            self.image.save(image_file)

if __name__ == '__main__':
    app = QApplication([])

    window = ImageResizer()
    window.showMaximized()

    app.exec()

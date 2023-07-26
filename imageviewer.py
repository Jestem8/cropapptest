from PySide6.QtWidgets import QApplication, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QFileDialog, QWidget, QRubberBand, QFrame, QMenuBar, QInputDialog, QScrollArea, QSlider, QMenu
from PySide6.QtGui import QImage, QPixmap, QAction
from PySide6.QtCore import Qt, QRect

class ImageResizer(QWidget):
    def __init__(self):
        super().__init__()

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

        self.zoom_menu = self.menu_bar.addMenu('Zoom')
        self.toggle_zoom_action = QAction('Toggle Zoom Slider', self)
        self.toggle_zoom_action.setCheckable(True)
        self.toggle_zoom_action.triggered.connect(self.toggle_zoom_slider)
        self.zoom_menu.addAction(self.toggle_zoom_action)

        self.frame = QFrame(self)
        self.main_layout.addWidget(self.frame, alignment=Qt.AlignCenter)

        self.image_label = QLabel(self.frame)
        self.image_label.setMouseTracking(True)

        self.origin = None
        self.rubberband = QRubberBand(QRubberBand.Rectangle, self.image_label)
        self.child_windows = []  # Store child windows here

        self.default_width = 800
        self.default_height = 600
        self.image_file = None
        self.loaded_image = None

        self.zoom_slider = QSlider(Qt.Horizontal)
        self.zoom_slider.setMinimum(10)
        self.zoom_slider.setMaximum(200)
        self.zoom_slider.setSingleStep(5)
        self.zoom_slider.setValue(100)
        self.zoom_slider.valueChanged.connect(self.zoom_image)
        self.zoom_slider.hide()

    def change_resolution(self):
        width, ok = QInputDialog.getInt(self, 'Change default width', 'Enter new width:', self.default_width, 1, 5000)
        if ok:
            self.default_width = width
        height, ok = QInputDialog.getInt(self, 'Change default height', 'Enter new height:', self.default_height, 1, 5000)
        if ok:
            self.default_height = height

        if self.loaded_image:
            self.load_image()

    def load_image(self):
        image_file, _ = QFileDialog.getOpenFileName(self, 'Open Image File', r"<Default dir>", 'Images (*.png *.xpm *.jpg)')
        if image_file:
            self.image_file = image_file

        if self.image_file:
            self.loaded_image = QImage()
            self.loaded_image.load(self.image_file)

            self.resized_image = self.loaded_image.scaled(self.default_width, self.default_height, Qt.KeepAspectRatio)

            self.image_label.setPixmap(QPixmap.fromImage(self.resized_image))
            self.image_label.setFixedSize(self.resized_image.size())
            self.frame.setFixedSize(self.resized_image.size())

            self.zoom_image()  

    def toggle_crop_tool(self, checked):
        if not checked:
            self.rubberband.hide()

    def toggle_zoom_slider(self, checked):
        if checked:
            self.zoom_slider.show()
            self.zoom_image() 
        else:
            self.zoom_slider.hide()

    def zoom_image(self):
        if self.loaded_image and self.toggle_zoom_action.isChecked():
            zoom_factor = self.zoom_slider.value() / 100.0
            zoomed_image = self.resized_image.scaled(self.resized_image.width() * zoom_factor, self.resized_image.height() * zoom_factor, Qt.KeepAspectRatio)
            self.image_label.setPixmap(QPixmap.fromImage(zoomed_image))

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

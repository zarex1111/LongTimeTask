from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5.uic import loadUi
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
import sys
import requests
from io import BytesIO


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        loadUi('main.ui', self)

        self.coords = ("23.346548", "42.685321")
        self.mode = 'map'
        self.scale = "17"

        self.run()
        
    def run(self):
        self.draw_image()


    def keyPressEvent(self, event):

        scale = int(self.scale)

        if event.key() == Qt.Key.Key_PageUp:
            if scale > 1:
                scale -= 1
        elif event.key() == Qt.Key.Key_PageDown:
            if scale < 17:
                scale += 1
        
        self.scale = str(scale)

        self.draw_image()

    
    def draw_image(self):

        map_params = {'ll': ','.join(self.coords),
            'l': self.mode,
            'z': self.scale}
        img = requests.get("http://static-maps.yandex.ru/1.x/", params=map_params).content

        pixmap = QPixmap()
        pixmap.loadFromData(img)
        self.label.setPixmap(pixmap)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    ex.show()
    sys.exit(app.exec())
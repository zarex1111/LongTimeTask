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
        coords = list(map(float, self.coords))
        coeff = 0.0005 * (18 - scale) ** 3

        if event.key() == Qt.Key.Key_PageUp:
            if scale > 1:
                scale -= 1
        elif event.key() == Qt.Key.Key_PageDown:
            if scale < 17:
                scale += 1
        elif event.key() == Qt.Key.Key_Down:
            if coords[1] - 2 * coeff >= -180:
                coords[1] -= coeff
        elif event.key() == Qt.Key.Key_Up:
            if coords[1] + 2 * coeff <= 180:
                coords[1] += coeff
        elif event.key() == Qt.Key.Key_Left:
            if coords[0] - 2 * coeff >= -90:
                coords[0] -= coeff
        elif event.key() == Qt.Key.Key_Right:
            if coords[0] + 2 * coeff <= 90:
                coords[0] += coeff
        
        self.scale = str(scale)
        self.coords = tuple(list(map(str, coords)))

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
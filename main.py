from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5.uic import loadUi
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import Qt
import sys
import requests
from io import BytesIO


MAP_MODES = {'Гибрид': 'sat,skl', 'Спутник': 'sat', 'Карта': 'map'}

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        loadUi('main.ui', self)

        self.coords = ("23.346548", "42.685321")
        self.mode = 'map'
        self.scale = "17"

        self.setup_buttons()
        self.design_buttons()

        self.draw_image()

    def setup_buttons(self):
        self.pushButton.clicked.connect(lambda: self.update_mode('Карта'))
        self.pushButton_2.clicked.connect(lambda: self.update_mode('Спутник'))
        self.pushButton_3.clicked.connect(lambda: self.update_mode('Гибрид'))
        self.pushButton_4.clicked.connect(self.search_adress)

    def design_buttons(self):
        self.pushButton.setIcon(QIcon('img/map.png'))
        self.pushButton_2.setIcon(QIcon('img/sat.jpg'))
        self.pushButton_3.setIcon(QIcon('img/gib.png'))
        self.pushButton_4.setIcon(QIcon('img/search.png'))

    def search_adress(self):
        adress = self.lineEdit.text()
        if adress == '':
            return
        params = self.search_toponym(adress)

        self.coords = params['ll'].split(',')
        
        self.draw_image()
        
    def search_toponym(self, toponym):
        geocoder_api_server = "http://geocode-maps.yandex.ru/1.x/"

        geocoder_params = {
            "apikey": "40d1649f-0493-4b70-98ba-98533de7710b",
            "geocode": toponym,
            "format": "json"}

        response = requests.get(geocoder_api_server, params=geocoder_params).json()
        
        toponym = response["response"]["GeoObjectCollection"][
            "featureMember"][0]["GeoObject"]
        toponym_coodrinates = toponym["Point"]["pos"]
        toponym_longitude, toponym_lattitude = toponym_coodrinates.split(" ")

        map_params = {
            "ll": ",".join([toponym_longitude, toponym_lattitude])
        }
        return map_params

    def run(self):
        self.draw_image()


    def update_mode(self, text):
        self.mode = MAP_MODES[text]
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
        elif event.key() == Qt.Key.Key_S:
            if coords[1] - 2 * coeff >= -180:
                coords[1] -= coeff
        elif event.key() == Qt.Key.Key_W:
            if coords[1] + 2 * coeff <= 180:
                coords[1] += coeff
        elif event.key() == Qt.Key.Key_A:
            if coords[0] - 2 * coeff >= -90:
                coords[0] -= coeff
        elif event.key() == Qt.Key.Key_D:
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
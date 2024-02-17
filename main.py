import requests
import sys
import os
import io
from map_func import get_spn, get_coord, search_toponym, get_address
from map_func import get_postal_code

from PyQt5 import uic
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QMainWindow

template = '''<?xml version="1.0" encoding="UTF-8"?>
<ui version="4.0">
 <class>MainWindow</class>
 <widget class="QMainWindow" name="MainWindow">
  <property name="geometry">
   <rect>
    <x>0</x>
    <y>0</y>
    <width>849</width>
    <height>630</height>
   </rect>
  </property>
  <property name="windowTitle">
   <string>MainWindow</string>
  </property>
  <widget class="QWidget" name="centralwidget">
   <widget class="QComboBox" name="comboBox">
    <property name="geometry">
     <rect>
      <x>70</x>
      <y>10</y>
      <width>151</width>
      <height>22</height>
     </rect>
    </property>
   </widget>
   <widget class="QLabel" name="map">
    <property name="geometry">
     <rect>
      <x>30</x>
      <y>90</y>
      <width>801</width>
      <height>501</height>
     </rect>
    </property>
    <property name="text">
     <string/>
    </property>
   </widget>
   <widget class="QLabel" name="label">
    <property name="geometry">
     <rect>
      <x>10</x>
      <y>10</y>
      <width>111</width>
      <height>20</height>
     </rect>
    </property>
    <property name="text">
     <string>Вид карты</string>
    </property>
   </widget>
   <widget class="QLineEdit" name="lineEdit">
    <property name="geometry">
     <rect>
      <x>230</x>
      <y>10</y>
      <width>491</width>
      <height>20</height>
     </rect>
    </property>
   </widget>
   <widget class="QPushButton" name="pushButton">
    <property name="geometry">
     <rect>
      <x>740</x>
      <y>10</y>
      <width>75</width>
      <height>23</height>
     </rect>
    </property>
    <property name="text">
     <string>Поиск</string>
    </property>
   </widget>
   <widget class="QPushButton" name="clear_push_button">
    <property name="geometry">
     <rect>
      <x>740</x>
      <y>40</y>
      <width>75</width>
      <height>23</height>
     </rect>
    </property>
    <property name="text">
     <string>Сброс</string>
    </property>
   </widget>
   <widget class="QLineEdit" name="lineEdit_2">
    <property name="geometry">
     <rect>
      <x>230</x>
      <y>40</y>
      <width>491</width>
      <height>20</height>
     </rect>
    </property>
    <property name="readOnly">
     <bool>true</bool>
    </property>
   </widget>
   <widget class="QLabel" name="label_2">
    <property name="geometry">
     <rect>
      <x>170</x>
      <y>40</y>
      <width>47</width>
      <height>13</height>
     </rect>
    </property>
    <property name="text">
     <string>Адрес</string>
    </property>
   </widget>
   <widget class="QCheckBox" name="checkBox">
    <property name="geometry">
     <rect>
      <x>70</x>
      <y>40</y>
      <width>70</width>
      <height>17</height>
     </rect>
    </property>
    <property name="text">
     <string>Индекс</string>
    </property>
   </widget>
  </widget>
  <widget class="QMenuBar" name="menubar">
   <property name="geometry">
    <rect>
     <x>0</x>
     <y>0</y>
     <width>849</width>
     <height>21</height>
    </rect>
   </property>
  </widget>
  <widget class="QStatusBar" name="statusbar"/>
 </widget>
 <resources/>
 <connections/>
</ui>
'''


class Example(QMainWindow):
    def __init__(self):
        super().__init__()
        f = io.StringIO(template)
        uic.loadUi(f, self)
        self.lon = 37.530887
        self.lat = 55.703118
        self.dx = 0.002
        self.dy = 0.002
        self.z = 17
        self.view = "map"
        self.point = ""
        self.comboBox.addItem("Карта")
        self.comboBox.addItem("Спутник")
        self.comboBox.addItem("Гибрид")
        self.comboBox.currentTextChanged.connect(self.changeView)
        self.pushButton.clicked.connect(self.searchObject)
        self.checkBox.stateChanged.connect(self.get_postal_code)
        self.clear_push_button.clicked.connect(self.clearObject)
        self.refreshImage()

    def searchObject(self):
        toponym = search_toponym(self.lineEdit.text())
        # print(toponym)
        if toponym:
            self.lon, self.lat = get_coord(toponym)
            self.dx, self.dy = get_spn(toponym)
            self.point = f"{self.lon},{self.lat}"
            address = get_address(toponym)
            if self.checkBox.checkState():
                address += get_postal_code(address)
            self.lineEdit_2.setText(address)
            self.refreshImage()

    def get_postal_code(self):
        toponym = search_toponym(self.lineEdit.text())
        address = get_address(toponym)
        address += get_postal_code(address) if self.checkBox.checkState() else ''
        self.lineEdit_2.setText(address)

    def clearObject(self):
        self.point = ""
        self.lineEdit_2.setText("")
        self.lineEdit.setText('')
        self.refreshImage()

    def keyPressEvent(self, event) -> None:
        # print("!!!!!!!")
        if event.key() == Qt.Key_PageUp:
            if self.z > 0:
                self.z -= 1
                self.dx *= 2
                self.dy *= 2
        elif event.key() == Qt.Key_PageDown:
            if self.z < 21:
                self.z += 1
                self.dx /= 2
                self.dy /= 2
        elif event.key() == Qt.Key_Up:
            if self.lat < 89:
                self.lat += self.dy
        elif event.key() == Qt.Key_Down:
            if self.lat > -89:
                self.lat -= self.dy
        elif event.key() == Qt.Key_Left:
            if self.lon > -179:
                self.lon -= self.dx
        elif event.key() == Qt.Key_Right:
            if self.lon < 179:
                self.lon += self.dx
        self.refreshImage()

    def changeView(self):
        values = {"Карта": "map", "Спутник": "sat", "Гибрид": "sat,skl"}
        text = self.comboBox.currentText()
        self.view = values[text]
        self.refreshImage()

    def refreshImage(self):
        self.getImage()
        self.pixmap = QPixmap(self.map_file)
        self.map.setPixmap(self.pixmap)
        self.setFocus()

    def getImage(self):

        api_server = "http://static-maps.yandex.ru/1.x/"

        params = {
            "ll": ",".join([str(self.lon), str(self.lat)]),
            # "spn": ",".join([self.dx, self.dy]),
            "z": str(self.z),
            "l": self.view
        }

        if self.point:
            params["pt"] = f"{self.point},pm2dgl"

        response = requests.get(api_server, params=params)

        if not response:
            print("Ошибка выполнения запроса:")
            print(response.request.url)
            print("Http статус:", response.status_code, "(", response.reason, ")")
            sys.exit(1)

        # Запишем полученное изображение в файл.
        self.map_file = "map.png"
        with open(self.map_file, "wb") as file:
            file.write(response.content)

    def closeEvent(self, event):
        """При закрытии формы подчищаем за собой"""
        os.remove(self.map_file)


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Example()
    ex.show()
    sys.excepthook = except_hook
    sys.exit(app.exec())

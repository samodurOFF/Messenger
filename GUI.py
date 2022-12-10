import sys
import client, server
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *


class ConnectServer(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(QMainWindow, self).__init__(*args, **kwargs)
        self.initUI()

    def initUI(self):
        # изменение размеров
        self.setFixedSize(320, 130)

        # заголовок окна
        self.setWindowTitle('Подключение к серверу')

        # основные виджеты
        self.ip_label = QLabel('IP адрес')
        self.port_label = QLabel('Порт')

        self.ip_adress = QLineEdit()
        self.ip_adress.setPlaceholderText('Введите ip адрес...')

        self.port = QLineEdit()
        self.port.setPlaceholderText('Введите порт...')

        self.connect = QPushButton('Подключиться')
        self.connect.clicked.connect(self.check_connection)

        self.create_server = QPushButton('Создать локальный сервер')
        self.create_server.clicked.connect(self.run_server)

        # схемы расположения
        left_layout = QVBoxLayout()
        left_layout.addWidget(self.ip_label)
        left_layout.addWidget(self.port_label)

        right_layout = QVBoxLayout()
        right_layout.addWidget(self.ip_adress)
        right_layout.addWidget(self.port)

        top_layout = QHBoxLayout()
        top_layout.addLayout(left_layout)
        top_layout.addLayout(right_layout)

        bottom_layout = QVBoxLayout()
        bottom_layout.addWidget(self.connect)
        bottom_layout.addWidget(self.create_server)

        main_layout = QVBoxLayout()
        main_layout.addLayout(top_layout)
        main_layout.addLayout(bottom_layout)

        container = QWidget()  # виджет контейнера
        container.setLayout(main_layout)  # добавление к контейнеру виджета главной схемы расположения
        self.setCentralWidget(container)  # установка центрального виджета

        self.show()

    def message_window(self, name, message):
        window = QDialog()
        window.setFixedSize(250, 100)
        window.setWindowTitle(name)
        msg = QLabel(message)
        layout = QVBoxLayout()
        layout.addWidget(msg, alignment=Qt.AlignmentFlag.AlignCenter)
        window.setLayout(layout)
        window.setModal(True)
        window.show()
        window.exec()

    def check_connection(self):
        ip = self.ip_adress.text()
        port = self.port.text()
        if client.check_server(ip, int(port)):
            pass
        else:
            self.message_window('ОШИБКА', 'СЕРВЕР НЕДОСТУПЕН')

    def run_server(self):
        pass


class MainWindow(QMainWindow):
    """
    Класс основного окна
    """

    def __init__(self, *args, **kwargs):
        super(QMainWindow, self).__init__(*args, **kwargs)
        self.initUI()

    def initUI(self):
        # заголовок окна
        self.setWindowTitle('MESSENGER')

        # основные виджеты
        self.contact_list = QListWidget(self)
        self.history = QTextEdit()
        self.history.setReadOnly(True)
        self.text_field = QTextEdit()
        self.text_field.setReadOnly(True)
        self.text_field.setPlaceholderText('Введите текст сообщения...')
        self.send_button = QPushButton('Отправить')
        self.send_button.setEnabled(False)

        # схемы расположения
        main_layout = QHBoxLayout()  # основная схема расположения элементов окна
        main_layout.addWidget(self.contact_list)  # добавление списка контактов

        v_layout = QVBoxLayout()  # схема расположения истории сообщений и схемы расположения текстового поля и кнопки.
        v_layout.addWidget(self.history)  # добавление истории сообщений
        v_layout.addWidget(self.text_field)  # добавление текстового поля
        v_layout.addWidget(self.send_button)  # добавление кнопки отправки

        main_layout.addLayout(v_layout)  # добавление к главной схеме расположения

        container = QWidget()  # виджет контейнера
        container.setLayout(main_layout)  # добавление к контейнеру виджета главной схемы расположения
        self.setCentralWidget(container)  # установка центрального виджета

        self.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ConnectServer()
    app.exec()

# Создать окно регистрации пользователей для проводника

import sqlite3
from PyQt6.QtWidgets import *
from hashlib import sha256
from PyQt6.QtCore import Qt


class Auth(QMainWindow):

    def __init__(self):
        super().__init__()
        self.resize(300, 100)

        self.login_label = QLabel('Логин:')
        self.login = QLineEdit()
        self.login.setPlaceholderText('Введите логин...')

        self.password_label = QLabel('Пароль:')
        self.password = QLineEdit()
        self.password.setPlaceholderText('Введите пароль...')
        self.password.setEchoMode(QLineEdit.EchoMode.Password)

        self.button = QPushButton('Войти')
        self.button.clicked.connect(self.enter)

        self.reg_button = QPushButton('Регистрация')
        self.reg_button.clicked.connect(self.add_to_db)

        self.show_password = QCheckBox('Показать пароль')
        self.show_password.toggled.connect(self.reveal)

        layout_1 = QVBoxLayout()
        layout_1.addWidget(self.login_label)
        layout_1.addWidget(self.password_label)

        layout_2 = QVBoxLayout()
        layout_2.addWidget(self.login)
        layout_2.addWidget(self.password)

        layout_3 = QHBoxLayout()
        layout_3.addLayout(layout_1)
        layout_3.addLayout(layout_2)

        layout_4 = QHBoxLayout()
        layout_4.addWidget(self.reg_button)
        layout_4.addWidget(self.show_password, alignment=Qt.AlignmentFlag.AlignRight)

        main_layout = QVBoxLayout()
        main_layout.addLayout(layout_3)
        main_layout.addLayout(layout_4)
        main_layout.addWidget(self.button)

        self.container = QWidget()
        self.container.setLayout(main_layout)
        self.setCentralWidget(self.container)

        self.show()

    def enter(self):
        login = self.login.text()
        password = self.password.text()
        conn = sqlite3.connect('test.db')
        cursor = conn.cursor()
        message = QMessageBox()
        if login and password:
            try:
                cursor.execute('SELECT * FROM USER')
            except Exception as error:
                if str(error) == 'no such table: USER':
                    message.setWindowTitle('ОШИБКА')
                    message.setText('Ни одного пользователя не создано!')
            else:
                data = cursor.fetchall()
                logins = tuple(i[0] for i in data)
                passwords = tuple(i[1] for i in data)
                if login in logins and sha256(password.encode('utf-8')).hexdigest() in passwords:
                    message.setWindowTitle('ВХОД')
                    message.setText('Вы успешно вошли в систему!')
                else:
                    message.setWindowTitle('ОШИБКА')
                    message.setText('Неверный логин или пароль!')
        else:
            message.setWindowTitle('ОШИБКА')
            message.setText('Поля ввода не должны быть пустыми!')

        conn.close()
        message.exec()

    def add_to_db(self):
        login = self.login.text()
        password = self.password.text()
        conn = sqlite3.connect('test.db')
        cursor = conn.cursor()
        message = QMessageBox()
        if login and password:
            cursor.execute(
                '''
                CREATE TABLE IF NOT EXISTS USER(
                 LOGIN NOT NULL UNIQUE,
                 PASSWORD NOT NULL,
                 PRIMARY KEY (LOGIN)
                 )
                 '''
            )

            user = (login, sha256(password.encode('utf-8')).hexdigest())
            try:
                cursor.execute("INSERT INTO USER(LOGIN, PASSWORD) VALUES(?, ?);", user)
            except Exception as error:
                if str(error) == 'UNIQUE constraint failed: USER.LOGIN':
                    message.setWindowTitle('ОШИБКА')
                    message.setText(f'Пользователь {login} уже существует!')
            else:

                conn.commit()
                message.setWindowTitle('РЕГИСТРАЦИЯ')
                message.setText(f'Пользователь {login} успешно добавлен!')
                self.login.clear()
                self.password.clear()
                self.login.setPlaceholderText('Введите логин...')
                self.password.setPlaceholderText('Введите пароль...')

        else:
            message.setWindowTitle('ОШИБКА')
            message.setText('Поля ввода не должны быть пустыми!')

        conn.close()
        message.exec()

    def reveal(self):
        if self.show_password.isChecked():
            self.password.setEchoMode(QLineEdit.EchoMode.Normal)
        else:
            self.password.setEchoMode(QLineEdit.EchoMode.Password)


if __name__ == '__main__':
    app = QApplication([])
    app.setApplicationName("Explorer")
    window = Auth()
    window.setWindowTitle('Authentication')
    app.exec()

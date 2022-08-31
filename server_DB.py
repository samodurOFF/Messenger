from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData, ForeignKey, DateTime
from sqlalchemy.orm import mapper, sessionmaker
from common.variables import *
import datetime


class ServerDB:
    """
    Класс – база данных для сервера
    """

    class AllUsers:
        """
        Отображение таблицы всех пользователей.
        Для связи с таблицей users_table
        """

        def __init__(self, username):
            self.name = username
            self.last_login = datetime.datetime.now()
            self.id = None

    class ActiveUsers:
        """
        Отображение таблицы активных пользователей.
        Для связи с таблицей active_users_table
        """

        def __init__(self, user_id, ip_address, port, login_time):
            self.user = user_id
            self.ip_address = ip_address
            self.port = port
            self.login_time = login_time
            self.id = None

    class LoginHistory:
        """
        Отображение таблицы истории входов.
        Для связи с таблицей user_login_history
        """

        def __init__(self, name, date, ip, port):
            self.id = None
            self.name = name
            self.date_time = date
            self.ip = ip
            self.port = port

    def __init__(self):
        """
        Конструктор класса базы данных
        """

        # движок
        self.database_engine = create_engine(SERVER_DATABASE, echo=False, pool_recycle=7200)

        # объект MetaData
        self.metadata = MetaData()

        # таблица пользователей
        users_table = Table('Users', self.metadata,
                            Column('id', Integer, primary_key=True),
                            Column('name', String, unique=True),
                            Column('last_login', DateTime)
                            )

        # таблица активных пользователей
        active_users_table = Table('Active_users', self.metadata,
                                   Column('id', Integer, primary_key=True),
                                   Column('user', ForeignKey('Users.id'), unique=True),
                                   Column('ip_address', String),
                                   Column('port', Integer),
                                   Column('login_time', DateTime)
                                   )

        # таблица истории входов
        user_login_history = Table('Login_history', self.metadata,
                                   Column('id', Integer, primary_key=True),
                                   Column('name', ForeignKey('Users.id')),
                                   Column('date_time', DateTime),
                                   Column('ip', String),
                                   Column('port', String)
                                   )

        # создание всех таблиц
        self.metadata.create_all(self.database_engine)

        # ORM связь классов отображения с соответствующими таблицами
        mapper(self.AllUsers, users_table)
        mapper(self.ActiveUsers, active_users_table)
        mapper(self.LoginHistory, user_login_history)

        # Сессия
        Session = sessionmaker(bind=self.database_engine)
        self.session = Session()

        # очистка таблицы активных пользователей при создании новой сессии
        self.session.query(self.ActiveUsers).delete()
        self.session.commit()

    def user_login(self, username, ip_address, port):
        """
        Метод записи данных пользователя при входе на сервер
        """

        # поиск имени пользователя в таблице всех пользователей
        rez = self.session.query(self.AllUsers).filter_by(name=username)

        if rez.count():  # если пользователь уже существует, то
            user = rez.first()
            user.last_login = datetime.datetime.now()  # обновляем время входа
        else:  # если пользователь новый, то
            user = self.AllUsers(username)  # создаем пользователя
            self.session.add(user)  # и добавляем в таблицу
            self.session.commit()  # сохранение изменений

        # создание активного пользователя
        new_active_user = self.ActiveUsers(user.id, ip_address, port, datetime.datetime.now())
        self.session.add(new_active_user)  # добавление в таблицу активных пользователей

        history = self.LoginHistory(user.id, datetime.datetime.now(), ip_address, port)  # история входов
        self.session.add(history)  # добавление в таблицу истории входов

        self.session.commit()  # сохранение изменений

    # Функция фиксирующая отключение пользователя
    def user_logout(self, username):
        """
        Метод регистрации отключённого пользователя
        """

        user = self.session.query(self.AllUsers).filter_by(name=username).first()  # нужный пользователь

        self.session.query(self.ActiveUsers).filter_by(user=user.id).delete()  # удаление из таблицы активных

        self.session.commit()  # сохранение изменений



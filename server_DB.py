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
            self.id = None
            self.name = username
            self.last_login = datetime.datetime.now()

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

    class UsersContacts:
        """
        Отображение списка контактов пользователей.
        Для связи с таблицей contacts
        """

        def __init__(self, user, contact):
            self.id = None
            self.user = user
            self.contact = contact

    class UsersHistory:
        """
        Отображение истории действий.
        Для связи с таблицей users_history_table
        """

        def __init__(self, user):
            self.id = None
            self.user = user
            self.sent = 0
            self.accepted = 0

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

        # таблица контактов пользователей
        contacts = Table('Contacts', self.metadata,
                         Column('id', Integer, primary_key=True),
                         Column('user', ForeignKey('Users.id')),
                         Column('contact', ForeignKey('Users.id'))
                         )

        # таблица истории действий пользователей
        users_history_table = Table('History', self.metadata,
                                    Column('id', Integer, primary_key=True),
                                    Column('user', ForeignKey('Users.id')),
                                    Column('sent', Integer),
                                    Column('accepted', Integer),
                                    )

        # создание всех таблиц
        self.metadata.create_all(self.database_engine)

        # ORM связь классов отображения с соответствующими таблицами
        mapper(self.AllUsers, users_table)
        mapper(self.ActiveUsers, active_users_table)
        mapper(self.LoginHistory, user_login_history)
        mapper(self.UsersContacts, contacts)
        mapper(self.UsersHistory, users_history_table)

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

    def user_logout(self, username):
        """
        Метод регистрации отключённого пользователя
        """

        user = self.session.query(self.AllUsers).filter_by(name=username).first()  # нужный пользователь

        self.session.query(self.ActiveUsers).filter_by(user=user.id).delete()  # удаление из таблицы активных

        self.session.commit()  # сохранение изменений

    def process_message(self, sender, recipient):
        """
        Метод регистрации сообщения
        """

        sender = self.session.query(self.AllUsers).filter_by(name=sender).first().id
        recipient = self.session.query(self.AllUsers).filter_by(name=recipient).first().id
        # Запрашиваем строки из истории и увеличиваем счётчики
        sender_row = self.session.query(self.UsersHistory).filter_by(user=sender).first()
        sender_row.sent += 1
        recipient_row = self.session.query(self.UsersHistory).filter_by(user=recipient).first()
        recipient_row.accepted += 1

        self.session.commit()  # add_new

    def add_contact(self, user, contact):
        """
        Метод добавления контакта в список контактов пользователя
        """

        user = self.session.query(self.AllUsers).filter_by(name=user).first()  # пользователь
        contact = self.session.query(self.AllUsers).filter_by(name=contact).first()  # пользователя-контакт

        already_exist = self.session.query(self.UsersContacts).filter_by(user=user.id, contact=contact.id)
        print(bool(already_exist))

        if user and contact and not already_exist:  # если пользователь и контакт существуют,
            # и контакта пользователя еще не существует в списке его контактов, то
            contact_row = self.UsersContacts(user.id, contact.id)  # создается запись для таблицы контактов
            self.session.add(contact_row)  # добавляется запись в таблицу контактов
            self.session.commit()  # сохраняется

    def remove_contact(self, user, contact):
        """
        Метод удаление контакта из списка контактов пользователя
        """

        # контакт, который нужно удалить
        contact = self.session.query(self.UsersContacts).filter_by(user=user, contact=contact).first()

        # пользователь, из списка контактов которого нужно удалить контакт
        user = self.session.query(self.AllUsers).filter_by(name=user).first()

        if user and contact:  # если пользователь существует и в списках его контактов присутствует удаляемый контакт, то
            # удаляем контакт
            self.session.query(self.UsersContacts).filter(
                self.UsersContacts.user == user.id,
                self.UsersContacts.contact == contact.id
            ).delete()
            self.session.commit()  # add_new

    def users_list(self):
        """
        Метод возврата известных пользователей со временем последнего входа.
        """

        query = self.session.query(
            self.AllUsers.name,
            self.AllUsers.last_login
        )

        return query.all()

    def active_users_list(self):
        """
        Метод возврата списка активных пользователей
        """

        query = self.session.query(
            self.AllUsers.name,
            self.ActiveUsers.ip_address,
            self.ActiveUsers.port,
            self.ActiveUsers.login_time
        ).join(self.AllUsers)

        return query.all()

    def login_history(self, username=None):
        """
        Метод возврата истории входов по пользователю или всем пользователям
        """

        query = self.session.query(self.AllUsers.name,
                                   self.LoginHistory.date_time,
                                   self.LoginHistory.ip,
                                   self.LoginHistory.port
                                   ).join(self.AllUsers)

        if username:
            query = query.filter(self.AllUsers.name == username)

        return query.all()

    def get_contacts(self, username):
        """
        Метод получения контактов конкретного пользователя
        """

        user = self.session.query(self.AllUsers).filter_by(name=username).one()  # пользователь

        query = self.session.query(self.UsersContacts, self.AllUsers.name). \
            filter_by(user=user.id). \
            join(self.AllUsers, self.UsersContacts.contact == self.AllUsers.id)

        # выбираем только имена пользователей и возвращаем их.
        return [contact[1] for contact in query.all()]

    def message_history(self):
        """
        Метод возврата количества переданных и полученных сообщений
        """

        query = self.session.query(
            self.AllUsers.name,
            self.AllUsers.last_login,
            self.UsersHistory.sent,
            self.UsersHistory.accepted
        ).join(self.AllUsers)

        return query.all()

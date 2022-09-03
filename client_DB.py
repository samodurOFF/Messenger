import os

from sqlalchemy import create_engine, Table, Column, Integer, String, Text, MetaData, DateTime
from sqlalchemy.orm import mapper, sessionmaker
from common.variables import *
import datetime


class ClientDB:
    """
    Класс – база данных для клиента
    """

    class KnownUsers:
        """
        Отображение известных пользователей
        Для связи с таблицей users
        """

        def __init__(self, user):
            self.id = None
            self.username = user

    class MessageHistory:
        """
        Отображение истории сообщений.
        Для связи с таблицей history
        """

        def __init__(self, from_user, to_user, message):
            self.id = None
            self.from_user = from_user
            self.to_user = to_user
            self.message = message
            self.date = datetime.datetime.now()

    class Contacts:
        """
        Отображение списка контактов.
        Для связи с таблицей contacts
        """

        def __init__(self, contact):
            self.id = None
            self.name = contact

    def __init__(self, name):
        DB_dir = 'client_DB'
        if not os.path.exists(DB_dir):
            os.mkdir(DB_dir)

        self.database_engine = create_engine(
            f'sqlite:///{DB_dir}/client_{name}_db.db3',
            echo=False,
            pool_recycle=7200,
            connect_args={
                'check_same_thread': False
            },
        )

        # объект MetaData
        self.metadata = MetaData()

        # таблица известных пользователей
        users = Table('known_users', self.metadata,
                      Column('id', Integer, primary_key=True),
                      Column('username', String)
                      )

        # таблица истории сообщений
        history = Table('message_history', self.metadata,
                        Column('id', Integer, primary_key=True),
                        Column('from_user', String),
                        Column('to_user', String),
                        Column('message', Text),
                        Column('date', DateTime)
                        )

        # таблица контактов
        contacts = Table('contacts', self.metadata,
                         Column('id', Integer, primary_key=True),
                         Column('name', String, unique=True)
                         )

        # создание всех таблиц
        self.metadata.create_all(self.database_engine)

        # ORM связь классов отображения с соответствующими таблицами
        mapper(self.KnownUsers, users)
        mapper(self.MessageHistory, history)
        mapper(self.Contacts, contacts)

        # Сессия
        Session = sessionmaker(bind=self.database_engine)
        self.session = Session()

        # очистка таблицы контактов при создании новой сессии
        self.session.query(self.Contacts).delete()
        self.session.commit()

    def add_contact(self, contact):
        """
        Метод добавления контактов
        """

        if not self.session.query(self.Contacts).filter_by(name=contact).count():
            contact_row = self.Contacts(contact)
            self.session.add(contact_row)
            self.session.commit()

    def del_contact(self, contact):
        """
        Метод удаления контактов
        """

        self.session.query(self.Contacts).filter_by(name=contact).delete()

    def add_users(self, users_list):
        """
        Метод добавления известных пользователей.
        """

        self.session.query(self.KnownUsers).delete()
        for user in users_list:
            user_row = self.KnownUsers(user)
            self.session.add(user_row)
        self.session.commit()

    def save_message(self, from_user, to_user, message):
        """
        Метод сохранения сообщений
        """

        message_row = self.MessageHistory(from_user, to_user, message)
        self.session.add(message_row)
        self.session.commit()

    def get_contacts(self):
        """
        Метод получения списка контактов
        """

        return [contact[0] for contact in self.session.query(self.Contacts.name).all()]

    def get_users(self):
        """
        Метод получения списка известных пользователей
        """

        return [user[0] for user in self.session.query(self.KnownUsers.username).all()]

    def check_user(self, user):
        """
        Метод, проверяющий, что пользователь является известным
        """

        if self.session.query(self.KnownUsers).filter_by(username=user).count():
            return True
        else:
            return False

    def check_contact(self, contact):
        """
        Метод, проверяющий, что пользователь является контактом
        """

        if self.session.query(self.Contacts).filter_by(name=contact).count():
            return True
        else:
            return False

    def get_history(self, from_who=None, to_who=None):
        """
        Метод, возвращающий историю переписки
        """

        query = self.session.query(self.MessageHistory)
        if from_who:
            query = query.filter_by(from_user=from_who)
        if to_who:
            query = query.filter_by(to_user=to_who)
        return [(history_row.from_user, history_row.to_user, history_row.message, history_row.date)
                for history_row in query.all()]

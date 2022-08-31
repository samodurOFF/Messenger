import sys
from argparse import ArgumentParser
from json import JSONDecodeError
from logging import getLogger
from socket import socket, SOCK_STREAM, AF_INET
from threading import Thread
from time import time, sleep

from common.variables import *
from common.utils import *
from errors import IncorrectDataReceivedError, ReqFieldMissingError, ServerError
from decos import log
from metaclasses import ClientVerifier

# Инициализация клиентского логера
logger = getLogger('client')


class Client(Thread):
    def __init__(self, account_name, sock):
        """
        Основной класс формирования и отправки сообщений на сервер и взаимодействия с пользователем.
        """
        self.account_name = account_name
        self.sock = sock
        super().__init__()


class ClientSender(Client, metaclass=ClientVerifier):

    def create_exit_message(self):
        """
        Метод создаёт словарь с сообщением о выходе.
        """
        return {
            ACTION: EXIT,
            TIME: time(),
            ACCOUNT_NAME: self.account_name
        }

    #
    def create_message(self):
        """
        Метод запрашивает кому отправить сообщение и само сообщение, и отправляет полученные данные на сервер.
        """
        to = input('Введите получателя сообщения: ')
        message = input('Введите сообщение для отправки: ')
        message_dict = {
            ACTION: MESSAGE,
            SENDER: self.account_name,
            DESTINATION: to,
            TIME: time(),
            MESSAGE_TEXT: message
        }
        logger.debug(f'Сформирован словарь сообщения: {message_dict}')
        try:
            self.sock.send(encode_message(message_dict))
            logger.info(f'Отправлено сообщение для пользователя {to}')
        except:
            logger.critical('Потеряно соединение с сервером.')
            exit(1)

    def run(self):
        """
        Метод взаимодействия с пользователем, запрашивает команды, отправляет сообщения
        """
        self.print_help()
        while True:
            command = input('Введите команду: ')
            if command == 'message':
                self.create_message()
            elif command == 'help':
                self.print_help()
            elif command == 'exit':
                try:
                    self.sock.send(encode_message(self.create_exit_message()))
                except:
                    pass
                print('Завершение соединения.')
                logger.info('Завершение работы по команде пользователя.')
                # Задержка неоходима, чтобы успело уйти сообщение о выходе
                sleep(0.5)
                break
            else:
                print('Команда не распознана, попробойте снова. help - вывести поддерживаемые команды.')

    # Функция выводящая справку по использованию.
    def print_help(self):
        """
        Метод выводящий справку по использованию.
        """

        print('Поддерживаемые команды:')
        print('message - отправить сообщение. Кому и текст будет запрошены отдельно.')
        print('help - вывести подсказки по командам')
        print('exit - выход из программы')


class ClientReader(Client, metaclass=ClientVerifier):

    def run(self):
        """
        Основной цикл приёмника сообщений.
        Принимает сообщения, выводит в консоль. Завершается при потере соединения.
        """
        while True:
            try:
                message = decode_message(self.sock.recv(MAX_PACKAGE_LENGTH))
                if ACTION in message and message[ACTION] == MESSAGE and SENDER in message and DESTINATION in message \
                        and MESSAGE_TEXT in message and message[DESTINATION] == self.account_name:
                    print(f'\nПолучено сообщение от пользователя {message[SENDER]}:\n{message[MESSAGE_TEXT]}')
                    logger.info(f'Получено сообщение от пользователя {message[SENDER]}:\n{message[MESSAGE_TEXT]}')
                else:
                    logger.error(f'Получено некорректное сообщение с сервера: {message}')
            except IncorrectDataReceivedError:
                logger.error(f'Не удалось декодировать полученное сообщение.')
            except (OSError, ConnectionError, ConnectionAbortedError, ConnectionResetError, JSONDecodeError):
                logger.critical(f'Потеряно соединение с сервером.')
                break


@log
def create_presence(account_name):
    """
    Функция генерации запроса о присутствии клиента
    """
    out = {
        ACTION: PRESENCE,
        TIME: time(),
        USER: {
            ACCOUNT_NAME: account_name
        }
    }
    logger.debug(f'Сформировано {PRESENCE} сообщение для пользователя {account_name}')
    return out


@log
def process_response_ans(message):
    """
    Функция разбирает ответ сервера на сообщение о присутствии.
    Возвращает 200 если все ОК или генерирует исключение при ошибке.
    """
    logger.debug(f'Разбор приветственного сообщения от сервера: {message}')
    if RESPONSE in message:
        if message[RESPONSE] == 200:
            return '200 : OK'
        elif message[RESPONSE] == 400:
            raise ServerError(f'400 : {message[ERROR]}')
    raise ReqFieldMissingError(RESPONSE)


@log
def arg_parser():
    """
    Парсер аргументов командной строки
    """
    parser = ArgumentParser()
    parser.add_argument('addr', default=DEFAULT_IP_ADDRESS, nargs='?')
    parser.add_argument('port', default=DEFAULT_PORT, type=int, nargs='?')
    parser.add_argument('-n', '--name', default=None, nargs='?')
    namespace = parser.parse_args(sys.argv[1:])
    server_address = namespace.addr
    server_port = namespace.port
    client_name = namespace.name

    # проверим подходящий номер порта
    if not 1023 < server_port < 65536:
        logger.critical(
            f'Попытка запуска клиента с неподходящим номером порта: {server_port}. Допустимы адреса с 1024 до 65535. Клиент завершается.')
        exit(1)

    return server_address, server_port, client_name


def main():
    # Сообщаем о запуске
    print('Консольный месседжер. Клиентский модуль.')

    # Загружаем параметры командной строки
    server_address, server_port, client_name = arg_parser()

    # Если имя пользователя не было задано, необходимо запросить пользователя.
    if not client_name:
        client_name = input('Введите имя пользователя: ')
    else:
        print(f'Клиентский модуль запущен с именем: {client_name}')

    logger.info(
        f'Запущен клиент с парамертами: адрес сервера: {server_address} , порт: {server_port}, имя пользователя: {client_name}')

    # Инициализация сокета и сообщение серверу о нашем появлении
    try:
        transport = socket(AF_INET, SOCK_STREAM)
        transport.connect((server_address, server_port))
        transport.send(encode_message(create_presence(client_name)))
        answer = process_response_ans(decode_message(transport.recv(MAX_PACKAGE_LENGTH)))
        logger.info(f'Установлено соединение с сервером. Ответ сервера: {answer}')
        print(f'Установлено соединение с сервером.')
    except JSONDecodeError:
        logger.error('Не удалось декодировать полученную Json строку.')
        exit(1)
    except ServerError as error:
        logger.error(f'При установке соединения сервер вернул ошибку: {error.text}')
        exit(1)
    except ReqFieldMissingError as missing_error:
        logger.error(f'В ответе сервера отсутствует необходимое поле {missing_error.missing_field}')
        exit(1)
    except (ConnectionRefusedError, ConnectionError):
        logger.critical(
            f'Не удалось подключиться к серверу {server_address}:{server_port}, конечный компьютер отверг запрос на подключение.')
        exit(1)
    else:
        # Если соединение с сервером установлено корректно, запускаем клиентский процесс приёма сообщений.
        module_receiver = ClientReader(client_name, transport)
        module_receiver.daemon = True
        module_receiver.start()

        # затем запускаем отправку сообщений и взаимодействие с пользователем.
        module_sender = ClientSender(client_name, transport)
        module_sender.daemon = True
        module_sender.start()
        logger.debug('Запущены процессы')

        # Основной цикл.
        # Если один из потоков завершён, то это значит, что, либо потеряно соединение, либо пользователь
        # ввёл exit. Поскольку все события обрабатываются в потоках, достаточно просто завершить цикл.
        while True:
            sleep(1)
            if module_receiver.is_alive() and module_sender.is_alive():
                continue
            break


if __name__ == '__main__':
    main()

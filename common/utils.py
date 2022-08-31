from sys import path
from json import dumps, loads
from common.variables import MAX_PACKAGE_LENGTH, ENCODING
from errors import IncorrectDataReceivedError, NonDictInputError
from decos import log

path.append('../')


@log
def decode_message(encoded_response):
    """
    Функция декодирования сообщения от клиента.
    Возвращает словарь или бросает исключение, если сообщение не в байтах или если ответ не словарь.
    """
    if isinstance(encoded_response, bytes):
        json_response = encoded_response.decode(ENCODING)
        response = loads(json_response)
        if isinstance(response, dict):
            return response
        else:
            raise IncorrectDataReceivedError
    else:
        raise IncorrectDataReceivedError


@log
def encode_message(message):
    """
    Функция кодирования сообщения.
    Если сообщение не словарь – бросает исключение.
    """
    if not isinstance(message, dict):
        raise NonDictInputError
    js_message = dumps(message)
    encoded_message = js_message.encode(ENCODING)
    return encoded_message
